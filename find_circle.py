import cv2
import numpy as np
import matplotlib.pyplot as plt

# 读取鱼眼图像
image_path = "/home/Fisheye/kentic_20250316_221310_421768.jpg"
image = cv2.imread(image_path, cv2.IMREAD_COLOR)

# 转换为灰度图像
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 应用高斯模糊
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# 使用Canny边缘检测
edges = cv2.Canny(blurred, 50, 150)

# 使用霍夫变换检测圆
circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1.1, minDist=100,
                           param1=50, param2=30, minRadius=10, maxRadius=1000)

# 计算图像尺寸
h, w = gray.shape

# 计算理论上的中心点
ideal_center = (w // 2, h // 2)

# 处理检测到的圆
if circles is not None:
    circles = np.uint16(np.around(circles))
    detected_center = (circles[0, 0, 0], circles[0, 0, 1])
    detected_radius = circles[0, 0, 2]
else:
    detected_center = None
    detected_radius = None

# 计算圆心偏移
if detected_center:
    offset_x = detected_center[0] - ideal_center[0]
    offset_y = detected_center[1] - ideal_center[1]
else:
    offset_x, offset_y = None, None

# 可视化检测结果
fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
ax[0].set_title("Original Image")
ax[1].imshow(edges, cmap='gray')
ax[1].set_title("Detected Edges")

# 在原图上标记圆心
if detected_center:
    cv2.circle(image, detected_center, detected_radius, (0, 255, 0), 2)
    cv2.circle(image, detected_center, 5, (0, 0, 255), -1)  # 标记圆心  红色
    cv2.circle(image, ideal_center, 5, (255, 0, 0), -1)  # 标记理论中心  蓝色

ax[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

plt.savefig("12.jpg")

# 返回检测到的圆心和偏移量
print("Circle center:",detected_center, offset_x, offset_y)
#print("ideal Circle center:",ideal_center, offset_x, offset_y)
print("Circle detected_radius:",detected_radius)