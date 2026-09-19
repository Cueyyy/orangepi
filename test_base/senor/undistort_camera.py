import cv2
import numpy as np
import os

CAMERA_ID = "/dev/video1"

PARAM_FILE = (
    "/home/orangepi/Desktop/test_base/senor/pic/"
    "fisheye_params.npz"
)

# =========================
# 1. 加载参数
# =========================

if not os.path.exists(PARAM_FILE):
    print("找不到参数文件！")
    exit()

data = np.load(PARAM_FILE)

K = data["K"].astype(np.float64)
D = data["D"].astype(np.float64)

print("K =\n", K)
print("D =\n", D)
print("RMS =", data["rms"])

# 检查参数是否存在 NaN 或无穷大
if not np.isfinite(K).all() or not np.isfinite(D).all():
    print("参数中存在 NaN 或无穷大！")
    exit()

# =========================
# 2. 打开摄像头
# =========================

cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_V4L2)

if not cap.isOpened():
    print("摄像头打开失败！")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

ret, frame = cap.read()

if not ret:
    print("读取画面失败！")
    cap.release()
    exit()

h, w = frame.shape[:2]

print("实际分辨率：", w, "x", h)

# 检查标定尺寸
calib_w = int(data["image_width"])
calib_h = int(data["image_height"])

print("标定分辨率：", calib_w, "x", calib_h)

if (w, h) != (calib_w, calib_h):
    print("警告：当前分辨率与标定分辨率不一致！")

# =========================
# 3. 生成映射表
# =========================

try:
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
        K,
        D,
        (w, h),
        np.eye(3),
        balance=0.0
    )

    print("new_K =\n", new_K)

    map1, map2 = cv2.fisheye.initUndistortRectifyMap(
        K,
        D,
        np.eye(3),
        new_K,
        (w, h),
        cv2.CV_32FC1
    )

except cv2.error as e:
    print("生成映射表失败：")
    print(e)
    cap.release()
    exit()

print("map1范围：", np.nanmin(map1), np.nanmax(map1))
print("map2范围：", np.nanmin(map2), np.nanmax(map2))

# =========================
# 4. 实时去畸变
# =========================

while True:

    ret, frame = cap.read()

    if not ret:
        print("读取画面失败！")
        break

    undistorted = cv2.remap(
        frame,
        map1,
        map2,
        cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT
    )

    cv2.imshow("Original", frame)
    cv2.imshow("Undistorted", undistorted)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        cv2.imwrite(
            "/home/orangepi/Desktop/test_base/senor/pic/undistorted.jpg",
            undistorted
        )
        print("已保存校正图片")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()