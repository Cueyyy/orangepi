import cv2
import time


CAMERA_DEVICE = "/dev/video1"
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FRAME_FPS = 30


def open_camera(device): # 打开摄像头
    # USB 摄像头通常使用 V4L2 后端
    cap = cv2.VideoCapture(device, cv2.CAP_V4L2)

    # 如果 V4L2 后端打开失败，再让 OpenCV 自动选择后端
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(device)

    if not cap.isOpened():
        raise RuntimeError(f"无法打开摄像头: {d8evice}")

    # MJPG 可以减少 USB 摄像头传输带宽
    # 但摄像头必须支持 MJPG，否则该设置可能不会生效
    cap.set(
        cv2.CAP_PROP_FOURCC,
        cv2.VideoWriter_fourcc(*"MJPG")
    )

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FRAME_FPS)

    # 尽量只保留较新的帧，降低延迟
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)

    print(
        f"摄像头已打开: {device}, "
        f"{actual_width}x{actual_height}, "
        f"{actual_fps:.1f} FPS"
    )

    return cap

def picture(device): # 拍照
    cap = cv2.VideoCapture(device, cv2.CAP_V4L2)

    if not cap.isOpened():
        raise RuntimeError("摄像头打开失败")

    ret, frame = cap.read()

    if ret:
        cv2.imwrite("/home/orangepi/test.jpg", frame)
        print("图片已保存到 /home/orangepi/test.jpg")
    else:
        print("读取图像失败")

    cap.release()    

def video(): # 录制视频
    cap = cv2.VideoCapture(CAMERA_DEVICE, cv2.CAP_V4L2)
   # 如果 V4L2 后端打开失败，再让 OpenCV 自动选择后端
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(CAMERA_DEVICE)
    if not cap.isOpened():
        raise RuntimeError("无法打开摄像头")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    out = cv2.VideoWriter("/home/orangepi/test.avi", fourcc, FRAME_FPS, (FRAME_WIDTH, FRAME_HEIGHT))

    print("开始录制，按 Ctrl+C 停止")

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("读取图像失败")
                continue

            out.write(frame)

    except KeyboardInterrupt:
        print("录制结束")

    finally:
        cap.release()
        out.release()
        print("视频已保存为 /home/orangepi/test.avi")

def main():
    # video()
    cap = open_camera(CAMERA_DEVICE)
    # cap = picture(CAMERA_DEVICE)
    try:
        while True:
            ret, frame = cap.read()
        #cap.read()返回值为(ret, frame)，ret为bool类型，frame为numpy数组
        # ret 为 True 表示读取成功，否则为 False
            if not ret:
                print("读取图像失败")
                time.sleep(0.01)
                continue

            # frame 是 OpenCV 的 BGR 图像
            cv2.imshow("camera", frame)

            # 按 q 退出
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("摄像头已释放")


if __name__ == "__main__":
    main()