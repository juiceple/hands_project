# sender.py
import cv2
import socket
import pickle
import struct
import time
from picamera2 import Picamera2

def start_streaming(host_ip='192.168.1.119', port=9999):
    # 소켓 서버 설정
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_address = (host_ip, port)
    server_socket.bind(socket_address)
    server_socket.listen(5)
    print(f"Listening at {socket_address}")

    # Picamera2 설정
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    time.sleep(2)  # 카메라 초기화 대기

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print('Connection from:', addr)
            try:
                while True:
                    # 프레임 캡처
                    frame = picam2.capture_array()
                    # BGR로 변환 (YOLO 분석을 위해)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    # 프레임 직렬화
                    data = pickle.dumps(frame)
                    # 프레임 크기 정보를 포함한 메시지 생성
                    message = struct.pack("Q", len(data)) + data
                    
                    try:
                        client_socket.sendall(message)
                    except:
                        break
                    
                    # 선택사항: 프레임 전송 간격 조절
                    time.sleep(0.03)  # ~30 FPS
                    
            except Exception as e:
                print(f"Streaming error: {e}")
            finally:
                client_socket.close()
                print("Client disconnected")
                
    except KeyboardInterrupt:
        print("Stopping server...")
    finally:
        picam2.stop()
        server_socket.close()
        print("Server closed")

if __name__ == "__main__":
    start_streaming()