#include <Encoder.h>

const int pinEncA = 3;
const int pinEncB = 2;
const int pinMotorDir1 = 4;
const int pinMotorDir2 = 5;
const int pinMotorPWM = 6;

Encoder myEnc(pinEncA, pinEncB);

long targetPosition = 0;
long currentPosition = 0;
long lastReportedPosition = -999;
bool isMoving = false;
int tolerance = 10;

int maxSpeed = 255;
int minSpeed = 60;
long brakingDistance = 600;

void setup() {
  Serial.begin(115200);
  pinMode(pinMotorDir1, OUTPUT);
  pinMode(pinMotorDir2, OUTPUT);
  pinMode(pinMotorPWM, OUTPUT);
  Serial.println("READY");
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.startsWith("GOTO ")) {
      targetPosition = cmd.substring(5).toInt();
      isMoving = true;
      Serial.print("TARGET:");
      Serial.println(targetPosition);
    } else if (cmd == "STOP") {
      isMoving = false;
      stopMotor();
      Serial.println("STOPPED");
    } else if (cmd == "ZERO") {
      myEnc.write(0);
      targetPosition = 0;
      isMoving = false;
      stopMotor();
      Serial.println("ZEROED");
    } else if (cmd.startsWith("SETPOS ")) {
      long newPos = cmd.substring(7).toInt();
      myEnc.write(newPos);
      currentPosition = newPos;
      targetPosition = newPos;
      Serial.print("SYNCED_TO:");
      Serial.println(newPos);
    } else if (cmd.startsWith("POSNOW:")) {
      currentPosNow();
    }
  }

  currentPosition = myEnc.read();

  if (abs(currentPosition - lastReportedPosition) > 10) {
    Serial.print("POS:");
    Serial.println(currentPosition);
    lastReportedPosition = currentPosition;
  }

  if (isMoving) {
    long error = targetPosition - currentPosition;
    long absError = abs(error);

    if (absError <= tolerance) {
      stopMotor();
      isMoving = false;
      Serial.print("CALL:");
      Serial.println(currentPosition);
      delay(500);
      Serial.print("POSNOW:");
      Serial.println(currentPosition);

    } else {
      int speed;
      if (absError > brakingDistance) {
        speed = maxSpeed;
      } else {
        speed = map(absError, tolerance, brakingDistance, minSpeed, maxSpeed);
      }
      speed = constrain(speed, minSpeed, maxSpeed);
      if (error > 0) {
        moveMotor(speed, true);
      } else {
        moveMotor(speed, false);
      }
    }
  }
}

void moveMotor(int speed, bool forward) {
  analogWrite(pinMotorPWM, speed);
  if (forward) {
    digitalWrite(pinMotorDir1, HIGH);
    digitalWrite(pinMotorDir2, LOW);
  } else {
    digitalWrite(pinMotorDir1, LOW);
    digitalWrite(pinMotorDir2, HIGH);
  }
}

void stopMotor() {
  analogWrite(pinMotorPWM, 0);
  digitalWrite(pinMotorDir1, LOW);
  digitalWrite(pinMotorDir2, LOW);
}

void currentPosNow() {
  currentPosition = myEnc.read();
  Serial.print("POSNOW:");
  Serial.println(currentPosition);

}
