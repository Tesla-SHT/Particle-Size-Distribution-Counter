# Particle-Size-Distribution-Counter
We developed the Nanoparticle Size Distribution Counter software. This tool is designed to simplify and expedite the analysis of multiple types of photos like Transmission Electron Microscopy (TEM) graphs, microscopy graphs ect., enabling researchers to obtain accurate and comprehensive statistical information about particle size distributions within a given sample.

## Description
Our software uses Electron as the frontend frame and Python as the backend language. Its mechanism is based on OpenCV, including image processing algorithms and statistical modeling techniques. The main code can be divided by 4 steps: 
1. Extract a plotting scale from the scaled image (make sure the color is white).
2. Balance the image's lightness for more accurate recognition.
3. Apply algorithms for the image adjustment.
4. Draw the coutours of the nanoparticles and collect the diameters

It is important to note that the accuracy of the results depends on the quality of the input graph. Therefore, it is recommended to ensure high-resolution and well-defined images for optimal analysis. Additionally, users have the option to customize various parameters.

Furthermore, when the object is very large (just one in the image), we can accurately measure its diameter (the scale should be black though). This code is Diameter-Measurement.py, simple but useful. And you can just enter the folder's name, this program will automatically process every image and export the data to output.xlsx

## Installation
- Install npm [Download npm](https://nodejs.org)

- Open cmd in the root dir:

    npm install electron

    npm install echart

    npm run start

    Relevant Doc: [Building your First App](https://www.electronjs.org/docs/latest/tutorial/tutorial-first-app)

- Packages for Python:

    import cv2

    import numpy

    import os

    import math

    import matplotlib.pyplot

    import sys
## Usage
1. Generate a TEM graph with a white plotting scale 
<div align=center>
<img src = "https://static.igem.wiki/teams/4702/wiki/software/particle-size-distribution-counter/example.jpg" alt = "example image" style = "padding-left:25%; width:50%;"/>
</div>

2. After entering the app, you can choose the file's path and enter the min-radius, max-radius, scale and width of the distribution bars in the scale's unit. Then Click to process image!
<div align=center>
<img src = "https://static.igem.wiki/teams/4702/wiki/software/particle-size-distribution-counter/main-display.png" alt = "example image" style = "padding-left:25%; width:75%;"/>
</div>

3. Then the app will generate an image with nanoparticles contoured with green color and circled with red color.

    <div align=center>
    <img src = "https://static.igem.wiki/teams/4702/wiki/software/particle-size-distribution-counter/image.jpg" alt = "example image" style = "padding-left:12.5%; width:75%;"/>
    </div>
    And it will generate a bar graph, providing users with a clear and intuitive visualization of the particle size distribution.
        <div align=center>
    <img src = "https://static.igem.wiki/teams/4702/wiki/software/particle-size-distribution-counter/bar.png" alt = "example image" style = "padding-left:10%; width:80%;"/>
    </div>

## Contributing
This code is open to contributions.
## Authors and acknowledgment
The inspiration of this script came from Shouyi Hu, and Haotian Shen brought it into codes.

