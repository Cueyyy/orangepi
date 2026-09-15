import OPi.GPIO as GPIO
import time

LED_PIN = 7

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    for i in range(10):
        GPIO.output(LED_PIN, GPIO.HIGH)
        print(f"第 {i+1} 次：LED ON")
        time.sleep(0.5)
        GPIO.output(LED_PIN, GPIO.LOW)
        print(f"第 {i+1} 次：LED OFF")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\n用户中断")
finally:
    GPIO.cleanup()
    print("GPIO 清理完成")