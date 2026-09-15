import OPi.GPIO as GPIO
import time

LED_PIN = 7
KEY_PIN = 5
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(KEY_PIN, GPIO.IN)

try:

    while True:
        value = GPIO.input(KEY_PIN) #检测电平函数
        print("按键电平 =", value)
        time.sleep(0.5)
        if GPIO.input(KEY_PIN) == 0:
            time.sleep(0.02)
            if GPIO.input(KEY_PIN)==0:
                GPIO.output(LED_PIN, not GPIO.input(LED_PIN))#灯电平反转
                print(f"灯")
        
except KeyboardInterrupt:
    print("\n用户中断")
finally:
    GPIO.cleanup()
    print("111")