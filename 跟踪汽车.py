import cv2
import numpy as np

# 加载YOLO模型
def load_yolo():
    # 读取YOLOv4的权重和配置文件
    net = cv2.dnn.readNet("yolov4.weights", "yolov4.cfg")  # 使用YOLOv4
    # 获取网络的所有层名称
    layer_names = net.getLayerNames()
    # 获取输出层的名称
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return net, output_layers

# 检测汽车
def detect_cars(frame, net, output_layers):
    # 获取当前帧的高度和宽度
    height, width = frame.shape[:2]
    # 将图像转换为YOLO模型所需的输入格式
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    # 将blob作为输入传递给网络
    net.setInput(blob)
    # 前向传播，获取输出
    outputs = net.forward(output_layers)

    # 初始化边界框、置信度和类ID的列表
    boxes = []
    confidences = []
    class_ids = []

    # 遍历每个输出
    for output in outputs:
        for detection in output:
            # 获取检测结果的置信度分数
            scores = detection[5:]
            # 获取置信度最高的类ID
            class_id = np.argmax(scores)
            # 获取该类的置信度
            confidence = scores[class_id]
            # 只考虑置信度高于0.5且类ID为2（汽车）的检测结果
            if confidence > 0.5 and class_id == 2:  # 2是汽车的类ID
                # 计算边界框的中心坐标和宽高
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # 计算左上角的坐标
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                # 将边界框、置信度和类ID添加到列表中
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # 使用非极大值抑制（NMS）来消除重叠的边界框
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    detected_cars = []  # 创建一个空列表来存储检测到的汽车信息

    # 遍历非极大值抑制后的索引
    for i in indexes.flatten():
        detected_cars.append((boxes[i], confidences[i]))  # 将边界框和置信度添加到结果列表中

    return detected_cars

# 主函数
def main():
    # 打开视频文件
    cap = cv2.VideoCapture("video.mp4")  # 替换为你的视频文件路径
    # 加载YOLO模型和输出层
    net, output_layers = load_yolo()

    # 创建一个多目标跟踪器
    trackers = cv2.MultiTracker_create()

    # 循环读取视频帧
    while True:
        ret, frame = cap.read()  # 读取一帧
        if not ret:  # 如果没有读取到帧，退出循环
            break

        # 如果没有跟踪器，进行检测
        if len(trackers.getObjects()) == 0:
            detected_cars = detect_cars(frame, net, output_layers)  # 检测汽车
            for box, confidence in detected_cars:
                x, y, w, h = box  # 获取边界框的坐标和大小
                # 添加新的跟踪器
                trackers.add(cv2.TrackerKCF_create(), frame, (x, y, w, h))
                # 在图像上绘制边界框
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # 在边界框上方显示置信度
                cv2.putText(frame, f"Car: {confidence:.2f}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        else:  # 如果有跟踪器，更新跟踪
            success, boxes = trackers.update(frame)  # 更新所有跟踪器
            for i, new_box in enumerate(boxes):
                x, y, w, h = [int(v) for v in new_box]  # 获取新的边界框坐标
                # 在图像上绘制更新后的边界框
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 显示当前帧
        cv2.imshow("Car Tracking", frame)
        # 按下 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放视频捕捉对象和关闭所有窗口
    cap.release()
    cv2.destroyAllWindows()

# 程序入口
if __name__ == "__main__":
    main()
