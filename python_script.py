import cv2
import numpy as np
import os
import math
import matplotlib.pyplot as plt
import sys

#***Step1: Get the arguments from the frontend***
image_path = sys.argv[1]
image = cv2.imread(image_path)
# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Read the scale value, min radius, and max radius from command line arguments
scale = int(sys.argv[4])
min_radius = int(sys.argv[2])
max_radius = int(sys.argv[3])
# Resize the input image to a fixed size
scale_image = cv2.resize(image, (1500, 1200)).copy()

#***Step2: Extract a plotting scale from the scaled image. Remember to use the white scale!***
height, width, _ = scale_image.shape
roi = scale_image
# Convert the scale to grayscale
gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
# Apply thresholding to the grayscale image
_, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
# Find contours of the scale
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# Iterate through the contours to find the scale
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    # Check if the contour corresponds to the scale reference
    if w > 100 and h > 2:
        cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 0, 255), 2)
        scale_length_pixels = w  # Determine the pixel length of the scale
        break
# Define the known scale length
scale_length = scale
# Calculate the pixel-to-length ratio
pixel_to_length_ratio = scale_length / scale_length_pixels
min_radius /= pixel_to_length_ratio
max_radius /= pixel_to_length_ratio

#***Step3: Balance the image's lightness***
filtered_image = cv2.resize(image, (1500, 1200)).copy()
# Apply Gaussian blur to the image
layer = image.copy()
blurred_layer = cv2.GaussianBlur(layer, (301, 301), 0)
# Adjust the brightness of the blurred image
lowered_brightness = cv2.convertScaleAbs(blurred_layer, alpha=1, beta=-50)
# Create a blended image by subtracting the lowered brightness from the original
blended_image = cv2.subtract(layer, lowered_brightness)
# Merge the blended image with the original image
merged_layer = cv2.add(layer, blended_image)
# Further process the merged layer to enhance features
blurred_merged_layer = cv2.convertScaleAbs(blended_image, alpha=-1., beta=90)
blurred_merged_layer = cv2.convertScaleAbs(blurred_merged_layer, alpha=3., beta=0)

#***Step4: Apply algorithms to find coutours of the nanoparticles***
image = cv2.resize(blurred_merged_layer, (1500, 1200))
# Convert the image to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# Apply thresholding to the grayscale image
_, binary_image = cv2.threshold(gray_image, 100, 255, cv2.THRESH_BINARY_INV)
# Create a kernel for morphological operations
kernel = np.ones((5, 5), np.uint8)
# Dilate and then erode the binary image
dilated_image = cv2.dilate(binary_image, kernel, iterations=1)
eroded_image = cv2.erode(dilated_image, kernel, iterations=2)
# Apply Gaussian blur to the eroded image
blurred_image = cv2.GaussianBlur(eroded_image, (3, 3), 0)
# Detect edges in the blurred image using the Canny edge detector
edges = cv2.Canny(blurred_image, threshold1=50, threshold2=100)
# Find contours in the edge-detected image
contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#***Step5: Draw coutours of the nanoparticles in the image***
# Initialize a list to store diameters
diameters = []
# Iterate through the contours to find circles within specified radius ranges
for contour in contours:
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)

    # Check if the contour corresponds to a circle within the specified radius range
    if area > math.pi * min_radius**2 and area < math.pi * max_radius**2 and perimeter > math.pi * 2 * min_radius and perimeter < math.pi * 2 * max_radius:
        cv2.drawContours(filtered_image, [contour], -1, (0, 255, 0), 2)
        # Find the minimum enclosing circle of the contour
        (x, y), radius = cv2.minEnclosingCircle(contour)
        # Check if the radius falls within the specified range
        if radius > min_radius and radius < max_radius:
            cv2.circle(filtered_image, (int(x), int(y)), int(radius), (0, 0, 255), 2)
            diameter = radius * 2
            diameters.append(diameter)

#**Step6: Save the processed image and the diameters**
# Save the processed image with highlighted circles
output_path = 'processed_image.jpg'
cv2.imwrite(output_path, filtered_image)
# Write the pixel-to-millimeter ratio and calculated diameters to a text file
with open('diameters.txt', 'w') as file:
    file.write(f'{pixel_to_length_ratio}\n')
    for diameter in diameters:
        file.write(f'{diameter * pixel_to_length_ratio}\n')

# Print the path to the processed image
print(output_path)
