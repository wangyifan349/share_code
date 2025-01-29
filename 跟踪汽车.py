import cv2
import numpy as np

# 加载YOLO模型
def load_yolo():
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return net, output_layers

# 检测汽车
def detect_cars(frame, net, output_layers):
    height, width = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)

    boxes = []
    confidences = []
    class_ids = []

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5 and class_id == 2:  # 2是汽车的类ID
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # 使用非极大值抑制（NMS）来消除重叠的边界框
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    detected_cars = []  # 创建一个空列表来存储检测到的汽车信息

    # 拆开列表推导式
    for i in indexes.flatten():  # 遍历非极大值抑制后的索引
        detected_cars.append((boxes[i], confidences[i]))  # 将边界框和置信度添加到结果列表中

    return detected_cars

# 主函数
def main():
    cap = cv2.VideoCapture("video.mp4")  # 替换为你的视频文件路径
    net, output_layers = load_yolo()

    trackers = cv2.MultiTracker_create()  # 创建一个多目标跟踪器

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if len(trackers.getObjects()) == 0:  # 如果没有跟踪器，进行检测
            detected_cars = detect_cars(frame, net, output_layers)
            for box, confidence in detected_cars:
                x, y, w, h = box
                trackers.add(cv2.TrackerKCF_create(), frame, (x, y, w, h))
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Car: {confidence:.2f}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        else:  # 如果有跟踪器，更新跟踪
            success, boxes = trackers.update(frame)
            for i, new_box in enumerate(boxes):
                x, y, w, h = [int(v) for v in new_box]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Car Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
