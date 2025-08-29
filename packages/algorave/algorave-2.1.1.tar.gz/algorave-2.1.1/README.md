# Algorave

A fast and flexible image augmentation library for deep learning, computer vision, and machine learning workflows.

Algorave is a fork of the [Albumentations](https://github.com/albumentations-team/albumentations) library, providing powerful image transformation capabilities with a focus on performance and ease of use.

## Installation

```bash
pip install algorave
```

For development installation:
```bash
git clone https://github.com/your-username/algorave.git
cd algorave
pip install -e .
```

## Features

- **Fast and efficient**: Optimized for performance with NumPy and OpenCV backends
- **Flexible**: Supports a wide range of image augmentations for various computer vision tasks
- **Easy to use**: Simple, intuitive API that integrates seamlessly with popular deep learning frameworks
- **Extensible**: Easy to add custom augmentations
- **Battle-tested**: Based on the proven Albumentations library used in numerous production systems

## Quick Start

```python
import algorave as A
import cv2

# Define an augmentation pipeline
transform = A.Compose([
    A.RandomCrop(width=256, height=256),
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.2),
])

# Read an image
image = cv2.imread("image.jpg")
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Apply augmentations
transformed = transform(image=image)
transformed_image = transformed["image"]
```

## Supported Data Types

Algorave supports augmentation of:
- Images
- Masks
- Bounding boxes
- Keypoints

## Requirements

- Python >= 3.9
- NumPy
- OpenCV
- PyYAML
- scikit-image (optional)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Algorave is based on [Albumentations](https://github.com/albumentations-team/albumentations), originally created by the Albumentations team. This fork was created from commit [66212d7](https://github.com/albumentations-team/albumentations/commit/66212d75638f25dae1842ad3db069cf3bf4f8449).

Special thanks to the original Albumentations authors:
- Vladimir Iglovikov
- Alexander Buslaev
- Alex Parinov
- Eugene Khvedchenya
- Mikhail Druzhinin