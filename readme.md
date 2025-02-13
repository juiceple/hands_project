# 조류 퇴치기 프로젝트

## 개요
본 프로젝트는 YOLO를 활용하여 새의 현재 위치를 분석하고, 해당 위치에 레이저를 쏘아 조류를 퇴치하는 시스템을 구축하는 것을 목표로 합니다.

### 주요 구성 요소
- **YOLO 모델**: 새의 위치를 분석 (노트북에서 로컬 실행)
- **라즈베리 파이**: 카메라 모듈을 이용하여 사진 촬영 및 데이터 전송
- **아두이노**: 분석된 좌표를 받아 레이저를 조절하여 조류 퇴치 수행

---
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
- 아두이노는 HC-06을 블루투스로 연결합니다.

### 2. 실행 명령어
1. **소프트웨어 및 라이브러리**
   ```bash
   pip install -r requirements.txt
   ```
   그리고 
2. **라즈베리 파이에서 촬영된 사진을 노트북으로 전송**
   ```bash
   python3 main.py
   ```
3. **라즈베리 파이에서 카메라 촬영 시작**
   ```bash
   python3 camera_controller.py
   ```
4. **노트북에서 시작**
   ```bash
   python main.py
   ```
---

## 발견된 오류
1. serial module 'serial' has no attribute 'Serial'
<br/>오류원인
  <br/> pyserial이 올바른 위치에 설치되지 않음
   해결방법
   ```bash
      python -m pip install --force-reinstall pyserial
   ```

## 폴더 설명

| 폴더명                  | 설명 |
|--------------------------|------------------------------------------------|
| `laptop`           | 노트북에서 실행되는 파일 |
| `arduino`  | 아두이노에서 실행되는 파일 |
| `incoming_images`               | 라즈베리 파이에서 이미지를 받아오는 파일 경로 |
| `final_model`       | 학습된 YOLO 모델을 저장하는 폴더 |
| `runs/detect`            | YOLO가 분석한 결과를 저장하는 폴더 |

## 파일 설명

| 파일명                  | 설명 |
|--------------------------|------------------------------------------------|
| `laptop/rasberry.py`           | 라즈베리 파이와 아두이노 간 통신 설정 |
| `rasberry/camera_controller.py`  | 카메라 모듈을 사용하여 일정 간격으로 사진 촬영 |
| `rasberry/main.py`               | 촬영된 사진을 노트북으로 자동 전송 |
| `laptop/monitor_real.py`       | `watchdog`을 활용하여 사진을 감지하고 YOLO 분석 실행 |
| `arduino/arduino.ino`            | 아두이노에서 분석된 좌표를 바탕으로 레이저 위치 및 각도 조정 |
| `main.py`            | rasberry.py와 monitor_real.py 한번에 실행행 |

---
## 요구 사항

- **하드웨어**
  - 라즈베리 파이 (카메라 모듈 포함)
  - 아두이노 (서보 모터 및 레이저 포함)
  - 노트북 (YOLO 실행 가능 환경)



  
---
## 참고 사항
- YOLO 모델은 로컬에서 실행되므로, 사전에 모델 파일을 다운로드하고 적절한 환경을 구성해야 합니다.
- `watchdog` 라이브러리는 폴더 내 사진 추가를 자동 감지하여 YOLO를 실행하도록 설정되어 있습니다.
- 라즈베리 파이와 노트북이 동일한 네트워크 내에 있어야 원활한 데이터 전송이 가능합니다.

---
## 프로젝트 목표 및 활용
본 프로젝트는 조류 피해를 방지하는 자동화 시스템으로, 농업, 공항, 발전소 등 다양한 분야에서 응용될 수 있습니다. 향후에는 실시간 영상 분석 및 AI 기반의 최적화된 조류 퇴치 알고리즘을 추가할 계획입니다.

# hands_project
