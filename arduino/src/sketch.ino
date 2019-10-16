#define CONTROL_PIN 4
#define TOGGLE_PIN 12
#define LEFT_PIN 2
#define RIGHT_PIN 3
#define SIDE_PIN 5
#define BOTTOM_PIN 6
#define TOP_PIN 7

int state = 0; // closed, open, opening_long, opening_short, closing

void setup() {
  Serial.begin(9600);
  pinMode(CONTROL_PIN, OUTPUT);
  pinMode(LEFT_PIN, OUTPUT);
  pinMode(RIGHT_PIN, OUTPUT);

  pinMode(TOGGLE_PIN, INPUT);
  pinMode(BOTTOM_PIN, INPUT);
  pinMode(TOP_PIN, INPUT);
  pinMode(SIDE_PIN, INPUT);

  // try to init in the right state
  if (reachedTop() || reachedSide()) {
    state = 1;
  }

  Serial.println("ready");
  Serial.flush();
}

long lastTransitionStart;
long lastUpdate;
// long lastUp;
int buttonState[3];

void loop() {
  // if open or closed (not transitioning) and incoming command
  long now = millis();
  bool serialAvailable = Serial.available() > 0;
  bool buttonPressed = digitalRead(TOGGLE_PIN) == HIGH;
  if ((state == 0 || state == 1) && (serialAvailable || buttonPressed)) {
    int cmd;
    resetTimeout(now);

    // serial or button press?
    if (serialAvailable) {
      cmd = Serial.read();
      // dump remaining buffer
      while (Serial.available() > 0) {
        Serial.read();
      }
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
    if (reachedTimeout(now) || reachedTop() || reachedSide()) {
      changeState(1); // open
      // lastUp = now;
      doStop();
    } else if (state == 2 && reachedSide()) { // reached side so slow down
      changeState(3); // opening_short
      doUp(false); // open slow
    }
  }
//  if (state == 1 && now - lastUp > 5000) { // open and duration has passed
//    state = 4; // closing
//    lastTransitionStart = now;
//    doDown();
//  }
  if (state == 4) { // closing
    if (reachedBottom() || reachedTimeout(now)) { // reached limit or duration
      changeState(0); // closed
      doStop();
    } else if (reachedTop() || reachedSide()) { // retracted then reopened.  dont break the belt
      changeState(1); // open
      doStop();
    }
  }
  // report state of sensors every minute
  if (now - lastUpdate > 60000) {
    // currentstate, topsensor, sidesensor, bottomsensor
    Serial.print(state);
    Serial.print("|");
    Serial.print(digitalRead(TOP_PIN));
    Serial.print("|");
    Serial.print(digitalRead(SIDE_PIN));
    Serial.print("|");
    Serial.println(digitalRead(BOTTOM_PIN));
    lastUpdate = now;
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

bool reachedTimeout(long now) {
  return now - lastTransitionStart > 5000;
}

void resetTimeout(long now) {
  lastTransitionStart = now;
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
