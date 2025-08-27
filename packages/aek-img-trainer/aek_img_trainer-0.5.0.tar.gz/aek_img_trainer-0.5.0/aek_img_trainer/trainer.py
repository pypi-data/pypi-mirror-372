import os
import cv2
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torch.optim.lr_scheduler import StepLR, ReduceLROnPlateau
import numpy as np
import time
import timm
import random
import openvino as ov
from openvino.runtime import Core


class Preprocessor:
    """
    Handles image augmentation and preprocessing steps including resizing,
    normalization, and conversion to tensor format compatible with PyTorch.
    """

    def __init__(self, img_size=224, augment=False):
        """
        Initialize the Preprocessor.

        Args:
            img_size (int): Target size for image resizing (width and height).
            augment (bool): Whether to apply augmentation in transforms.
        """
        self.img_size = img_size
        self.augment = augment
    
    def random_brightness_contrast(self, img, brightness=0.2, contrast=0.2):
        """
        Apply random brightness and contrast adjustment to the image.

        Args:
            img (np.ndarray): Input image.
            brightness (float): Maximum brightness shift as a fraction.
            contrast (float): Maximum contrast scale factor.
        
        Return:
            np.ndarray: Augmented image.
        """
        beta = random.uniform(-brightness*255, brightness*255)
        alpha = random.uniform(1-contrast, 1+contrast)
        img = img.astype(np.float32) * alpha + beta
        img = np.clip(img, 0, 255).astype(np.uint8)
        return img
    
    def random_rotation(self, img, degrees=15):
        """
        Rotate the image randomly within the specified degree range.

        Args:
            img (np.ndarray): Input image.
            degrees (float): Maximum rotation angle in degrees.
        
        Returns:
            np.ndarray: Rotated image.
        """
        h, w = img.shape[:2]
        angle = random.uniform(-degrees, degrees)
        M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
        img = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        return img
    
    def random_affine(self, img, translate=0.1, scale_range=(0.8, 1.2), shear=5):
        """
        Apply random affine transformation including translation, scaling, and shearing.

        Args:
            img (np.ndarray): Input image.
            translate (float): Max translation as a fraction of image dimension.
            scale_range (tuple): Min and max scale factors.
            shear (float): Max shear angle in degrees.
        
        Returns:
            np.ndarray: Affine transformed image.
        """

        h, w = img.shape[:2]
        max_tx = translate * w
        max_ty= translate * h
        tx = random.uniform(-max_tx, max_tx)
        ty = random.uniform(-max_ty, max_ty)
        scale = random.uniform(scale_range[0], scale_range[1])
        shear_angle = random.uniform(-shear, shear)
        shear_rad = np.deg2rad(shear_angle)
        M = np.array([
            [scale, np.tan(shear_rad), tx],
            [0, scale, ty]
        ], dtype=np.float32)
        img = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        return img
    
    def random_flip(self, img, p_horizontal=0.5, p_vertical=0.1):
        """
        Randomly flip the image horizontally and/or vertically.

        Args:
            img (np.ndarray): Input image.
            p_horizontal (float): Probability of horizontal flip.
            p_vertical (float): Probability of vertical flip.

        Return:
            np.ndarray: Flipped image.
        """
        if random.random() < p_horizontal:
            img = cv2.flip(img, 1)
        if random.random() < p_vertical:
            img = cv2.flip(img, 0)
        return img
    
    def random_perspective(self, img, distortion_scale=0.1, p=0.3):
        """
        Apply random perspective distortion with given probability.

        Args:
            img (np.ndarray): Input image.
            distortion_scale (float): Max distortion as a fraction of image size.
            p (float): Probability to apply perspective transform.

        Returns:
            np.ndarray: Perspective transformed image or original image.
        """
        if random.random() > p:
            return img
        h, w = img.shape[:2]
        pts1 = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        max_dx = distortion_scale * w
        max_dy = distortion_scale * h
        pts2 = pts1 + np.float32([
            [random.uniform(-max_dx, max_dx), random.uniform(-max_dy, max_dy)],
            [random.uniform(-max_dx, max_dx), random.uniform(-max_dy, max_dy)],
            [random.uniform(-max_dx, max_dx), random.uniform(-max_dy, max_dy)],
            [random.uniform(-max_dx, max_dx), random.uniform(-max_dy, max_dy)],
        ])
        M = cv2.getPerspectiveTransform(pts1, pts2)
        img = cv2.warpPerspective(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        return img
    
    def apply_augmentations(self, img):
        """
        Apply all augmentation transforms sequentially.

        Args:
            img (np.ndarray): Input image.

        Return:
            np.ndarray: Augmented image.
        """
        img = self.random_brightness_contrast(img)
        img = self.random_rotation(img)
        img = self.random_affine(img)
        img = self.random_flip(img)
        img = self.random_perspective(img)
        return img
    
    def preprocess_image(self, img):
        """
        Preprocess the image: optionally augment, resize, normalize, convert to tensor.

        Args:
            img (np.ndarray): Input image.

        Returns:
            np.ndarray: Preprocessed image blob with shape (3, img_size, img_size).

        """
        if self.augment:
            img = self.apply_augmentations(img)
        blob = cv2.dnn.blobFromImage(
            image=img,
            scalefactor=2.0/255.0,
            size=(self.img_size, self.img_size),
            mean=(1.0, 1.0, 1.0),
            swapRB=True,
            crop=False
        )
        return blob

class ImageFolderOpenCV(Dataset):
    """
    Custom PyTorch Dataset to load images using OpenCV with preprocessing support.
    Assumes directory structure with subfolders per class.
    """
    
    def __init__(self, root_dir, preprocessor: Preprocessor):
        """
        Args:
            root_dir (str): Path to dataset root directory.
            preprocessor (Preprocessor): Instance of Preprocessor for augmentation & preprocessing.
        """
        self.root_dir = root_dir
        self.preprocessor = preprocessor
        self.samples = []
        self.class_to_idx = {}

        for idx, class_name in enumerate(sorted(os.listdir(root_dir))):
            class_path = os.path.join(root_dir, class_name)
            if not os.path.isdir(class_path):
                continue
            self.class_to_idx[class_name] = idx
            for fnmae in os.listdir(class_path):
                if fnmae.lower().endswith((".jpg", ".jpeg", ".png")):
                    self.samples.append((os.path.join(class_path, fnmae), idx))
    
    def __len__(self):
        """
        Returns:
            int: Number of samples in the dataset.
        """
        return len(self.samples)
    
    def __getitem__(self, idx):
        """
        Get a sample image tensor and its label.

        Args:
            idx (int): Index of sample.

        Returns:
            tuple: (image_tensor (torch.FloatTensor), label (int))
        """
        img_path, label = self.samples[idx]
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        img = self.preprocessor.preprocess_image(img).squeeze(0)
        return torch.tensor(img).float(), label
    
class Trainer:
    """
    Trainer class encapsulates model creation, training and validation loops,
    checkpoint saving and early stopping based on validation accuracy.
    """

    def __init__(self,
                 train_root,
                 val_root,
                 num_classes=16,
                 img_size=224,
                 batch_size=4,
                 val_reach=0.9999,
                 num_epochs=150,
                 learning_rate=1e-3,
                 checkpoint_path="efficientnet_b0_best_model.pth",
                 model_name = "efficientnet_b0",
                 device=None,
                 augment=True,
                 scheduler=None,
                 scheduler_params=None,
                 pretrained=True):
        """
        Initialize Trainer with datasets, model, loss, optimizer, and loaders.

        Args:
            train_root (str): Path to training dataset root directory.
            val_root (str): Path to validation dataset root directory.
            num_classes (int): Number of target classes.
            img_size (int): Image size (width and height) for resizing.
            batch_size (int): Batch size for traning and validation.
            num_epochs (int): Number of epochs to train.
            learning_rate (float): Learning rate for optimizer.
            checkpoint_path (str): File path to save the best model weights.
            model_name (str): Model name to create with timm
            device (torch.device or None): Device to train on, defaults to CUDA if available.
            augment (bool): Whether to apply augmentations on training data.
        """

        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.num_classes = num_classes
        self.img_size = img_size
        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.learning_rate = learning_rate
        self.checkpoint_path = checkpoint_path
        self.model_name = model_name
        self.pretrained = pretrained
        self.val_reach = val_reach

        self.train_preproc = Preprocessor(img_size=img_size, augment=augment)
        self.val_preproc = Preprocessor(img_size=img_size, augment=False)

        self.train_dataset = ImageFolderOpenCV(train_root, self.train_preproc)
        self.val_dataset = ImageFolderOpenCV(val_root, self.val_preproc)

        self.train_loader = DataLoader(self.train_dataset, batch_size=batch_size, shuffle=True)
        self.val_loader = DataLoader(self.val_dataset, batch_size=batch_size, shuffle=False)

        self.model = timm.create_model(model_name, pretrained=self.pretrained)
        self.model = self._replace_classifier(self.model, self.num_classes)
        self.model.to(self.device)

        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.AdamW(self.model.parameters(), lr=learning_rate)

        if scheduler is not None:
            self.scheduler = scheduler(self.optimizer, **(scheduler_params or {}))
        else:
            self.scheduler = None
        self.best_val_acc = 0.0
        self.best_val_loss = float("inf")

    def _replace_classifier(self, model, num_classes):
        """
        Replace the classification head of timm model to match the number of classes.

        This method handles common classifier attribute names used in timm models such as:
        - 'classifier'
        - 'fc'
        - 'head'

        Args:
            model (torch.nn.Module): The pre-trained model instance.
            num_classes (int): Number of target output classes.

        Returns:
            torch.nn.Module: The model with the replaced classification head.

        Raises:
            AttributeError: If no known classifier attribute is found in the model.
        """
        if hasattr(model, "classifier") and isinstance(model.classifier, nn.Linear):
            in_features = model.classifier.in_features
            model.classifier = nn.Linear(in_features, num_classes)
        elif hasattr(model, "fc") and isinstance(model.fc, nn.Linear):
            in_features = model.fc.in_features
            model.fc = nn.Linear(in_features, num_classes)
        elif hasattr(model, "head") and isinstance(model.head, nn.Linear):
            in_features = model.head.in_features
            model.head = nn.Linear(in_features, num_classes)
        else:
            raise AttributeError("No known classifier layer found in the model to replace.")
        return model

    def evaluate(self):
        """
        Evaluate the model on the validation dataset.

        Returns:
            tuple: (avg_val_loss (float), val_accuracy (float))
        """
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for inputs, labels in self.val_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)

                total_loss += loss.item() * inputs.size(0)
                _, preds = torch.max(outputs, 1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)

        avg_loss = total_loss / total
        accuracy = correct / total
        return avg_loss, accuracy
    
    def train(self):
        """
        Run the training and validation loop for the specified number of epochs.
        Saves the best model based on validation loss and implements early stopping
        if validation accuracy exceeds 99.99%.

        Prints training/validation statistics for each epoch. 
        """
        for epoch in range(self.num_epochs):
            self.model.train()
            running_loss = 0.0
            start_time = time.time()

            for inputs, labels in self.train_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)

                self.optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()
                
                running_loss += loss.item() * inputs.size(0)

            train_loss = running_loss / len(self.train_dataset)
            val_loss, val_acc = self.evaluate()
            current_lr = self.optimizer.param_groups[0]["lr"]
            elapsed = time.time() - start_time

            print(f"Epoch {epoch+1}/{self.num_epochs} | Train Loss: {train_loss:.4f} | "
                  f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc*100:.2f}% | "
                  f"LR: {current_lr:.2e} | Time: {elapsed:.1f}s")
            

            if val_acc > 0.99999:
                torch.save(self.model.state_dict(), "100percent.pth")
                print(f"Best model saved! Val Loss: {self.best_val_loss:.4f}")
                print(f"Val Accuracy reached {self.val_reach * 100:.2f}% training is stopped early.")
                break

            if val_acc > self.best_val_acc:
                self.best_val_acc = val_acc
                torch.save(self.model.state_dict(), self.checkpoint_path)
                print(f"Best model saved! Val Loss: {self.best_val_acc:.4f}")
            
            if self.scheduler is not None:
                if isinstance(self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_loss)
                else:
                    self.scheduler.step()

            
        print("Training completed")
    
    def predict(self, checkpoint_path, test_path=None, test_set_path=None):
        model = timm.create_model(self.model_name, pretrained=False)
        model = self._replace_classifier(model, self.num_classes)
        model.load_state_dict(torch.load(checkpoint_path, map_location=self.device))
        model.to(self.device)
        model.eval()
        preprocessor = Preprocessor(img_size=self.img_size, augment=False)

        if test_set_path is not None:
            correct = 0
            total = 0

            class_to_idx = {}
            classes = sorted([d for d in os.listdir(test_set_path) if os.path.isdir(os.path.join(test_set_path, d))])
            for idx, c, in enumerate(classes):
                class_to_idx[c] = idx
            for class_name in classes:
                class_folder = os.path.join(test_set_path, class_name)
                for fname in os.listdir(class_folder):
                    if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                        continue

                    img_path = os.path.join(class_folder, fname)
                    img = cv2.imread(img_path)
                    if img is None:
                        print(f"Warning: Could not read image {img_path}, skipping.")
                        continue
                    img_proc = preprocessor.preprocess_image(img)
                    img_tensor = torch.tensor(img_proc).to(self.device)
                    
                    with torch.no_grad():
                        output = model(img_tensor)
                        _, pred = torch.max(output, 1)

                    true_label = class_to_idx[class_name]
                    total += 1
                    if pred.item() == true_label:
                        correct += 1
            accuracy = correct / total if total > 0 else 0
            print(f"Test set evaluation: {correct}/{total}correct. Accuracy: {accuracy*100:.2f}%")

        elif test_path is not None:

            img = cv2.imread(test_path)
            if img is None:
                raise ValueError(f"Could not read image from path: {test_path}")
            preprocessor = Preprocessor(img_size=self.img_size, augment=False)
            img = preprocessor.preprocess_image(img)
            img = torch.tensor(img).to(self.device)

            with torch.no_grad():
                output = model(img)
                probabilities = torch.softmax(output, dim=1)
                _, pred = torch.max(output, 1)
            prob_np = probabilities.cpu().numpy().squeeze()
            pred_class = pred.item()
            print(f"Predicted class index: {pred_class}")
            percentages = prob_np * 100
            percentages_str = [f"{p:.2f}%" for p in percentages]
            print("Class probabilities (%):")
            for idx, pct in enumerate(percentages_str):
                print(f"  Class {idx}: {pct}")
    

    def savexml(self, pth_path, output_path, class_number=16, model_name="efficientnet_b0"):
        """
        Converts pth file to xml file and saves it.

        Args:
        pth_path (str): Path of the pth file.
        output_path (str): Path to save xml file.
        class_number (int): Class number for classification problem.
        model_name (str): Model name for creating a model architecture from timm.

        Returns:
        str: Path to created xml file or None if any error occurs.
        """
        model = timm.create_model(model_name, pretrained=False)
        model.classifier = torch.nn.Linear(model.classifier.in_features, class_number)
        model.load_state_dict(torch.load(pth_path))
        model.eval()

        example_input = torch.randn(1, 3, 224, 224)
        ov_model = ov.convert_model(model, example_input=example_input)
        ov.save_model(ov_model, output_path)
    
    def _preprocess_blob_cv(self, img):
        """
        Preprocess image using cv2.dnn.blobFromImage to mimic PyTorch:
        - Resize to 224x224
        - Scale factor 2/255
        - Mean subtraction 1.0
        - Swap BGR->RGB
        - No crop
        """
        blob = cv2.dnn.blobFromImage(
            image=img,
            scalefactor=2.0/255.0,
            size=(224, 224),
            mean=(1.0, 1.0, 1.0),
            swapRB=True,
            crop=False
        )
        return blob
    
    def _softmax(self, x):
        """
        Apply softmax to get probabilities.
        """
        e_x = np.exp(x - np.max(x))
        return e_x / np.sum(e_x, axis=-1, keepdims=True)
    
    def predict_xml(self, xml_path, bin_path, test_path=None, test_set_path=None):
        """
        Predicts using OpenVINO XML model on single image or test dataset.

        Args:
            xml_path (str): Path to xml model file.
            bin_path (str): Path to bin weight file.
            test_path (str, optional): Path to single test image.
            test_set_path (str, optional): Path to test dataset directory.

        Returns:
            None: Prints prediction results.
        """
        core = Core()
        model = core.read_model(xml_path, bin_path)
        compiled_model = core.compile_model(model, "CPU")
        output_layer = compiled_model.output(0)

        if test_set_path is not None:
            correct, total = 0, 0
            wrong_images = []

            class_to_idx = {c: idx for idx, c in enumerate(sorted(os.listdir(test_set_path))) if os.path.isdir(os.path.join(test_set_path, c))}
            idx_to_class = {v: k for k, v in class_to_idx.items()}

            for class_name, idx in class_to_idx.items():
                class_folder = os.path.join(test_set_path, class_name)
                for fname in os.listdir(class_folder):
                    if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                        continue
                    img_path = os.path.join(class_folder, fname)
                    img = cv2.imread(img_path)
                    if img is None:
                        print(f"Warning: Could not read {img_path}, skipping.")
                        continue

                    img_blob = self._preprocess_blob_cv(img)
                    result = compiled_model([img_blob])[output_layer]
                    result = np.squeeze(result)
                    probs = self._softmax(result)
                    pred = int(np.argmax(probs))

                    total += 1
                    if pred == idx:
                        correct += 1
                    else:
                        wrong_images.append((class_name, fname, pred, idx_to_class[pred]))
            
            acc = correct / total if total > 0 else 0
            print(f"Test set evaluation: {correct}/{total} correct. Accuracy: {acc*100:.2f}%")

            if wrong_images:
                print("\nWrong predicted images:")
                for real_class, fname, pred_idx, pred_class_name in wrong_images:
                    print(f"  Actual class: {real_class}, File: {fname}, Predicted class: {pred_idx} ({pred_class_name})")

            elif test_path is not None:
                img = cv2.imread(test_path)
                if img is None:
                    raise ValueError(f"Could not read image from {test_path}")
                img_blob = self._preprocess_blob_cv(img)
                result = compiled_model([img_blob])[output_layer]
                result = np.squeeze(result)
                probs = self._softmax(result)
                pred = int(np.argmax(probs))

                print(f"Predicted class index: {pred}")
                for idx, pct in enumerate(probs*100):
                    print(f"   Class {idx}: {pct:.2f}%")

    def help(self):
        """
        Prints all methods of the Trainer class with their dockstrings.
        Useful for quick reference of available functionalities.
        """
        print(f"Help for {self.__class__.__name__} class methods:\n")
        
        for name, func in self.__class__.__dict__.items():
                if callable(func) and not name.startswith('_'):
                    doc = func.__doc__ or "No documentation available."
                    print(f"Method: {name} \n{'-'*40}\n{doc.strip()}\n")


    
    def print_model_info(self):
        """
        Prints detailed information about the loaded model:
        - Model architecture
        - Model class type
        - Total and trainable parameter counts
        """
        print("=== Model Information ===")
        print(f"Model class: {type(self.model)}\n")
        print(f"Model architecture:\n{self.model}\n")

        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        print(f"Total parameters: {total_params:,}")
        print(f"Trainable parameters: {trainable_params:,}")
        print("=============================")
    
    def list_all_timm_models(self):
        """
        Prints all available model name in the timm library along with the total count.

        Use this to check which pretrained or custom models you can specify
        via the `model_name` parameters in the Trainer()

        Args:
            None
        
        Returns:
            None
        """
        models = timm.list_models(pretrained=False)
        print(f"Total {len(models)} models found in the timm:\n")
        for model_name in models:
            print(model_name)