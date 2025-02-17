import time
import os
import threading
import cv2
import numpy as np
import serial
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ultralytics import YOLO

###########################
# 1. 아두이노 시리얼 연결 설정 
###########################
SERIAL_PORT = "COM3"  # 환경에 맞게 수정 (예: Linux는 '/dev/ttyUSB0')
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"[시리얼] 아두이노와 {SERIAL_PORT} 포트로 연결되었습니다.")
except Exception as e:
    print(f"[시리얼] 시리얼 포트 연결 오류: {e}")
    ser = None

###########################
# 2. 모델 초기화 (이미지 예측용)
###########################
model = YOLO("final_model/weights/best.pt")

###########################
# 3. 폴더 경로 설정
###########################
IMAGE_WATCH_FOLDER = "incoming_images"
PARENT_FOLDER = "runs/detect"

if not os.path.exists(IMAGE_WATCH_FOLDER):
    os.makedirs(IMAGE_WATCH_FOLDER)
if not os.path.exists(PARENT_FOLDER):
    os.makedirs(PARENT_FOLDER)

###########################
# 4. 유틸리티 함수: 이미지 유효성 체크
###########################
def is_valid_image(path, retries=3, delay=0.5):
    for i in range(retries):
        img = cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR)
        if img is not None:
            return True
        print(f"[이미지 체크] 이미지 읽기 실패 (재시도 {i+1}/{retries}): {path}")
        time.sleep(delay)
    return False

###########################
# 5. 이미지 예측 모니터링 이벤트 핸들러
###########################
class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"[이미지 모니터링] 새 이미지 발견: {event.src_path}")
            threading.Timer(1.0, self.process_image, args=[event.src_path]).start()
    
    def process_image(self, image_path):
        try:
            file_size = os.path.getsize(image_path)
        except Exception as e:
            print(f"[이미지 모니터링] 파일 크기 확인 중 에러: {e}")
            return

        if file_size == 0:
            print("[이미지 모니터링] 파일이 비어 있습니다. 건너뜁니다.")
            return

        if not is_valid_image(image_path, retries=3, delay=0.5):
            print(f"[이미지 모니터링] 유효하지 않은 이미지 파일: {image_path}")
            return

        try:
            # YOLO 예측 실행 전 시간 측정 시작
            start_time = time.time()
            results = model.predict(source=image_path, conf=0.5, save=True, save_txt=True)
            # YOLO 예측 실행 후 시간 측정 종료
            elapsed_time = time.time() - start_time
            print(f"[시간 측정] YOLO 분석에 걸린 시간: {elapsed_time:.3f}초")
            
            for result in results:
                annotated_img = result.plot()
                cv2.imshow("Prediction", annotated_img)
                cv2.waitKey(1000)
                cv2.destroyWindow("Prediction")
                print("[이미지 모니터링] 예측 결과 (xywh):", result.boxes.xywh)
                print("[이미지 모니터링] 예측 결과 (confidence):", result.boxes.conf)
                print("[이미지 모니터링] 예측 결과 (class):", result.boxes.cls)
        except Exception as e:
            print(f"[이미지 모니터링] 예측 실행 중 에러: {e}")

###########################
# 6. 텍스트 파일 감지 및 아두이노 전송 (recursive)
###########################
class TxtRecursiveHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.txt'):
            print(f"[텍스트 모니터링] 새 txt 파일 발견: {event.src_path}")
            time.sleep(0.5)
            try:
                with open(event.src_path, "r") as f:
                    content = f.read().strip()
                print(f"[텍스트 모니터링] 원본 파일 내용: {content}")
                
                tokens = content.split()
                if len(tokens) < 3:
                    print("[텍스트 모니터링] 예상 형식이 아닙니다.")
                    return
                normX = tokens[1]
                normY = tokens[2]
                
                command = f"{normX},{normY}\n"
                self.send_to_arduino(command)
            except Exception as e:
                print(f"[텍스트 모니터링] txt 파일 읽기 오류: {e}")
    
    def send_to_arduino(self, command):
        if ser:
            try:
                ser.write(command.encode('utf-8'))
                print(f"[텍스트 모니터링] 아두이노로 전송: {command.strip()}")
            except Exception as e:
                print(f"[텍스트 모니터링] 아두이노 전송 오류: {e}")
        else:
            print("[텍스트 모니터링] 아두이노 시리얼 연결이 설정되지 않았습니다.")

###########################
# 7. Observer들을 동시에 실행
###########################
if __name__ == "__main__":
    image_handler = ImageHandler()
    image_observer = Observer()
    image_observer.schedule(image_handler, path=IMAGE_WATCH_FOLDER, recursive=False)
    image_observer.start()
    print(f"[시작] 이미지 폴더 '{IMAGE_WATCH_FOLDER}' 모니터링 시작.")

    txt_recursive_handler = TxtRecursiveHandler()
    txt_observer = Observer()
    txt_observer.schedule(txt_recursive_handler, path=PARENT_FOLDER, recursive=True)
    txt_observer.start()
    print(f"[시작] '{PARENT_FOLDER}' 및 하위 폴더 전체에 대해 텍스트 파일 모니터링 시작 (recursive=True).")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[종료] 모니터링 종료 중...")
        image_observer.stop()
        txt_observer.stop()
    image_observer.join()
    txt_observer.join()
    if ser:
        ser.close()
