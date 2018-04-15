#include "CurieIMU.h"
#include "arduinoFFT.h"
#include <DHT.h>
#define DHTPIN 0     // what pin we're connected to
#define DHTTYPE DHT22   // DHT 22  (AM2302)
DHT dht(DHTPIN, DHTTYPE); //// Initialize DHT sensor for normal 16mhz Arduino

int ledPin = 13;
int sensorPin = 0;
double alpha = 0.75;
int period = 500;
double change = 0.0;
/*
#define SAMPLES 32             //Must be a power of 2

#define SAMPLING_FREQUENCY 10
double vReal[SAMPLES*2];
double vImag[SAMPLES*2];
int counter=0;
arduinoFFT FFT = arduinoFFT();

*/

void setup() {
  // put your setup code here, to run once:
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
  dht.begin();
  while(!Serial) ;    // wait for serial port to connect..
  /* Initialise the IMU */
  CurieIMU.begin();
  CurieIMU.attachInterrupt(eventCallback);

  /* Enable Shock Detection */
  CurieIMU.setDetectionThreshold(CURIE_IMU_SHOCK, 10500); // 1.5g = 1500 mg
  CurieIMU.setDetectionDuration(CURIE_IMU_SHOCK, 1000);   // 50ms
  CurieIMU.interrupts(CURIE_IMU_SHOCK);

  
}

void loop() {
  // put your main code here, to run repeatedly:
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  float hic = dht.computeHeatIndex(t, h, false);
  Serial.print(hic);
  Serial.print(",");  
  
  static double oldValue = 0;
  static double oldChange = 0;
  int rawValue =analogRead(sensorPin);
  double value = alpha * oldValue+ (1 - alpha) * rawValue;
  //vReal[counter%SAMPLES]=value;
  //vImag[counter%SAMPLES]=0;
  //counter++;
  Serial.println(value);
  oldValue = value;
  delay(period);
  //if(counter%SAMPLES==0){
    /*FFT*/
    /*
    FFT.Windowing(vReal, SAMPLES, FFT_WIN_TYP_HAMMING, FFT_FORWARD);
    FFT.Compute(vReal, vImag, SAMPLES, FFT_FORWARD);
    FFT.ComplexToMagnitude(vReal, vImag, SAMPLES);
    double peak = FFT.MajorPeak(vReal, SAMPLES, SAMPLING_FREQUENCY);
 */
    /*PRINT RESULTS*/
    //Serial.println(peak);     //Print out what frequency is the most dominant.
 /*
    for(int i=0; i<(SAMPLES/2); i++)
    {
        //View all these three lines in serial terminal to see which frequencies has which amplitudes
         
        Serial.print((i * 1.0 * SAMPLING_FREQUENCY) / SAMPLES, 1);
        Serial.print(" ");
        Serial.println(vReal[i], 1);    //View only this line in serial plotter to visualize the bins
    }
    */
 
    //delay(1000);  //Repeat the process every second OR:
    //while(1);       //Run code once  
  //}
}

static void eventCallback(void)
{
  if (CurieIMU.getInterruptStatus(CURIE_IMU_SHOCK)) {
      Serial.print("FALL");
  }
}

