import cv2
import numpy as np
import os
import math
import matplotlib.pyplot as plt
import sys

# 接受命令行参数
image_path = sys.argv[1]
current_dir = os.path.dirname(os.path.abspath(__file__))

scale = int(sys.argv[4])
min_radius = int(sys.argv[2])
max_radius = int(sys.argv[3])
# 读取图像
image = cv2.imread(image_path)

# 比例尺测量
scale_image = cv2.resize(image, (1500, 1200)).copy()

# 裁剪图像的左下角区域
height, width, _ = scale_image.shape
roi = scale_image[height - 50:, 0:300]  # 裁剪左下角区域，根据实际情况调整坐标和大小

# 灰度化
gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

# 二值化
_, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

# 查找轮廓
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 通过轮廓筛选可能是比例尺的对象
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    
    # 过滤掉太短或太窄的对象，根据实际情况调整阈值
    if w > 100 and h > 2:
        cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 0, 255), 2)
        scale_length_pixels = w  # 获取比例尺的像素长度
        break  # 假设只有一个比例尺，找到一个后就退出循环

# 比例尺的真实长度（例如，1毫米）
scale_length_mm = scale  # 假设比例尺的真实长度为10毫米

# 计算像素到真实尺寸的转换比例
pixel_to_mm_ratio = scale_length_mm / scale_length_pixels
min_radius /= pixel_to_mm_ratio
max_radius /= pixel_to_mm_ratio
with open('scale.txt', 'w') as file:
    file.write(f'{pixel_to_mm_ratio}\n')
    file.write(f'{scale_length_pixels}\n')

filtered_image = cv2.resize(image, (1500, 1200)).copy()#方便最后画图并且缩放

# 2. 复制图层
layer = image.copy()

# 3. 模糊当前图层
blurred_layer = cv2.GaussianBlur(layer, (301, 301), 0)

# 4. 调低亮度
lowered_brightness = cv2.convertScaleAbs(blurred_layer, alpha=1, beta=-50)
# 5. 图层混合（减去）
blended_image = cv2.subtract(layer, lowered_brightness)

# 6. 合并图
#merged_layer = cv2.add(layer, blended_image)

#先得到亮度的最小值和最大值，然后将亮度区间映射到0-255
min_brightness = np.min(blended_image)
max_brightness = np.max(blended_image)
blended_image = cv2.convertScaleAbs(blended_image, alpha=255/(max_brightness-min_brightness), beta=-255*min_brightness/(max_brightness-min_brightness))
# 7. 模糊当前图层

blurred_merged_layer=cv2.convertScaleAbs(blended_image, alpha=-1., beta=80)
blurred_merged_layer=cv2.convertScaleAbs(blurred_merged_layer, alpha=3., beta=0)
blurred_merged_layer = cv2.GaussianBlur(blurred_merged_layer, (5, 5), 0)

# 8. 调曲线
# 创建一个包含256个条目的查找表

curve = np.arange(256, dtype=np.uint8)

# 在查找表上应用您的映射规则
curve[0:50] = 0  # 将前50个像素值映射为0
curve[50:100] = 50  # 将50-100的像素值映射为25
curve[100:140] = 75  # 将100-150的像素值映射为75
curve[140:190] = 110     # 将150-200的像素值映射为150
curve[190:255] = 255  # 将150-255的像素值映射为200

# 使用新的查找表应用LUT
blurred_merged_layer = cv2.LUT(blurred_merged_layer, curve)

# 9. 保存最终图片
output_path = 'blurred_image.jpg'

cv2.imwrite(output_path, blurred_merged_layer)

# 1. 图像处理
current_dir = os.path.dirname(os.path.abspath(__file__))

# 1. 图像处理
image_path = os.path.join(current_dir, "blurred_image.jpg")

big_image = cv2.imread(image_path)
image = cv2.resize(big_image, (1500, 1200))  # 缩小图像到 800x600
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

_, binary_image = cv2.threshold(gray_image, 100, 255, cv2.THRESH_BINARY_INV)
#cv2.imshow("binary_image", binary_image)
# 2. 形态学操作 - 膨胀和腐蚀
kernel = np.ones((5,5), np.uint8)
dilated_image = cv2.dilate(binary_image, kernel, iterations=1)
eroded_image = cv2.erode(dilated_image, kernel, iterations=2)
cv2.imwrite('eroded_image.jpg', eroded_image)

# 3. 滤波器 - 高斯滤波器
blurred_image = cv2.GaussianBlur(eroded_image, (3, 3), 0)
# 4. 边缘检测和轮廓提取
edges = cv2.Canny(blurred_image, threshold1=50, threshold2=100)
contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 5. 绘制筛选后的轮廓


# 计算直径数据
diameters = []  # 存储圆的直径

for contour in contours:
# 计算轮廓的面积和周长
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    
    # 如果面积和周长满足条件，绘制轮廓并计算直径
    if area>math.pi*min_radius**2 and area < math.pi*max_radius**2 and perimeter > math.pi*2*min_radius and perimeter < math.pi*2*max_radius:
        cv2.drawContours(filtered_image, [contour], -1, (0, 255, 0), 2)
        
        # 计算轮廓的最小外接圆
        (x, y), radius = cv2.minEnclosingCircle(contour)
        
        # 过滤掉半径不满足条件的圆
        if radius >min_radius and radius<max_radius:
            cv2.circle(filtered_image, (int(x), int(y)), int(radius), (0, 0, 255), 2)
            diameter = radius * 2
            diameters.append(diameter)

# 保存最终图片
output_path = 'processed_image.jpg'
cv2.imwrite(output_path, filtered_image)
# 将直径数据输出到文件
with open('diameters.txt', 'w') as file:
    file.write(f'{pixel_to_mm_ratio}\n')
    for diameter in diameters:
        file.write(f'{diameter*pixel_to_mm_ratio}\n')

# 输出结果文件路径
print(output_path)