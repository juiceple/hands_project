import multiprocessing
import subprocess
import time

# 실행할 스크립트 파일 경로
RASPBERRY_SCRIPT = "laptop/rasberry.py"
MONITOR_SCRIPT = "laptop/monitor_real.py"

def run_script(script_name):
    """지정된 Python 스크립트를 실행"""
    try:
        subprocess.run(["python", script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ {script_name} 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    # 두 개의 프로세스를 실행
    raspberry_process = multiprocessing.Process(target=run_script, args=(RASPBERRY_SCRIPT,))
    monitor_process = multiprocessing.Process(target=run_script, args=(MONITOR_SCRIPT,))

    # 프로세스 시작
    raspberry_process.start()
    monitor_process.start()

    try:
        while True:
            time.sleep(1)  # 메인 프로세스 유지
    except KeyboardInterrupt:
        print("\n[종료] 모든 프로세스를 종료합니다...")

        # 프로세스 종료
        raspberry_process.terminate()
        monitor_process.terminate()

        raspberry_process.join()
        monitor_process.join()

    print("🔌 모든 프로세스 종료 완료.")
