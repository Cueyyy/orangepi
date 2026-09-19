import cv2
import numpy as np
import os
from datetime import datetime

# =========================
# 路径配置
# =========================
CAMERA_ID = "/dev/video1"

PARAMS_FILE = "/home/orangepi/Desktop/test_base/senor/pic/fisheye_params.npz"

PHOTO_DIR = "/home/orangepi/Desktop/test_base/senor/corrected_photos"
VIDEO_DIR = "/home/orangepi/Desktop/test_base/senor/corrected_videos"

# 创建保存目录
os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

# =========================
# 读取标定参数
# =========================
data = np.load(PARAMS_FILE)

K = data["K"]
D = data["D"]

print("K =")
print(K)

print("D =")
print(D)

# =========================
# 打开摄像头
# =========================
cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_V4L2)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("摄像头打开失败！")
    exit()

# 读取一帧，确定实际分辨率
ret, frame = cap.read()

if not ret:
    print("无法读取摄像头画面！")
    cap.release()
    exit()

h, w = frame.shape[:2]

print("实际分辨率：", w, "x", h)

# =========================
# 计算畸变校正映射表
# =========================
new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
    K,
    D,
    (w, h),
    np.eye(3),
    balance=0.0
)

print("new_K =")
print(new_K)

map1, map2 = cv2.fisheye.initUndistortRectifyMap(
    K,
    D,
    np.eye(3),
    new_K,
    (w, h),
    cv2.CV_32FC1
)

print("畸变校正映射表生成完成！")

# =========================
# 录像相关变量
# =========================
video_writer = None
recording = False

print()
print("操作说明：")
print("按 s：保存一张校正后的照片")
print("按 v：开始/停止录像")
print("按 q：退出程序")

# =========================
# 主循环
# =========================
while True:
    ret, frame = cap.read()

    if not ret:
        print("读取画面失败！")
        break

    # 畸变校正
    corrected_frame = cv2.remap(
        frame,
        map1,
        map2,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT
    )

    # 显示校正后的画面
    show_frame = corrected_frame.copy()

    if recording:
        cv2.putText(
            show_frame,
            "REC",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

        # 保存校正后的画面到视频
        video_writer.write(corrected_frame)

    cv2.imshow("Corrected Camera", show_frame)

    key = cv2.waitKey(1) & 0xFF

    # 按 s：保存照片
    if key == ord("s"):
        filename = datetime.now().strftime("photo_%Y%m%d_%H%M%S.jpg")
        filepath = os.path.join(PHOTO_DIR, filename)

        cv2.imwrite(filepath, corrected_frame)

        print("照片已保存：")
        print(filepath)

    # 按 v：开始或停止录像
    elif key == ord("v"):

        if not recording:
            filename = datetime.now().strftime("video_%Y%m%d_%H%M%S.avi")
            filepath = os.path.join(VIDEO_DIR, filename)

            # MJPG 编码，兼容性较好
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")

            video_writer = cv2.VideoWriter(
                filepath,
                fourcc,
                20.0,
                (w, h)
            )

            if not video_writer.isOpened():
                print("录像文件创建失败！")
                video_writer = None
            else:
                recording = True
                print("开始录像：")
                print(filepath)

        else:
            recording = False

            if video_writer is not None:
                video_writer.release()
                video_writer = None

            print("录像已停止！")

    # 按 q：退出
    elif key == ord("q"):
        break

# =========================
# 释放资源
# =========================
if video_writer is not None:
    video_writer.release()

cap.release()
cv2.destroyAllWindows()

print("程序已退出！")