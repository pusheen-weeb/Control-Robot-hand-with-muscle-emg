#include <Servo.h>
//communication
int so_bien_gui = 11;
int so_bien_nhan = 6;
int cac_bien_gui[11];
int cac_bien_nhan[6];

// create servo object to control a servo
Servo servo1;  
Servo servo2;
// servo port
int servo1_port = 2;
int servo2_port = 3;
// variable to store the servo servo position
int valServo1 = 0;    
int valServo2 = 0;
int valServo1Aliign1 = 0;
int valServo1Aliign2 = 0;
//servo changing speed
int speedServo1 = 0;
int speedServo2 = 0;
// number of loop skiped to control servo
int nLSkipServo1 = 20;
int nLSkipServo2 = 20;

int nLSkipSend = 100;

// Variables to hold sensor values
int valSensor1;
int valSensor2;
//min max threshold for sensor3
int minSensor1 = 100;
int maxSensor1 = 400;
int minSensor2 = 100;
int maxSensor2 = 400;

int loopCount1 = 0;
int loopCount2 = 0;

int loopCountSend = 0;
// time elapse
unsigned long CurrentTime;
void truyen_data() {
  Serial.print('<');
  for (int i = 0; i < so_bien_gui-1; i++) {
    Serial.print(cac_bien_gui[i]);
    Serial.print(',');    
  }
  Serial.print(cac_bien_gui[so_bien_gui-1]);
  Serial.print('>');
}
void nhan_data(){
  //data format <n,n,n,n>
  char inChar;
  if (Serial.available() > 0){
    inChar = Serial.read();
    if (inChar == '<'){
      String data = Serial.readStringUntil('>');
      int arr_index = 0;
      String value_str; 
      int commaIndex = data.indexOf(',');
      int previousCommaIndex = -1;
      while (commaIndex != -1){
        value_str = data.substring(previousCommaIndex+1, commaIndex);
        cac_bien_nhan[arr_index] = value_str.toInt();
        previousCommaIndex = commaIndex;
        arr_index = arr_index + 1;
        commaIndex = data.indexOf(',',previousCommaIndex+1);
        
        if (commaIndex == -1){
          value_str = data.substring(previousCommaIndex+1,data.length());
          cac_bien_nhan[arr_index] = value_str.toInt();
        }
      }
    }
  }
}

int fChangeServo(int valSensor,int valServo,int minValue,
int maxValue,int minServo,int maxServo,bool isReverse){
  int stepServo = 1;
  if (isReverse){
    stepServo = -1;
  }
  else{
    stepServo = 1;
  }
  if (minValue <= valSensor && valSensor <= maxValue){
    valServo = valServo+stepServo;
  }
  else{
    valServo = valServo-stepServo;
  }
  if (valServo > maxServo ){
    valServo = maxServo ;
  }
  if (valServo < minServo  ){
    valServo = minServo ;
  }
  return valServo;
}
void servo_test(){
  while (true){
    for (int i =0;i<=180;i++){
      servo1.write(i);
    servo2.write(i);
    delay(15);
    }
    for (int i =180;i>=0;i--){
      servo1.write(i);
    servo2.write(i);
    delay(15);
    }
  }
}
void setup() {
  // Set up serial port
  Serial.begin(9600);
  //servo pin attatch
  servo1.attach(servo1_port); 
  servo2.attach(servo2_port);
}

void loop() {
  //servo_test();
  
  //thuc thi hoat dong
  valSensor1 = analogRead(A0);
  valSensor2 = analogRead(A1);
  
  if (loopCount1 >= nLSkipServo1){
    valServo1 = fChangeServo(valSensor1,valServo1,minSensor1,maxSensor1,30,140,1);
    servo1.write(valServo1);
    valServo1Aliign1 = 180-valServo1-40;
    loopCount1 = 0;    
  }
  if (loopCount2 >= nLSkipServo2){
    valServo2 = fChangeServo(valSensor2,valServo2,minSensor2,maxSensor2,10,80,1);
    servo2.write(valServo2);
    valServo1Aliign2 = 180-valServo2-100;
    loopCount2 = 0;
  }
  loopCount1 = loopCount1 + 1;
  loopCount2 = loopCount2 + 1;
  loopCountSend = loopCountSend + 1;
 
  //gui
  if (loopCountSend >= nLSkipSend){
    //communication
    //truyen du lieu
    CurrentTime = millis();
    //truyen cac thong so he thong
    cac_bien_gui[0] = valSensor1;
    cac_bien_gui[1] = valSensor2;
    cac_bien_gui[2] = valServo1Aliign1;
    cac_bien_gui[3] = valServo1Aliign2;
    //truyen lai cac bien cai dat de kiem tra
    cac_bien_gui[4] = minSensor1;
    cac_bien_gui[5] = maxSensor1;
    cac_bien_gui[6] = nLSkipServo1;
    cac_bien_gui[7] = minSensor2;
    cac_bien_gui[8] = maxSensor2;
    cac_bien_gui[9] = nLSkipServo2;
    // thoi gian chay
    cac_bien_gui[10]= CurrentTime;
    truyen_data();
    //Serial.println(valSensor1);
    loopCountSend = 0;
  }
      
  //Nhan du lieu
  //Nhan
  nhan_data();
  //gan bien
  minSensor1 = cac_bien_nhan[0];
  maxSensor1 = cac_bien_nhan[1];
  nLSkipServo1 = cac_bien_nhan[2];
  minSensor2 = cac_bien_nhan[3];
  maxSensor2 = cac_bien_nhan[4];
  nLSkipServo2 = cac_bien_nhan[5];
  //Kiem tra neu minn cai dat lon hon max cai dat, rest ca 2 ve 0
  if (minSensor1>maxSensor1){
    minSensor1 = 0;
    minSensor1 = 0;
  }
  if (minSensor2>maxSensor2){
    minSensor2 = 0;
    minSensor2 = 0;
  }
}
