#include <EEPROM.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27,16,2);

// -------- Pin Definition --------
#define TRIG_PIN 2
#define ECHO_PIN 3

#define BUZZER_PIN 7
#define RED_LED 8
#define YELLOW_LED 9

#define SET_BUTTON 10
#define MANUAL_BUTTON 11

#define GREEN_LED 12
#define RELAY_PIN 13

long duration;
long distance;

int set_val;
int percentage;

bool pump=false;
bool state=false;

void setup() {

Serial.begin(9600);

lcd.init();
lcd.backlight();

lcd.setCursor(0,0);
lcd.print("WATER LEVEL:");

lcd.setCursor(0,1);
lcd.print("PUMP:OFF AUTO");

pinMode(TRIG_PIN,OUTPUT);
pinMode(ECHO_PIN,INPUT);

pinMode(BUZZER_PIN,OUTPUT);

pinMode(RED_LED,OUTPUT);
pinMode(YELLOW_LED,OUTPUT);
pinMode(GREEN_LED,OUTPUT);

pinMode(SET_BUTTON,INPUT_PULLUP);
pinMode(MANUAL_BUTTON,INPUT_PULLUP);

pinMode(RELAY_PIN,OUTPUT);

digitalWrite(RELAY_PIN,HIGH);

set_val=EEPROM.read(0);

if(set_val<5 || set_val>20)
set_val=20;

}

void loop(){

// ---------- Ultrasonic ----------
digitalWrite(TRIG_PIN,LOW);
delayMicroseconds(2);

digitalWrite(TRIG_PIN,HIGH);
delayMicroseconds(10);
digitalWrite(TRIG_PIN,LOW);

duration=pulseIn(ECHO_PIN,HIGH,30000);

distance=duration/29/2;

percentage=(set_val-distance)*100/set_val;

if(percentage>100)
percentage=100;

if(percentage<0)
percentage=0;

// ---------- Automatic ----------
if(percentage<30 && digitalRead(MANUAL_BUTTON))
pump=true;

if(percentage>85)
pump=false;

// ---------- AUTO / MANUAL ----------
if (digitalRead(MANUAL_BUTTON)) {      // AUTO MODE

    if (percentage < 30)
        pump = true;

    if (percentage > 85)
        pump = false;

}
else {                                 // MANUAL MODE

    if (!digitalRead(SET_BUTTON) && !state) {
        state = true;
        pump = !pump;                  // D10 Pump Toggle
    }

    if (digitalRead(SET_BUTTON))
        state = false;
}

digitalWrite(RELAY_PIN,!pump);

// ---------- LCD ----------
lcd.setCursor(12,0);
lcd.print("    ");

lcd.setCursor(12,0);
lcd.print(percentage);
lcd.print("%");

lcd.setCursor(5,1);

if(pump)
lcd.print("ON ");
else
lcd.print("OFF");

lcd.setCursor(9,1);

if(!digitalRead(MANUAL_BUTTON))
lcd.print("MANUAL");
else
lcd.print("AUTO  ");

// ---------- LED ----------
digitalWrite(RED_LED,LOW);
digitalWrite(YELLOW_LED,LOW);
digitalWrite(GREEN_LED,LOW);
digitalWrite(BUZZER_PIN,LOW);

if(percentage<30){

digitalWrite(RED_LED,HIGH);
digitalWrite(BUZZER_PIN,HIGH);

}

else if(percentage<80){

digitalWrite(YELLOW_LED,HIGH);

}

else{

digitalWrite(GREEN_LED,HIGH);

}

// ---------- Calibration ----------
if(!digitalRead(SET_BUTTON) && !state && digitalRead(MANUAL_BUTTON)){

state=true;

set_val=distance;

EEPROM.write(0,set_val);

lcd.clear();
lcd.print("HEIGHT SAVED");

delay(1000);

lcd.clear();
lcd.print("WATER LEVEL:");

}

if(digitalRead(SET_BUTTON))
state=false;

// ---------- Serial Output ----------
Serial.print(millis()/1000);
Serial.print(",");

Serial.print(distance);
Serial.print(",");

Serial.print(percentage);
Serial.print(",");

if(pump)
Serial.println("ON");
else
Serial.println("OFF");

delay(300);

}