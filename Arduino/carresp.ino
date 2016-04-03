enum SteeringDirection {
  NONE,
  LEFT,
  RIGHT
};

struct ProgramStep {
  float target_throttle;
  SteeringDirection steering;
  int duration;
};


const ProgramStep program[] = {
  (ProgramStep){100, NONE, 2000},
  (ProgramStep){0, NONE, 2000},
  (ProgramStep){-100, NONE, 2000},
  (ProgramStep){0, NONE, 2000},

  (ProgramStep){100, LEFT, 2000},
  (ProgramStep){0, LEFT, 2000},
  (ProgramStep){-100, LEFT, 2000},
  (ProgramStep){0, LEFT, 2000},

  (ProgramStep){100, RIGHT, 2000},
  (ProgramStep){0, RIGHT, 2000},
  (ProgramStep){-100, RIGHT, 2000},
  (ProgramStep){0, RIGHT, 2000},
};
const int program_length = 12;


const int throttle_control = 2;
const int throttle_enable = 3;

const int steering_control = 4;
const int steering_enable = 5;

void setup(){
  pinMode(throttle_control, OUTPUT);
  pinMode(throttle_enable, OUTPUT);
  pinMode(steering_control, OUTPUT);
  pinMode(steering_enable, OUTPUT);

  digitalWrite(throttle_enable, LOW);
  digitalWrite(steering_enable, LOW);
}


float current_throttle = 0;
float acceleration_step = 0;
int program_counter = 0;
int step_counter = 0;
SteeringDirection current_steering = NONE;

void loop(){
  delay(1);

  if (step_counter == 0) {
    ProgramStep step = program[program_counter];
    acceleration_step = (step.target_throttle - current_throttle) / (float) step.duration;
    current_steering = step.steering;
    step_counter = step.duration;
    program_counter = (program_counter + 1) % program_length;
  }

  current_throttle += acceleration_step;
  step_counter -= 1;

  // THROTTLE
  float mult = 1;
  if (current_throttle >= 0) {
    digitalWrite(throttle_control, HIGH);
  }
  else {
    mult = -1;
    digitalWrite(throttle_control, LOW);
  }
  analogWrite(throttle_enable, (int) ((current_throttle * mult * 255.0) / 100.0));

  // STEERING
  if (current_steering == NONE) {
    digitalWrite(steering_enable, LOW);
    digitalWrite(steering_control, LOW);
  }
  else if (current_steering == LEFT) {
    digitalWrite(steering_enable, HIGH);
    digitalWrite(steering_control, HIGH);
  }
  else {
    digitalWrite(steering_enable, HIGH);
    digitalWrite(steering_control, LOW);
  }
}
