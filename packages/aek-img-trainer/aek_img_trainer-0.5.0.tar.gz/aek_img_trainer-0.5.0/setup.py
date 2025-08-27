from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='aek-img-trainer',
    version='0.5.0',
    description='Image classification trainer using OpenCV and timm',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Alp Emre Karaahmet',
    author_email='alpemrekaraahmet@gmail.com',
    packages=find_packages(),
    install_requires=[
        'torch',
        'opencv-python',
        'numpy',
        'timm',
        'openvino',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)
