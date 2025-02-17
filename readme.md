

# 조류 퇴치기 프로젝트

## 개요
본 프로젝트는 YOLO를 활용하여 새의 현재 위치를 분석하고, 해당 위치에 레이저를 쏘아 조류를 퇴치하는 시스템을 구축하는 것을 목표로 합니다.

### 주요 구성 요소
- **YOLO 모델**: 새의 위치를 분석 (노트북에서 로컬 실행)
- **라즈베리 파이**: 카메라 모듈을 이용하여 사진 촬영 및 데이터 전송
- **아두이노**: 분석된 좌표를 받아 레이저를 조절하여 조류 퇴치 수행

---

## 시연 영상
<!-- YouTube 시연영상 임베드 (시작 시간 19초부터) -->
<iframe width="560" height="315" src="https://www.youtube.com/embed/H2yaHJI-CNM?start=19" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## 시스템 작동 과정

1. **통신 연결**: 컴퓨터와 아두이노 간 통신을 설정합니다. (`rasberry.py` 실행)
2. **사진 촬영**: 라즈베리 파이의 카메라 모듈을 활용하여 1초마다 한 번씩 사진을 촬영합니다. (`camera_controller.py` 실행)
3. **사진 저장**: 촬영된 사진이 자동으로 라즈베리 파이 및 노트북에 저장됩니다.
4. **YOLO 분석**: 새로운 사진이 감지되면 `watchdog`을 이용하여 자동으로 분석하고, 결과를 `.txt` 파일로 저장합니다. (`monitor_real.py` 실행)
5. **좌표 전송 및 조작**: YOLO 분석 결과를 아두이노로 전달하여, 아두이노가 레이저 위치 및 각도를 조정합니다.

---

## 실행 절차

### 1. 초기 설정
- 라즈베리 파이의 전원을 켭니다.
- 아두이노는 그냥 usb로 연결한 후 장치 관리자에서 COM3로 잘 연결됐는지 확인합니다. 아두이노 IDE를 활용해서 arduino 내 hands.ino 파일을 컴파일 후 업로드합니다.

### 2. 실행 명령어
1. **소프트웨어 및 라이브러리**
   ```bash
   pip install -r requirements.txt
