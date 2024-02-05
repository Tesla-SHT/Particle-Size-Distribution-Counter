import cv2
import numpy as np
import pandas as pd
import os
import math
import matplotlib.pyplot as plt
import sys
rel_files=[]
tif_files = []
def get_tif_files(folder_path):
    normalized_path = os.path.normpath(folder_path)
    for root, dirs, files in os.walk(normalized_path):
        for file in files:
            if file.lower().endswith('.tif'):
                tif_files.append(os.path.join(root, file))
                rel_files.append(file)
    return tif_files

folder_path = input('Enter folder path: ')
scale = int(input("Enter scale: "))
min_radius = int(input("Enter min_radius: "))
max_radius = int(input("Enter max_radius: "))
tif_files = get_tif_files(folder_path)
index=-1
D = []
for file_path in tif_files:
    index+=1
    print(file_path)
    image = cv2.imread(file_path)

    scale_image = image.copy()

    height, width, _ = scale_image.shape
    roi = scale_image  

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        if w > 100 and h > 2:
            cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 0, 255), 2)
            print(x,y,w,h)
            scale_length_pixels = w  
            break  

    
    scale_length_mm = scale  

    
    pixel_to_mm_ratio = scale_length_mm / scale_length_pixels
    min_radius /= pixel_to_mm_ratio
    max_radius /= pixel_to_mm_ratio
    print(scale_length_pixels)

    filtered_image = image.copy()

    
    layer = image.copy()

    
    blurred_layer = cv2.GaussianBlur(layer, (501, 501), 0)

   
    lowered_brightness = cv2.convertScaleAbs(blurred_layer, alpha=1, beta=-50)

    
    blended_image = cv2.subtract(layer, lowered_brightness)

   
    merged_layer = cv2.add(layer, blended_image)

   
    blurred_merged_layer=cv2.convertScaleAbs(blended_image, alpha=-1., beta=90)
    blurred_merged_layer=cv2.convertScaleAbs(blurred_merged_layer, alpha=3., beta=0)


    gray_image = cv2.cvtColor(blurred_merged_layer, cv2.COLOR_BGR2GRAY)

    _, binary_image = cv2.threshold(gray_image, 100, 255, cv2.THRESH_BINARY)

    kernel = np.ones((5,5), np.uint8)
    dilated_image = cv2.dilate(binary_image, kernel, iterations=1)
    eroded_image = cv2.erode(dilated_image, kernel, iterations=2)


    blurred_image = cv2.GaussianBlur(eroded_image, (3, 3), 0)

    edges = cv2.Canny(blurred_image, threshold1=50, threshold2=100)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    diameters = [] 

    for contour in contours:

        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if area>math.pi*min_radius**2 and area < math.pi*max_radius**2 and perimeter > math.pi*2*min_radius and perimeter < math.pi*2*max_radius:
            cv2.drawContours(filtered_image, [contour], -1, (0, 255, 0), 2)
            
            (x, y), radius = cv2.minEnclosingCircle(contour)
            radius = (area/math.pi)**0.5

            if radius >min_radius and radius<max_radius:
                cv2.circle(filtered_image, (int(x), int(y)), int(radius), (0, 0, 255), 2)
                diameter = radius * 2
                diameters.append(diameter)


    output_path = 'processed_'+rel_files[index]+'.jpg'
    cv2.imwrite(output_path, filtered_image)

    D.append(diameters)



data = {'File': rel_files,
        'Diameter': D}
print(data)
dfs = []


for file, diameters in zip(data['File'], data['Diameter']):
    df = pd.DataFrame({'File': [file], 'Diameter': [diameters]})
    dfs.append(df)


df = pd.concat(dfs, ignore_index=True)


df.to_excel('output.xlsx', index=False)