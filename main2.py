import cv2
import time
from ultralytics import YOLO
import serial
import numpy as np

#####################################
# 1. 아두이노 시리얼 연결 설정
#####################################
SERIAL_PORT = "COM4"  # 환경에 맞게 수정 (예: Linux는 '/dev/ttyUSB0')
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"[시리얼] 아두이노와 {SERIAL_PORT} 포트로 연결되었습니다.")
except Exception as e:
    print(f"[시리얼] 시리얼 포트 연결 오류: {e}")
    ser = None

#####################################
# 2. YOLO 모델 초기화
#####################################
# (Ultralytics YOLO v8 사용, 모델 경로 및 가중치 파일 설정)
model = YOLO("final_model/weights/best.pt")

#####################################
# 3. 라즈베리 파이 스트리밍 URL 설정
#####################################
# 라즈베리 파이에서 mjpg-streamer와 같은 스트리밍 서버가 실행 중이어야 합니다.
RPI_STREAM_URL = "http://192.168.1.119:8080/?action=stream"

#####################################
# 4. 아두이노 전송용 함수: 텍스트 결과에서 두번째와 세번째 토큰 전송
#####################################
def send_detection_to_arduino(result, frame_shape):
    """
    검출된 객체 중 첫 번째 결과의 bounding box 정보를 텍스트 형식으로 생성하고,
    두 번째(즉, x_center)와 세 번째(즉, y_center)를 추출하여 아두이노로 전송합니다.
    
    여기서는 별도의 정규화 연산 없이 YOLO 결과에 포함된 x_center와 y_center 값을 그대로 사용합니다.
    """
    if ser is None:
        print("[아두이노] 시리얼 연결이 설정되지 않음.")
        return

    try:
        # result.boxes.xywh: [x_center, y_center, width, height] 정보를 담은 텐서
        boxes = result.boxes.xywh.cpu().numpy()  # shape: (N, 4)
        # 클래스 정보가 있다면 추출 (없으면 0으로 처리)
        classes = result.boxes.cls.cpu().numpy() if hasattr(result.boxes, "cls") else None
    except Exception as e:
        print(f"[아두이노] 박스 추출 오류: {e}")
        return

    if len(boxes) == 0:
        return  # 검출 결과가 없으면 전송하지 않음

    # 첫 번째 검출 결과 사용
    x_center, y_center, width, height = boxes[0]
    cls_num = int(classes[0]) if classes is not None else 0

    # 텍스트 형식: "클래스번호 x_center y_center width height"
    detection_str = f"{cls_num} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
    print("[디텍션 문자열]", detection_str)

    # 문자열에서 두 번째와 세 번째 토큰 (x_center, y_center) 추출
    tokens = detection_str.split()
    if len(tokens) < 3:
        print("[아두이노 전송] 토큰 추출 실패")
        return

    # "x_center,y_center\n" 형식으로 아두이노에 전송
    command = f"{tokens[1]},{tokens[2]}\n"
    
    try:
        ser.write(command.encode('utf-8'))
        print(f"[아두이노 전송] {command.strip()}")
    except Exception as e:
        print(f"[아두이노 전송 오류] {e}")

#####################################
# 5. 실시간 스트리밍 및 YOLO 예측 함수
#####################################
def process_stream():
    # OpenCV의 VideoCapture를 사용해 라즈베리 파이 스트림에 연결
    cap = cv2.VideoCapture(RPI_STREAM_URL)
    if not cap.isOpened():
        print("비디오 스트림 열기 실패. 스트리밍 서버가 실행 중인지 확인하세요.")
        return
    
    print("비디오 스트림 연결 성공!")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("프레임 읽기 실패, 재시도 중...")
            time.sleep(0.1)
            continue

        # YOLO 모델을 사용하여 현재 프레임에 대한 객체 검출 수행
        try:
            results = model.predict(source=frame, conf=0.5)
        except Exception as e:
            print(f"[YOLO 오류] 예측 실행 중 에러: {e}")
            results = None

        if results:
            result = results[0]
            try:
                annotated_frame = result.plot()  # 검출 결과를 시각화한 이미지
            except Exception as e:
                print(f"[YOLO 오류] 결과 시각화 중 에러: {e}")
                annotated_frame = frame.copy()
            
            # 아두이노로 x_center와 y_center 전송
            send_detection_to_arduino(result, frame.shape)
        else:
            annotated_frame = frame.copy()
        
        cv2.imshow("YOLO 실시간 예측", annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

#####################################
# 6. 메인 실행부
#####################################
if __name__ == "__main__":
    process_stream()
    if ser:
        ser.close()
