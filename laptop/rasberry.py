import os
import paramiko
import time

# 📌 라즈베리 파이 접속 정보 설정
RPI_HOST = "192.168.1.119"
RPI_USER = "hands"
RPI_PASSWORD = "314"
RPI_YOLO_DIR = "/home/hands/yolo_file"
LOCAL_SAVE_DIR = os.path.join(os.getcwd(), "incoming_images")
PHOTO_LIMIT = 5  # 로컬에 저장할 사진(파일) 개수 제한

# 📌 로컬 저장 폴더가 없으면 생성
if not os.path.exists(LOCAL_SAVE_DIR):
    os.makedirs(LOCAL_SAVE_DIR)
    print(f"로컬 폴더 생성됨: {LOCAL_SAVE_DIR}")

def delete_oldest_file(folder_path):
    """
    지정된 폴더 내 파일 중 가장 오래된 파일을 삭제합니다.
    """
    files = os.listdir(folder_path)
    if not files:
        return
    # 각 파일의 수정시간을 기준으로 가장 오래된 파일 찾기
    oldest_file = min(files, key=lambda f: os.path.getmtime(os.path.join(folder_path, f)))
    try:
        os.remove(os.path.join(folder_path, oldest_file))
        print(f"🗑️ 삭제됨: {oldest_file}")
    except Exception as e:
        print(f"파일 삭제 중 에러 발생: {e}")

# 📌 SSH 연결 및 SFTP 설정
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
sftp = None

try:
    client.connect(RPI_HOST, username=RPI_USER, password=RPI_PASSWORD)
    sftp = client.open_sftp()
    print("✅ 라즈베리 파이 SSH 연결 성공!")
    
    # 라즈베리파이 폴더의 기존 파일 목록 확인
    try:
        files = sftp.listdir(RPI_YOLO_DIR)
        print(f"라즈베리파이 폴더 {RPI_YOLO_DIR}의 파일 목록:")
        for file in files:
            print(f"- {file}")
    except Exception as e:
        print(f"폴더 읽기 오류: {e}")
        raise
    
    # 기존에 받은 파일 리스트 저장
    existing_files = set(files)
    print(f"\n모니터링 시작... Ctrl+C로 종료할 수 있습니다.")
    
    while True:
        try:
            # 라즈베리 파이의 최신 파일 목록 가져오기
            current_files = set(sftp.listdir(RPI_YOLO_DIR))
            
            # 새로 추가된 파일 확인
            new_files = current_files - existing_files
            
            if new_files:
                print(f"\n새로운 파일 발견: {new_files}")
                for file in new_files:
                    remote_path = f"{RPI_YOLO_DIR}/{file}"
                    local_path = os.path.join(LOCAL_SAVE_DIR, file)
                    
                    try:
                        # 파일 다운로드
                        sftp.get(remote_path, local_path)
                        print(f"📥 파일 다운로드 완료: {file}")
                    except Exception as e:
                        print(f"❌ 파일 다운로드 실패 ({file}): {e}")
                    
                    # 다운로드 후 로컬 저장 폴더의 파일 개수가 PHOTO_LIMIT 초과 시 삭제
                    local_files = os.listdir(LOCAL_SAVE_DIR)
                    while len(local_files) > PHOTO_LIMIT:
                        delete_oldest_file(LOCAL_SAVE_DIR)
                        local_files = os.listdir(LOCAL_SAVE_DIR)
            
            # 기존 파일 목록 업데이트
            existing_files = current_files
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n프로그램 종료 요청됨...")
            break
        except Exception as e:
            print(f"❌ 반복문 내 오류 발생: {e}")
            break

except Exception as e:
    print(f"❌ 연결 오류 발생: {e}")

finally:
    if sftp:
        sftp.close()
    client.close()
    print("🔌 SSH 연결 종료")
