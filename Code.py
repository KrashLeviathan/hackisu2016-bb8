import time
import serial
import RPi.GPIO as GPIO
import pygame               # External library

# Creating serial connection for arduino
ser = serial.Serial('/dev/ttyACM0',9600)

# Setting the pin numbering style to BCM
GPIO.setmode(GPIO.BCM)

# Setting the pins to output
GPIO.setup(23, GPIO.OUT)    # Sets pin 23 for Motor1 speed
GPIO.setup(24, GPIO.OUT)    # Sets pin 24 for Motor2 speed
GPIO.setup(4,GPIO.OUT)      # Direction for motor1 +
GPIO.setup(17,GPIO.OUT)     # Direction for motor1 -
GPIO.setup(27,GPIO.OUT)     # Direction for motor2 +
GPIO.setup(22,GPIO.OUT)     # Direction for motor2 -

# Initializing pin 23 to 100 Hz (duty cycle)
motor1 = GPIO.PWM(23,100)
motor1.start(0)             # Sets duty cycle to 0

# Initializing pin 24 to 100 Hz (duty cycle)
motor2 = GPIO.PWM(24,100)
motor2.start(0)             # Sets duty cycle to 0

# Enables the controller receiver
pygame.init()
pygame.joystick.init()

clock = pygame.time.Clock() # Sets the clock for later use
done = False                # Variable for cleaning up on completion
LMA = 0                     # Left motor speed
RMA = 0                     # Right motor speed
motorOn = True              # Allows the motors to be used

# Continuously runs while not exited
while done == False:
    
    # Necessary for pygame
    for event in pygame.event.get():
         if event.type == pygame.QUIT:
                 done = True

    controller = pygame.joystick.Joystick(0)    # Sets controller to first joystick (can have more than one)
    controller.init()                           # Initializes controller

    RU = controller.get_axis(3)                 # Right stick vertical axis
    RS = controller.get_axis(2)                 # Right stick horizontal axis
    LU = controller.get_axis(1)                 # Left stick vertical axis
    LS = controller.get_axis(0)                 # Left stick horizontal axis
    L2 = controller.get_button(8)               # L2 button
    R2 = controller.get_button(9)               # R2 button
    R1 = controller.get_button(11)              # R1 button
    L1 = controller.get_button(10)              # L1 button
    Up = controller.get_button(4)               # Up button
    Down = controller.get_button(6)             # Down button
    Start = controller.get_button(3)            # Start button
    Select = controller.get_button(0)           # Select button
    PS = controller.get_button(16)              # Playstation button
    X = controller.get_button(14)               # X button

    if LU < 0:
        # Left stick is pushed upwards/forward
        GPIO.output(4, GPIO.HIGH)               
        GPIO.output(17,GPIO.LOW)

        GPIO.output(27, GPIO.HIGH)
        GPIO.output(22,GPIO.LOW)
    else if LU > 0:
        # Left stick is pushed backwards/downwards
        GPIO.output(4, GPIO.LOW)
        GPIO.output(17,GPIO.HIGH)
        
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22,GPIO.HIGH)
    else:
        # Left stick is unmoved
        GPIO.output(4, GPIO.LOW)
        GPIO.output(17,GPIO.LOW)
        
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22,GPIO.LOW)

    if RMA > 100:
        RMA = 100
    if LMA > 100:
        LMA = 100
    if RMA < 40 and RMA != 0:
        RMA = 40
    if LMA < 40 and LMA !=0:
        LMA = 40
    
    LMA = 100 * abs(LU)
    RMA = 100 * abs(LU)
    if L1 == 1:
        LMA = 0
    if R1 == 1:
        RMA = 0

    if motorOn == True:
        motor1.ChangeDutyCycle(LMA)
        motor2.ChangeDutyCycle(RMA)
    if motorOn == False:
        motor1.ChangeDutyCycle(0)
        motor2.ChangeDutyCycle(0)
    RU = round(RU,2)
    ser.write(str(RU))
    if L1 ==1 and R1 == 1 and R2 == 1 and L2 ==1:
         done = True
         print("Done!")
    if X == 1:
        print "BEE BEE DOH"
    if Start == 1:
        motorOn = False
        print "motors Off"
    if Select == 1:
        motorOn = True
        print "motors On"
    clock.tick(30)
motor1.stop()
motor2.stop()
GPIO.cleanup()
pygame.quit()
