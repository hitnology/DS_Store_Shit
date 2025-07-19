#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <BLE2902.h>

#define BLE_DEVICE_NAME "DSSTORE"
#define SERVICE_UUID    "0c9f673d-4fa1-44c0-ae45-a45f4a461acc"
#define CHAR_UUID       "8971bf5a-3b9c-4fcb-bef7-2832f9f8f0dd"
#define BTN_PIN         13
#define LONG_PRESS_TIME 1000

BLECharacteristic* pCharacteristic;
bool deviceConnected = false;

class MyServerCallbacks: public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    deviceConnected = true;
  }

  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
    BLEDevice::startAdvertising();
  }
};

const int buttonPin = BTN_PIN; 
bool lastButtonState = HIGH;
unsigned long buttonPressTime = 0;
bool longPressActive = false;
unsigned long lastPooTime = 0;

void setup() {
  Serial.begin(115200);

  pinMode(buttonPin, INPUT_PULLUP);
  
  BLEDevice::init(BLE_DEVICE_NAME);

  BLEServer* pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  
  BLEService* pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
                      CHAR_UUID,
                      BLECharacteristic::PROPERTY_NOTIFY
                    );
  pCharacteristic->addDescriptor(new BLE2902());
  pService->start();
  
  BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->start();

  Serial.println("BLE Ready. Waiting for client to connect...");
}

void loop() {
  bool buttonState = digitalRead(buttonPin);
  unsigned long now = millis();

  if (buttonState == LOW && lastButtonState == HIGH) {
    // Button pressed
    buttonPressTime = now;
    longPressActive = false;
  } else if (buttonState == LOW && lastButtonState == LOW) {
    // Button held down
    if (!longPressActive && now - buttonPressTime >= LONG_PRESS_TIME) {
      Serial.println("Long press started.");
      longPressActive = true;
      lastPooTime = 0; 
    }
    if (longPressActive && deviceConnected && now - lastPooTime >= 500) {
      Serial.println("Long press active. Sending 'poo'...");
      pCharacteristic->setValue("poo");
      pCharacteristic->notify();
      lastPooTime = now;
    }
  } else if (buttonState == HIGH && lastButtonState == LOW) {
    // Button released
    if (!longPressActive && deviceConnected) {
      Serial.println("Short press. Sending 'clean'...");
      pCharacteristic->setValue("clean");
      pCharacteristic->notify();
    }
    longPressActive  = false;
  }

  lastButtonState = buttonState;
  delay(10);
}