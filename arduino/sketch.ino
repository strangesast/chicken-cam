#include <AccelStepper.h>
#include <MultiStepper.h>

AccelStepper stepper1(AccelStepper::FULL4WIRE, 2, 4, 3, 5);
AccelStepper stepper2(AccelStepper::FULL4WIRE, 8, 10, 9, 11);
MultiStepper steppers;

void setup() {
  Serial.begin(9600);

  pinMode(0, INPUT_PULLUP);

  stepper1.setMaxSpeed(500);
  stepper1.setAcceleration(10000);
  stepper2.setMaxSpeed(500);
  stepper2.setAcceleration(10000);

  steppers.addStepper(stepper1);
  steppers.addStepper(stepper2);

  Serial.println("calibrating...");
  stepper2.move(1000);
  stepper2.setSpeed(500);
  while (digitalRead(0)) {
    stepper2.runSpeed();
  }
  stepper2.setCurrentPosition(0);
  Serial.println("done");
}

void loop() {
  long positions[2];
  
  positions[0] = 0;
  positions[1] = -100;
  steppers.moveTo(positions);
  // uses acceleration
  //stepper1.runToPosition();
  //stepper2.runToPosition();

  // doesn't use acceleration
  steppers.runSpeedToPosition();
  delay(1000);
  
  positions[0] = 0;
  positions[1] = -800;
  steppers.moveTo(positions);
  steppers.runSpeedToPosition();
  delay(1000);
}
