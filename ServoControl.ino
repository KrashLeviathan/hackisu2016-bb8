#include <Servo.h>                              // Includes Servo Library

Servo head;                                     // Servo motor that controls the head
int angle = 0;                                  // Keeps the current / last angle
int newAngle = 0;                               // The angle that is sent in
const int MaxChars = 4;                         // Max characters that can be sent in
char strValue[MaxChars + 1];                    // "Array" that holds value that's being sent in
int index = 0;                                  // Used for receiving serial input

// Initial setup
void setup()
{
 Serial.begin(9600);                            // Initializing serial communication
 head.attach(10);                               // Initialize servo motor to pin 10
 angle = 90;                                    // Default angle = 90 degrees
}

// Blank loop - using serialEvent instead
void loop() {}

// Runs when a serial event is received
void serialEvent()
{
  while(Serial.available()) 
  {
    // Value has been received, set to temp ch
    char ch = Serial.read();

    if (index < MaxChars && isDigit(ch))
    {            
      // Add ch to the "value" array        
      strValue[index++] = ch;
    }
    else
    {      
      strValue[index] = 0;
      newAngle = atoi(strValue);                // Computes the new angle to be set
      
      if (newAngle > 0 && newAngle < 180)
      {
        if (newAngle < angle)
        {
          // Decrement angle by one degree to prevent errors
          while (angle > newAngle)
          {
            head.write(angle);
            angle -= 1;
          }
        }
        else
        { 
          // Increment angle by one degree to prevent errors
          while (angle < newAngle)
          {
            head.write(angle);
            angle += 1;
          }
        }

        index = 0;                              // Reset index after new angle is set
        angle = newAngle;                       // Set angle holder to the new angle
      }  
    }
  }
}
