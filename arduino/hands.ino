#include <Servo.h>
#include <Arduino.h>

Servo servoX;
Servo servoY;

// 서보 제어 및 각도 계산에 사용될 상수들
const float PHOTO_WIDTH  = 119.0;
const float PHOTO_HEIGHT = 63.0;
const float DIST_CENTER  = 115.0;
const float DIST_TOP     = 126.0;

const int BASE_X = 110;
const int BASE_Y = 0;

void setup() {
  // USB 시리얼 디버깅 및 통신용 초기화
  Serial.begin(9600);
  while (!Serial) {
    ; // USB 시리얼 연결 대기
  }
  Serial.println("Arduino Debugging Starting...");

  // 서보 초기화 (핀 번호는 필요에 따라 변경)
  servoX.attach(6);
  servoY.attach(9);
  servoX.write(BASE_X);
  servoY.write(BASE_Y);
  Serial.println("Servos attached. Initial positions set.");
}

void loop() {
  // USB 시리얼로부터 데이터가 들어오면 처리
  if (Serial.available() > 0) {
    // '\n'까지 문자열 전체를 읽음 (예: "0.22000,0.40000")
    String inputLine = Serial.readStringUntil('\n');
    inputLine.trim(); // 앞뒤 공백 제거
    Serial.print("Received raw data: ");
    Serial.println(inputLine);

    // 입력 문자열에서 콤마(,)의 위치 찾기
    int commaIndex = inputLine.indexOf(',');
    if (commaIndex == -1) {
      Serial.println("Error: Comma not found in input data. Skipping.");
      return;
    }
    
    // 콤마를 기준으로 좌표값 분리
    String strNormX = inputLine.substring(0, commaIndex);
    String strNormY = inputLine.substring(commaIndex + 1);
    float normX = strNormX.toFloat();
    float normY = strNormY.toFloat();

    Serial.print("Parsed normX: ");
    Serial.println(normX, 5);
    Serial.print("Parsed normY: ");
    Serial.println(normY, 5);

    // [x축 계산]
    float offsetX = (0.5 - normX) * PHOTO_WIDTH;
    float thetaX_rad = atan(offsetX / DIST_CENTER);
    float thetaX_deg = thetaX_rad * 180.0 / PI;
    int servoXPos = constrain(BASE_X + (int)thetaX_deg, 0, 180);

    // [y축 계산]
    float offsetY = normY * PHOTO_HEIGHT;
    float thetaY_rad = atan(offsetY / DIST_TOP);
    float thetaY_deg = thetaY_rad * 180.0 / PI;
    int servoYPos = constrain(110 - (int)thetaY_deg, 0, 180);

    Serial.print("Calculated servoXPos: ");
    Serial.println(servoXPos);
    Serial.print("Calculated servoYPos: ");
    Serial.println(servoYPos);

    // 서보 모터에 각도 전송
    servoX.write(servoXPos);
    servoY.write(servoYPos);
    Serial.println("Servo positions updated.");

    // 잠시 대기
    delay(20);
  }
}
