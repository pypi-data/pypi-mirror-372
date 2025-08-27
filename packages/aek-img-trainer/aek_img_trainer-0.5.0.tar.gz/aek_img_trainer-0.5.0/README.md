<div align="center">
  <img src="https://raw.githubusercontent.com/alpemre8/aek-img-trainer/main/logo.png" alt="AEK Image Trainer Logo" width="400"/>
  
  # AEK Image Trainer
  
  AI image preprocessing library 
</div>



# Installation


```bash
pip install aek-img-trainer
```
For more secure way after doing that you can upgrade via:
```bash
pip install --upgrade aek-img-trainer
```
# Usage


## Create object


Now you can just use Trainer class methods example usage is shown below.
```python
from aek_img_trainer import Trainer, Preprocessor

model = Trainer(train_root="root/trainset",
                val_root="root/valset",
                num_classes=16,
                img_size=224,
                batch_size=4,
                val_reach=0.9999,
                num_epochs=150,
                learning_rate=1e-3,
                checkpoint_path="efficientnet_b0_best_model.pth",
                model_name="efficientnet_b0",
                device=None,
                augment=True,
                scheduler=None,
                scheduler_params=None,
                pretrained=True)
```

Those hyperparameters without train and val dataset path are default if you want to use default parameters you can just give your train and val datasets' path.
```python
model = Trainer(train_root="root/trainset",val_root="root/valset")
```

# Training


You can train your model with parameter that created earlier.
```python
model.train()
```

# Prediction


You can use your model in test with below code.
```python
model.predict(checkpoint_path="example_model.pth",
               test_path="root/test.png")
```
Or if you give the test set path this method predict all images in the dataset folder. Your dataset should be labelled like training dataset.

Example usage:
```python
model.predict(checkpoint_path="example_model.pth",
                test_set_path="root/testset")
```

# Save XML


You can save the pth model file to xml and bin files 

Example usage:

```python
model.savexml(pth_path="efnet.pth", output_path="efnet.xml", class_number=16, model_name="efficientnet_b0")
```


# Prediction on XML file


You can predict the model with xml and bin files. Like above predict function predict_xml takes either test_path or test_set_path and changes the result with the given path, either predict one image or images that inside the test set. Test set should be labelled like a training dataset.

Example usage:

```python
model.predict_xml(xml_path="enfet.xml", bin_path="efnet.bin", test_path=None, test_set_path="root/testset")
```



# Information


You can see your model's parameters and architecture.
```python
model.print_model_info()
```

# Help function for Trainer class


You can use help() function for get more information about functions that inside the Trainer class.
```python
model.help()
```


# Timm models


You can get models that inside the timm library you can use with their name in string format inside the Trainer() 'model_name' paramaters.
ATTENTION: You can just use the models whose head layers are 'fc', 'head' and 'classifier'
```python
model.list_all_timm_models()
```









