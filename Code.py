import time
import serial
import RPi.GPIO as GPIO
import pygame               # External library

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
LMS = 0                     # Left motor speed
RMS = 0                     # Right motor speed
motorOn = True              # Allows the motors to be used

# Recording/Playback variables
recordMode = False          # Records user input sequence when enabled
recordPause = False         # Pauses the recording when enabled
pauseBuffer = False         # Helps identify single pause clicks
playbackMode = False        # Plays back recorded input when enabled
rvArray = []                # Holds RV data
lmsArray = []               # Holds LMA data
rmsArray = []               # Holds RMA data

# Continuously runs while not exited
while done == False:
    
    # Necessary for pygame
    for event in pygame.event.get():
         if event.type == pygame.QUIT:
                 done = True

    controller = pygame.joystick.Joystick(0)    # Sets controller to first
                                                # joystick (can have more
                                                # than one)
    controller.init()                           # Initializes controller

    RV = controller.get_axis(3)                 # Right stick vertical axis
    RH = controller.get_axis(2)                 # Right stick horizontal axis
    LV = controller.get_axis(1)                 # Left stick vertical axis
    LH = controller.get_axis(0)                 # Left stick horizontal axis
    L2 = controller.get_button(8)               # L2 button
    R2 = controller.get_button(9)               # R2 button
    R1 = controller.get_button(11)              # R1 button
    L1 = controller.get_button(10)              # L1 button
    Up = controller.get_button(4)               # Up button
    Down = controller.get_button(6)             # Down button
    Start = controller.get_button(3)            # Start button
    Select = controller.get_button(0)           # Select button
    PS = controller.get_button(16)              # Playstation button
    Triangle = controller.get_button(12)        # Triangle button
    Circle = controller.get_button(13)          # Circle button
    X = controller.get_button(14)               # X button
    Square = controller.get_button(15)          # Square button

    ##### RECORDING / PLAYBACK BUTTON TOGGLING ####

    if Square == 1:                # Square starts record mode
        recordMode = True
        playbackMode = False
        rvArray[:] = []
        lmsArray[:] = []
        rmsArray[:] = []
        playbackCount = 0
    if Triangle == 1 and pauseBuffer == False:  # Triangle stops record mode
        pauseBuffer = True
        recordPause = not recordMode
        pauseCount = 10
    if Triangle == 0 and pauseBuffer == True:
        pauseCount -= 1            # Countdown removes possibility of bouncing.
        if pauseCount == 0:        # It takes 10 cycles before another
            pauseBuffer = False    # pause can be initiated
    if Circle == 1:                # Circle starts playback mode
        playbackMode = True
        recordMode = False
        playbackCount = 0
    if playbackCount >= 450:       # 15 seconds of playback at 30fps
        recordMode = False
        playbackMode = False
        recordPause = False
        pauseBuffer = False

    if LV < 0:
        # Left stick is pushed upwards/forward
        GPIO.output(4, GPIO.HIGH)               
        GPIO.output(17,GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(22,GPIO.LOW)
    elif LV > 0:
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

    LMS = 100 * abs(LV)         # Set left motor speed
    RMS = 100 * abs(LV)         # Set right motor speed
    RV = round(RV,2)

    if recordMode == True && recordPause == False:
        # Record values to playback arrays
        rvArray[playbackCount] = RV
        lmsArray[playbackCount] = LMS
        rmsArray[playbackCount] = RMS
        playbackCount += 1
    if playbackMode == True:
        # Iterate through playbackArrays instead of actual controller values
        motor1.ChangeDutyCycle(lmsArray[playbackCount])
        motor2.ChangeDutyCycle(rmsArray[playbackCount])
        ser.write(rvArray[playbackCount])
        playbackCount += 1
    else:
        # If playbackMode == False
        if motorOn == True:
            motor1.ChangeDutyCycle(LMS)
            motor2.ChangeDutyCycle(RMS)
        if motorOn == False:
            motor1.ChangeDutyCycle(0)
            motor2.ChangeDutyCycle(0)
        ser.write(str(RV))

    # Send motor speeds to arduino for PWM
    print(LMS)
    
    if L1 == 1 and R1 == 1 and R2 == 1 and L2 == 1:
        # Ends program
        done = True
        print("Done!")
    elif Start == 1:
        # Turning motors off
        motorOn = False
        print "Motors turned off"
    elif Select == 1:
        # Turning motors on
        motorOn = True
        print "Motors turned on"

    clock.tick(30)              # Delays program

# Cleanup
motor1.stop()
motor2.stop()
GPIO.cleanup()
pygame.quit()
