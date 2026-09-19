import cv2
import os

# 摄像头编号
CAMERA_ID = 1

# 保存照片的文件夹
SAVE_DIR =  "/home/orangepi/Desktop/test_base/senor/pic"

os.makedirs(SAVE_DIR, exist_ok=True)

cap = cv2.VideoCapture(CAMERA_ID)

if not cap.isOpened():
    print("摄像头打开失败！")
    exit()

# 可以根据实际情况修改分辨率
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

count = 0

print("按空格拍照，按 q 退出")

while True:
    ret, frame = cap.read()

    if not ret:
        print("读取摄像头失败")
        break

    cv2.imshow("Camera", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord(' '):
        filename = os.path.join(
            SAVE_DIR, f"calib_{count:02d}.jpg"
        )
        cv2.imwrite(filename, frame)
        print("已保存：", filename)
        count += 1

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("一共拍摄了", count, "张照片")