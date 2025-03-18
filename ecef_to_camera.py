import cv2
import numpy as np
import pandas as pd
from math import radians, sin, cos

# 1. 读取 txt 文件并转换为 DataFrame
def read_txt_to_df(file_path):
    # 指定列名
    column_names = ["TIME_GPST", "time", "SAT", "AZ(deg)", "EL(deg)", "SNR(dBHz)", "L1/LC"]
    
    # 读取数据，使用空格或 TAB 分隔，跳过第一行（假设无效行）
    df = pd.read_csv(file_path, delim_whitespace=True, names=column_names, skiprows=1, engine='python')
    
    # 解析时间列
    df["TIME_GPST"] = pd.to_datetime(df["TIME_GPST"] + " " + df["time"], format='%Y/%m/%d %H:%M:%S.%f')
    
    # 删除原始 time 列（已合并入 TIME_GPST）
    df.drop(columns=['time'], inplace=True)
    
    return df

# 读取两个文件
ordinary_df = read_txt_to_df('/home/Fisheye/leica316.txt')
choke_df = read_txt_to_df('/home/Fisheye/trimbel316.txt')

# 2. 剔除 "AZ(deg)" 为 0.0 且 "EL(deg)" 为 90.0 的数据
def filter_df(df):
    return df[~((df['AZ(deg)'] == 0.0) & (df['EL(deg)'] == 90.0))]

ordinary_filtered = filter_df(ordinary_df)
choke_filtered = filter_df(choke_df)

# 3. 按 TIME_GPST 和 SAT 进行分组
ordinary_grouped = ordinary_filtered.groupby(['TIME_GPST', 'SAT'])
choke_grouped = choke_filtered.groupby(['TIME_GPST', 'SAT'])

# 4. 识别 LOS 和 NLOS
nlos_list = []
los_list = []

# 遍历 ordinary_grouped
for (time, sat), ordinary_group in ordinary_grouped:
    if (time, sat) in choke_grouped.groups:
        los_list.append(ordinary_group)  # 该卫星在 choke 数据中也存在，归为 LOS
    else:
        nlos_list.append(ordinary_group)  # 该卫星在 choke 数据中不存在，归为 NLOS

# 合并数据
nlos_df = pd.concat(nlos_list, ignore_index=True)
los_df = pd.concat(los_list, ignore_index=True)

# 添加标签
nlos_df['Label'] = 'NLOS'
los_df['Label'] = 'LOS'

# 5. 读取鱼眼图像
image_path = "/home/Fisheye/north_g_3.16_17m15s.jpg"  # 请替换为实际图像路径
image = cv2.imread(image_path)
if image is None:
    print("无法读取图像，请检查路径是否正确！")
    exit()

# 6. 定义图像参数
center_x, center_y = 706, 733  # 图像中心坐标
radius = 602                   # 鱼眼图像半径（像素）
fov = 180                      # 视场角（度）
f = radius / (fov / 2)         # 焦距（像素/度）

# 7. 获取用户输入的时间戳
#timestamp = input("请输入时间戳 (格式: YYYY-MM-DD HH:MM:SS): ")
timestamp = "2025-03-16 09:34:55"
# 8. 过滤 LOS 和 NLOS 数据
los_satellites = los_df[los_df['TIME_GPST'] == pd.to_datetime(timestamp)]
nlos_satellites = nlos_df[nlos_df['TIME_GPST'] == pd.to_datetime(timestamp)]

if los_satellites.empty and nlos_satellites.empty:
    print("未找到该时间戳的卫星数据！")
    exit()

# 9. 投影并绘制卫星的函数
def project_and_draw_satellites(satellites, color):
    for index, row in satellites.iterrows():
        AZ = row['AZ(deg)']    # 方位角（度）
        EL = row['EL(deg)']    # 仰角（度）
        sat_name = row['SAT']  # 卫星名称
        
        # 计算投影坐标
        theta = 90 - EL              # 视角（度）
        r = f * theta                # 径向距离（像素）
        phi_deg = 270 - AZ           # 图像角度（度）
        phi_rad = radians(phi_deg)   # 转换为弧度
        x = center_x + r * cos(phi_rad)
        y = center_y + r * sin(phi_rad)
        
        # 绘制圆点
        cv2.circle(image, (int(x), int(y)), 5, color, -1)
        # 添加卫星名称标签
        cv2.putText(image, sat_name, (int(x) + 10, int(y)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

# 绘制 LOS（绿色）
project_and_draw_satellites(los_satellites, (0, 255, 0))

# 绘制 NLOS（红色）
project_and_draw_satellites(nlos_satellites, (0, 0, 255))

# 10. 保存结果图像
output_path = "fisheye_with_satellites2.jpg"
cv2.imwrite(output_path, image)
print(f"已保存带卫星投影的图像到: {output_path}")