# VisionEdgeFusion 👁️‍🗨️

**A lightweight and educational Python toolkit for fundamental feature extraction using Difference of Gaussians (DoG) and Histogram of Oriented Gradients (HoG).**

## Overview

VisionEdgeFusion is a Python library designed to provide clear, efficient, and accessible implementations of two cornerstone computer vision algorithms. It empowers users to perform robust edge and blob detection with Difference of Gaussians and to conduct powerful feature description for object detection using the Histogram of Oriented Gradients.

This toolkit is perfect for students, educators, and developers who want to understand and apply these fundamental techniques without the overhead of larger, more complex computer vision libraries.

## Installation

Install VisionEdgeFusion easily using pip:
```bash
pip install visionedgefusion
```

## Usage

Import the `v1` functions to get started.

### Difference of Gaussians (DoG)

```python
import cv2
import matplotlib.pyplot as plt
from visionedgefusion.v1 import difference_of_gaussians
from skimage.data import camera # Using a sample image

# Load an image
image = camera()

# Apply the Difference of Gaussians
dog_image = difference_of_gaussians(image, low_sigma=1.0, high_sigma=3.0)

# Display the results
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.imshow(image, cmap='gray')
plt.title('Original Image')
plt.axis('off')

plt.subplot(1, 2, 2)
plt.imshow(dog_image, cmap='gray')
plt.title('DoG Edges')
plt.axis('off')

plt.show()
```

### Histogram of Oriented Gradients (HoG)

```python
import cv2
import matplotlib.pyplot as plt
from visionedgefusion.v1 import histogram_of_oriented_gradients
from skimage.data import astronaut # Using a sample image

# Load an image
image = astronaut()
image_person = image[0:180, 150:280] # Crop to a person for better HOG viz

# Get HOG features and visualization
hog_features, hog_image = histogram_of_oriented_gradients(image_person, visualize=True)

print(f"HOG Feature Vector Shape: {hog_features.shape}")
print(f"Number of features: {len(hog_features)}")

# Display the results
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.imshow(image_person)
plt.title('Original Cropped Image')
plt.axis('off')

plt.subplot(1, 2, 2)
plt.imshow(hog_image, cmap='gray')
plt.title('HOG Visualization')
plt.axis('off')

plt.show()
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.