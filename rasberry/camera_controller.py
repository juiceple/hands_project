import tkinter as tk           # GUI 구성
import threading               # 촬영 프로세스를 백그라운드 스레드로 실행하기 위함
import os                      # 파일 및 폴더 작업
import time                    # 시간 관련 함수 사용 (파일명 생성, 대기)
from picamera2 import Picamera2  # Raspberry Pi Camera Module 3 제어 (picamera2 라이브러리)

# 전역 변수: 촬영 진행 여부
running = False
capture_thread = None  # 촬영 스레드를 담을 변수

def capture_loop():
    """
    촬영 프로세스: 
    - yolo_file 폴더가 없으면 생성
    - Picamera2 객체 생성 및 설정 후 카메라 시작
    - running 플래그가 True인 동안 2초 간격으로 이미지 촬영
    - 촬영된 이미지는 yolo_file에 저장되고, 파일 수가 5장을 초과하면 가장 오래된 파일 삭제
    - running이 False가 되면 카메라를 중지하고 프로세스 종료
    """
    global running

    # 저장 디렉터리 생성 (없으면 생성)
    output_dir = "yolo_file"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"디렉터리 '{output_dir}' 생성됨.")

    # Picamera2 초기화 및 정지(still) 촬영 설정 구성
    picam2 = Picamera2()
    config = picam2.create_still_configuration()
    picam2.configure(config)
    picam2.start()
    print("카메라 시작됨.")

    while running:
        # 현재 시각을 이용해 고유 파일명 생성 (예: image_20250208_153045.jpg)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"image_{timestamp}.jpg")

        # 이미지 촬영 및 파일 저장
        picam2.capture_file(filename)
        print(f"이미지 촬영 및 저장됨: {filename}")

        # 저장된 이미지 파일 목록 가져오기 (.jpg 파일만) 및 수정시간 기준 정렬
        files = sorted(
            [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.jpg')],
            key=os.path.getmtime
        )

        # 파일 개수가 5장을 초과하면 가장 오래된 파일 삭제
        if len(files) > 5:
            os.remove(files[0])
            print(f"최대 파일 수 초과로 인해 삭제됨: {files[0]}")

        # 2초 대기 후 다음 촬영
        time.sleep(2)

    # running이 False가 되면 카메라 정지
    picam2.stop()
    print("카메라 중지됨.")

def start_capture():
    """
    Start 버튼 클릭 시 호출되는 함수:
    - 전역 running 플래그를 True로 설정하고, 촬영 스레드를 시작
    - 이미 촬영이 진행 중이면 중복 실행되지 않도록 처리
    """
    global running, capture_thread
    if not running:
        running = True
        capture_thread = threading.Thread(target=capture_loop, daemon=True)
        capture_thread.start()
        print("촬영 스레드 시작됨.")

def stop_capture():
    """
    Stop 버튼 클릭 시 호출되는 함수:
    - 전역 running 플래그를 False로 설정하여 촬영 프로세스를 종료
    """
    global running
    running = False
    print("촬영 중지 요청됨.")

# tkinter GUI 구성
root = tk.Tk()
root.title("카메라 제어")

# Start 버튼 생성 및 배치
start_button = tk.Button(root, text="Start", width=15, command=start_capture)
start_button.pack(pady=10)

# Stop 버튼 생성 및 배치
stop_button = tk.Button(root, text="Stop", width=15, command=stop_capture)
stop_button.pack(pady=10)

# tkinter 이벤트 루프 시작
root.mainloop()
