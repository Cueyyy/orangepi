import cv2
import time

cap = cv2.VideoCapture("/dev/video1", cv2.CAP_V4L2)

if not cap.isOpened():
    raise RuntimeError("摄像头打开失败")

# 初始化时间变量
prev_time = time.time()
try:
    while True:
        # 记录当前帧开始时间
        curr_time = time.time()
        # 计算 FPS（防止除以0）
        fps = 1.0 / (curr_time - prev_time) if curr_time > prev_time else 0.0
        prev_time = curr_time

        ret, frame = cap.read()

        if not ret:
            print("读取失败")
            continue
        
        
        # 转换为灰度图像 高斯模糊
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray_frame, (5, 5), 0)
        # HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #  阈值（二值化）
        _, binary = cv2.threshold(gray_frame, 127, 255, cv2.THRESH_BINARY)
        # 形态学操作（开运算去噪）
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        morphology = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        # 轮廓检测
        contours, _ = cv2.findContours(morphology, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour_img = frame.copy()
        cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 2)

        height, width = gray_frame.shape[:2]
        center_x = width // 2
        center_y = height // 2
        # 绘制十字准星

        cv2.line(
            frame,
            (center_x - 30, center_y),
            (center_x + 30, center_y),
            (0, 255, 0),
            2,
        )
        cv2.line(
            frame,
            (center_x, center_y - 30),
            (center_x, center_y + 30),
            (0, 255, 0),
            2,
        )

        # 绘制分辨率文字
        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX, # 字体
            0.5,                        # 字体大小
            (255, 0, 0),              # 字体颜色
            1,                        # 字体粗细
        )

        cv2.imshow("vision test", contour_img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()

