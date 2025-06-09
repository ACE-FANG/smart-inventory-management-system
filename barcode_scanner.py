import cv2
from pyzbar.pyzbar import decode
from PIL import Image
import numpy as np

class BarcodeScanner:
    def __init__(self, camera_index=0):
        """
        初始化条形码扫描器
        :param camera_index: 摄像头索引，默认为0
        """
        self.camera = cv2.VideoCapture(camera_index)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.scanning = False
    
    def scan_barcode(self, timeout=30):
        """
        使用摄像头实时扫描条形码
        :param timeout: 超时时间（秒），默认30秒
        :return: 识别到的条形码字符串，超时返回None
        """
        self.scanning = True
        start_time = cv2.getTickCount()
        
        while self.scanning:
            # 检查超时
            elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
            if elapsed_time > timeout:
                break
            
            # 读取摄像头帧
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            # 转换为灰度图以提高识别效率
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 解码条形码
            decoded_objects = decode(gray)
            
            # 绘制识别结果
            for obj in decoded_objects:
                points = obj.polygon
                if len(points) > 4:
                    hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                    hull = list(map(tuple, np.squeeze(hull)))
                else:
                    hull = points
                
                # 绘制条形码边界
                n = len(hull)
                for j in range(0, n):
                    # 将点坐标转换为整数类型
                    p1 = (int(hull[j][0]), int(hull[j][1]))
                    p2 = (int(hull[(j + 1) % n][0]), int(hull[(j + 1) % n][1]))
                    cv2.line(frame, p1, p2, (0, 255, 0), 3)
                
                # 显示条形码数据
                barcode = obj.data.decode('utf-8')
                # 将坐标转换为整数类型
                org = (int(hull[0][0]), int(hull[0][1] - 10))
                cv2.putText(frame, barcode, org, 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # 显示摄像头画面
            cv2.imshow('Barcode Scanner - Press ESC to exit', frame)
            
            # 检测按键
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC键
                break
            elif key == 32:  # 空格键暂停/继续
                self.scanning = not self.scanning
                if self.scanning:
                    start_time = cv2.getTickCount()
            
            # 如果检测到条形码，返回结果
            if decoded_objects:
                barcode = decoded_objects[0].data.decode('utf-8')
                self.release_camera()
                cv2.destroyAllWindows()
                return barcode
        
        self.release_camera()
        cv2.destroyAllWindows()
        return None
    
    def read_barcode_from_image(self, image_path):
        """
        从图像文件中读取条形码
        :param image_path: 图像文件路径
        :return: 识别到的条形码字符串，未识别到返回None
        """
        try:
            image = Image.open(image_path)
            decoded_objects = decode(image)
            
            if decoded_objects:
                return decoded_objects[0].data.decode('utf-8')
            return None
        except Exception as e:
            print(f"Error reading barcode from image: {e}")
            return None
    
    def release_camera(self):
        """释放摄像头资源"""
        if self.camera.isOpened():
            self.camera.release()
    
    def __del__(self):
        """析构函数，确保释放资源"""
        self.release_camera()

if __name__ == "__main__":
    # 测试代码
    scanner = BarcodeScanner()
    
    print("选择扫描模式:")
    print("1. 摄像头扫描")
    print("2. 图片文件扫描")
    choice = input("请输入选项 (1/2): ")
    
    if choice == '1':
        print("请将条形码对准摄像头...")
        barcode = scanner.scan_barcode()
        if barcode:
            print(f"识别到的条形码: {barcode}")
        else:
            print("未识别到条形码")
    elif choice == '2':
        file_path = input("请输入图片文件路径: ")
        barcode = scanner.read_barcode_from_image(file_path)
        if barcode:
            print(f"识别到的条形码: {barcode}")
        else:
            print("未识别到条形码")
    else:
        print("无效选项")