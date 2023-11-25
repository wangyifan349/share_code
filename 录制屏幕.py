import cv2
import numpy as np
import pyautogui
import pygetwindow as gw

# 获取屏幕尺寸
screen_size = pyautogui.size()

# 定义编解码器并创建VideoWriter对象
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, screen_size)

while True:
    # 截取屏幕内容
    img = pyautogui.screenshot()
    # 转换颜色从BGR到RGB
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # 写入帧
    out.write(frame)
    # 显示录制的屏幕
    cv2.imshow('screen', frame)
    # 如果按下'q'键，则退出循环
    if cv2.waitKey(1) == ord('q'):
        break
# 释放VideoWriter对象
out.release()
# 关闭所有OpenCV窗口
cv2.destroyAllWindows()
