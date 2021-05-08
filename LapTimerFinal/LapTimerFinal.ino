#define MARGIN        15
#define WHEELBASE     5.167323
#define TRUE          1
#define FALSE         0


float calibratedAverage;
long lapTime;
int lapCount = 0;
long startTime;
int sensorIn;
int pressurePin = A0;
int speedFound;

float calibratePressure();
void printLap(long lapTime, int lapCount);
void printSpeed(long frontWheelTime, long backWheelTime);
void getSpeed(int timeOut);

void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  Serial.begin(9600);
  //Blink the light on and off for 5 seconds to let us know the timer is starting
  int i;
  for (i = 0; i < 5; ++i)
  {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
    digitalWrite(LED_BUILTIN, LOW);
    delay(500);
  }
  //Turn the light solid to let us know timing has started
  digitalWrite(LED_BUILTIN, HIGH);
  calibratedAverage = calibratePressure();
  startTime = millis();
}

void loop()
{
  sensorIn = analogRead(pressurePin);
  if (sensorIn > calibratedAverage + MARGIN)
  {
    ++lapCount;
    lapTime = millis() - startTime;
    lapTime /= 1000;
    Serial.print("L");
    Serial.print(lapCount);
    Serial.print(":");
    Serial.println(lapTime);
    delay(100);
    startTime = millis();
  }
}

float calibratePressure()
{
  int calibrationCounter;
  float average = 0;
  for (calibrationCounter = 0; calibrationCounter < 100; ++calibrationCounter)
  {
    average += analogRead(pressurePin);
    delay(10);
  }
  average /= 100;
  Serial.print("Calibration Pressure: ");
  Serial.println(average);

  return average;
}
