#define CONTROL_PIN 4
#define TOGGLE_PIN 12
#define LEFT_PIN 2
#define RIGHT_PIN 3
#define SIDE_PIN 5
#define BOTTOM_PIN 6
#define TOP_PIN 7

void setup() {
  Serial.begin(9600);
  pinMode(CONTROL_PIN, OUTPUT);
  pinMode(LEFT_PIN, OUTPUT);
  pinMode(RIGHT_PIN, OUTPUT);

  pinMode(TOGGLE_PIN, INPUT);
  pinMode(BOTTOM_PIN, INPUT);
  pinMode(TOP_PIN, INPUT);
  pinMode(SIDE_PIN, INPUT);

  Serial.println("ready");
  Serial.flush();
}

int state = 0; // closed, open, opening_long, opening_short, closing
long lastTransitionStart;
long lastUp;
int buttonState[3];

void loop() {
  // if open or closed (not transitioning) and incoming command
  if ((state == 0 || state == 1) && (Serial.available() > 0 || digitalRead(TOGGLE_PIN))) {
    int cmd;
    resetTimeout();

    // serial or button?
    if (Serial.available() > 0) {
      cmd = Serial.read();
    } else {
      if (state == 0) {
        cmd = '1';
      } else {
        cmd = '0';
      }
    }
    
    switch (cmd) {
      case '1': // open
        changeState(2); // start opening
        doUp(true);
        break;
      case '0': // close
        changeState(4); // start closing
        doDown();
        break;
    }
  }
  if (state == 2 || state == 3) { // opening
    // duration has passed or limit reached
    //if (reachedTimeout() || reachedTop()) {
    // sliders get janky at the furthest extent so just stop when reaching the side
    if (reachedTimeout() || reachedTop() || reachedSide()) {
      changeState(1); // open
      lastUp = millis();
      doStop();
    } else if (state == 2 && reachedSide()) { // reached side so slow down
      changeState(3); // opening_short
      doUp(false); // open slow
    }
  }
//  if (state == 1 && millis() - lastUp > 5000) { // open and duration has passed
//    state = 4; // closing
//    lastTransitionStart = millis();
//    doDown();
//  }
  if (state == 4) { // closing
    if (reachedBottom() || reachedTimeout()) { // reached limit or duration
      changeState(0);
      doStop();
    }
  }
}

bool reachedBottom() {
  return !digitalRead(BOTTOM_PIN);
}

bool reachedSide() {
  return !digitalRead(SIDE_PIN);
}

bool reachedTop() {
  return !digitalRead(TOP_PIN);
}

bool reachedTimeout() {
  return millis() - lastTransitionStart > 5000;
}

void resetTimeout() {
  lastTransitionStart = millis();
}

void changeState(int _state) {
  Serial.print(state);
  Serial.print("->");
  Serial.println(_state);
  state = _state;
}

void doUp(bool fast) {
  digitalWrite(RIGHT_PIN, LOW);
  digitalWrite(LEFT_PIN, HIGH);
  if (fast) {
    analogWrite(CONTROL_PIN, 255);
  } else {
    analogWrite(CONTROL_PIN, 240);
  }
}

void doDown() {
  digitalWrite(RIGHT_PIN, HIGH);
  digitalWrite(LEFT_PIN, LOW);
  analogWrite(CONTROL_PIN, 255);
}

void doStop() {
  digitalWrite(LEFT_PIN, HIGH);
  digitalWrite(RIGHT_PIN, HIGH);
}
