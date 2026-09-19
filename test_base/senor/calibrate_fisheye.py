import cv2
import numpy as np
import glob
import os

# =========================
# 1. 参数配置
# =========================

CHECKERBOARD = (9, 6)
SQUARE_SIZE = 25.0

IMAGE_DIR = "/home/orangepi/Desktop/test_base/senor/pic"

PARAM_FILE = os.path.join(
    IMAGE_DIR, "fisheye_params.npz"
)

# =========================
# 2. 创建棋盘格三维坐标
# =========================

objp = np.zeros(
    (1, CHECKERBOARD[0] * CHECKERBOARD[1], 3),
    np.float32
)

objp[0, :, :2] = np.mgrid[
    0:CHECKERBOARD[0],
    0:CHECKERBOARD[1]
].T.reshape(-1, 2)

objp *= SQUARE_SIZE

objpoints = []
imgpoints = []

# 只读取标定照片，避免读取参数文件等其他内容
images = sorted(
    glob.glob(os.path.join(IMAGE_DIR, "calib_*.jpg"))
)

if len(images) == 0:
    print("没有找到标定照片！")
    print("请先运行拍照程序")
    exit()

print("找到", len(images), "张照片")

# =========================
# 3. 检测棋盘格角点
# =========================

image_size = None
success_count = 0
failed_images = []

for filename in images:

    img = cv2.imread(filename)

    if img is None:
        print("无法读取：", filename)
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    current_size = (gray.shape[1], gray.shape[0])

    if image_size is None:
        image_size = current_size

    # 检查照片尺寸是否一致
    if current_size != image_size:
        print("尺寸不一致，跳过：", filename)
        failed_images.append(filename)
        continue

    # 检测棋盘格
    ret, corners = cv2.findChessboardCorners(
        gray,
        CHECKERBOARD,
        cv2.CALIB_CB_ADAPTIVE_THRESH
        + cv2.CALIB_CB_NORMALIZE_IMAGE
    )

    if ret:
        criteria = (
            cv2.TERM_CRITERIA_EPS
            + cv2.TERM_CRITERIA_MAX_ITER,
            30,
            0.001
        )

        corners = cv2.cornerSubPix(
            gray,
            corners,
            (3, 3),
            (-1, -1),
            criteria
        )

        objpoints.append(objp.copy())
        imgpoints.append(corners)

        success_count += 1

        print("检测成功：", os.path.basename(filename))

    else:
        print("检测失败：", os.path.basename(filename))
        failed_images.append(filename)

print("\n成功检测：", success_count, "张")
print("检测失败：", len(failed_images), "张")

if success_count < 6:
    print("有效照片太少，至少需要 6 张")
    print("建议重新拍摄更多棋盘格照片")
    exit()

# =========================
# 4. 鱼眼标定
# =========================

K = np.zeros((3, 3))
D = np.zeros((4, 1))

rvecs = []
tvecs = []

flags = (
    cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC
    + cv2.fisheye.CALIB_CHECK_COND
    + cv2.fisheye.CALIB_FIX_SKEW
)

criteria = (
    cv2.TERM_CRITERIA_EPS
    + cv2.TERM_CRITERIA_MAX_ITER,
    100,
    1e-6
)

try:
    rms, K, D, rvecs, tvecs = cv2.fisheye.calibrate(
        objpoints,
        imgpoints,
        image_size,
        K,
        D,
        rvecs,
        tvecs,
        flags,
        criteria
    )

except cv2.error as e:
    print("\n标定失败！")
    print(e)
    print("\n可能原因：")
    print("1. 棋盘格角点数量设置错误")
    print("2. 有效照片太少")
    print("3. 棋盘格姿态变化不够")
    print("4. 照片质量较差")
    exit()

# =========================
# 5. 保存参数
# =========================

np.savez(
    PARAM_FILE,
    K=K,
    D=D,
    image_width=image_size[0],
    image_height=image_size[1],
    rms=rms
)

print("\n========== 标定完成 ==========")
print("RMS误差：", rms)

print("\n相机内参 K：")
print(K)

print("\n鱼眼畸变参数 D：")
print(D)

print("\n参数保存位置：")
print(PARAM_FILE)