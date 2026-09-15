import serial
import time

ser = serial.Serial(
    port="/dev/ttyS6",
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.1
)

print("串口打开成功")

try:
    while True:
        # 发送
        ser.write(b"Hello Orange Pi!\r\n")
        print("发送：Hello Orange Pi!")

        # 接收
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            print("收到：", data)

        time.sleep(1)

except KeyboardInterrupt:
    print("\n用户中断")

finally:
    ser.close()
    print("串口关闭")