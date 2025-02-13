import time
import os
from picamera2 import Picamera2
from PIL import Image

def main():
    # 이미지 저장 폴더 생성 (없으면 생성)
    output_dir = "yolo_file"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"디렉터리 '{output_dir}' 생성됨.")
    
    # Picamera2 초기화 및 시작 (메인 스레드에서 실행)
    try:
        picam2 = Picamera2()
        config = picam2.create_still_configuration()
        picam2.configure(config)
        picam2.start()
        print("카메라 시작됨.")
    except Exception as e:
        print("카메라 초기화 오류:", e)
        return

    try:
        while True:
            # 현재 시각 기반의 고유 파일명 생성
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(output_dir, f"image_{timestamp}.jpg")
            
            try:
                # 이미지 캡처 (numpy array 형태) 후 PIL 이미지로 변환하여 저장
                arr = picam2.capture_array()
                img = Image.fromarray(arr)
                img.save(filename)
                print(f"이미지 촬영 및 저장됨: {filename}")
            except Exception as capture_err:
                print("이미지 촬영 오류:", capture_err)
            
            # 저장된 이미지 관리: 파일 개수가 5장을 초과하면 가장 오래된 파일 삭제
            files = sorted(
                [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.jpg')],
                key=os.path.getmtime
            )
            if len(files) > 5:
                os.remove(files[0])
                print(f"최대 파일 수 초과로 인해 삭제됨: {files[0]}")
            
            # 2초 대기 후 다음 촬영
            time.sleep(2)
    except KeyboardInterrupt:
        print("촬영 중지됨.")
    finally:
        picam2.stop()
        print("카메라 중지됨.")

if __name__ == "__main__":
    main()
