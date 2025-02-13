import os
import paramiko
import time


RPI_HOST = "192.168.1.119"
RPI_USER = "hands"
RPI_PASSWORD = "314"
RPI_YOLO_DIR = "/home/hands/yolo_file"
LOCAL_SAVE_DIR = "C:/yolo_file_note"


if not os.path.exists(LOCAL_SAVE_DIR):
    os.makedirs(LOCAL_SAVE_DIR)
    print(f"로컬 폴더 생성됨: {LOCAL_SAVE_DIR}")


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
sftp = None

try:
    client.connect(RPI_HOST, username=RPI_USER, password=RPI_PASSWORD)
    sftp = client.open_sftp()
    print(" 라즈베리 파이 SSH 연결 성공!")
    
    
    try:
        files = sftp.listdir(RPI_YOLO_DIR)
        print(f"라즈베리파이 폴더 {RPI_YOLO_DIR}의 파일 목록:")
        for file in files:
            print(f"- {file}")
    except Exception as e:
        print(f"폴더 읽기 오류: {e}")
        raise
    
    # 📌 기존에 받은 파일 리스트 저장
    existing_files = set(files)
    print(f"\n모니터링 시작... Ctrl+C로 종료할 수 있습니다.")
    
    while True:
        try:
            
            current_files = set(sftp.listdir(RPI_YOLO_DIR))
            
            
            new_files = current_files - existing_files
            
            if new_files:
                print(f"\n새로운 파일 발견: {new_files}")
                for file in new_files:
                    remote_path = f"{RPI_YOLO_DIR}/{file}"
                    local_path = os.path.join(LOCAL_SAVE_DIR, file)
                    
                    try:
                        
                        sftp.get(remote_path, local_path)
                        print(f" 파일 다운로드 완료: {file}")
                    except Exception as e:
                        print(f" 파일 다운로드 실패 ({file}): {e}")
            
            # 기존 파일 목록 업데이트
            existing_files = current_files
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n프로그램 종료 요청됨...")
            break
        except Exception as e:
            print(f" 반복문 내 오류 발생: {e}")
            break

except Exception as e:
    print(f" 연결 오류 발생: {e}")

finally:
    if sftp:
        sftp.close()
    client.close()
    print(" SSH 연결 종료")