
#include <Servo.h>
#include <Arduino.h>

Servo servoX; 
Servo servoY; 

float PHOTO_WIDTH   = 119.0;  
float PHOTO_HEIGHT  = 63.0;   
float DIST_CENTER   = 115.0;  
float DIST_TOP      = 126.0;  

int BASE_X = 110;    
int BASE_Y = 0;  

void setup() {
  Serial.begin(9600);
  servoX.attach(6);   
  servoY.attach(9);  
  servoX.write(BASE_X);
  servoY.write(BASE_Y);
}

void loop() {
  if (Serial.available() > 0) {
    float normX = Serial.parseFloat();  // 0 ~ 1 사이의 값 (x 좌표)
    if (Serial.read() != ',') {        
      return;     }
    float normY = Serial.parseFloat();  // 0 ~ 1 사이의 값 (y 좌표)

    // [x축 계산]
    float offsetX = (0.5 - normX) * PHOTO_WIDTH;
    float thetaX_rad = atan(offsetX / DIST_CENTER);
    float thetaX_deg = thetaX_rad * 180.0 / PI;
    int servoXPos = constrain(BASE_X + (int)thetaX_deg, 0, 180);

    // [y축 계산]
    // (0.5 - normY): normY가 0이면 사진 상단, 1이면 사진 하단
    float offsetY = (normY) * PHOTO_HEIGHT;
    int servoYPos;
    float thetaY_rad = atan(offsetY / DIST_TOP);
    float thetaY_deg = thetaY_rad * 180.0 / PI;
    servoYPos = constrain(110-(int)thetaY_deg, 0, 180); 
    
    servoX.write(servoXPos);
    servoY.write(servoYPos);

    Serial.print("normX: "); Serial.print(normX);
    Serial.print(" normY: "); Serial.print(normY);
    Serial.print(" -> servoX: "); Serial.print(servoXPos);
    Serial.print(" servoY: "); Serial.println(servoYPos);
    
    delay(20);  // 짧은 지연
  }
}