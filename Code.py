import time
import serial
import RPi.GPIO as GPIO
import pygame               # External library
import random

time.sleep(5)           # Wait for PS3 controller to turn on

# Initialize serial connection
#try:
#    ser = serial.Serial('/dev/ttyACM0', 9600)
#except:
     # First connection didn't work - retry
#    ser = serial.Serial('/dev/ttyACM1', 9600)
    
# Initialize sound player
pygame.mixer.init()

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

# Recording/Playback variables
recordMode = False          # Records user input sequence when enabled
playbackMode = False        # Plays back recorded input when enabled
lmsArray = []               # Holds LMA data
rmsArray = []               # Holds RMA data
lvArray = []                # Holds left vertical data
playbackCount = 0           # Index for playback iteration
maxPlayback = 0             # Keeps track of the playback actions
#servoTimer = 0
playingMusic = False
musicBusy = False

print("Initialized")
pygame.mixer.music.set_volume(1.0)

# Continuously runs while not exited
while done == False:
    
    # Necessary for pygame
    for event in pygame.event.get():
         if event.type == pygame.QUIT:
                 done = True

    controller = pygame.joystick.Joystick(0)    # Sets controller to first joystick
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
    musicBusy = pygame.mixer.music.get_busy()

    if Start == 1 and musicBusy == False and playingMusic == False:
        pygame.mixer.music.load("/home/pi/BB-8/songs/" + str(random.randrange(0, 10)) + ".mp3")
        pygame.mixer.music.play(0, 0.0)
        playingMusic = True

    if PS == 1 and musicBusy == False:
        pygame.mixer.music.load("/home/pi/BB-8/startup.mp3")
        pygame.mixer.music.play(0, 0.0)
    
    if Down == 1:
        playingMusic = False
        pygame.mixer.music.stop()
    
    if Square == 1:                # Square starts record mode
        recordMode = True
        playbackMode = False
        lmsArray = []
        rmsArray = []
        lvArray = []
        playbackCount = 0
        maxPlayback = 0
    time.sleep(0.1)
    
    if Circle == 1:                # Circle starts playback mode
        playbackMode = True
        recordMode = False
        playbackCount = 0

    if Up == 1 and musicBusy == False:                    # Plays a random sound
        musicPlaying = False
        pygame.mixer.music.load("/home/pi/BB-8/BB8Sounds/" + str(random.randrange(0, 19)) + "-bb8.wav")
        pygame.mixer.music.play(0, 0.0)
        
    if playbackCount >= 450:       # 15 seconds of playback at 30fps
        recordMode = False
        playbackMode = False

    if playbackMode == True:
        # Iterate through playbackArrays instead of actual controller values 
        LMS = lmsArray[playbackCount]
        RMS = rmsArray[playbackCount]
        LV = lvArray[playbackCount]
        playbackCount += 1

        if playbackCount >= 449 or playbackCount >= maxPlayback:
            playbackMode = False
    else:
        LMS = 100 * abs(LV)
        RMS = 100 * abs(LV)

        if L2 == 1:
            # Turning left
            LMS = LMS * 0.8
        elif R2 == 1:
            # Turning right
            RMS = RMS * 0.8

    if playingMusic == True and musicBusy == False:
        pygame.mixer.music.load("/home/pi/BB-8/songs/" + str(random.randrange(0, 10)) + ".mp3")
        pygame.mixer.music.play(0, 0.0)

    # Lower bounds for left motor
    if LMS < 0:
        LMS = 0

    # Lower bounds for left motor
    if RMS < 0:
        RMS = 0

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

    if recordMode == True:
        # Record values to playback arrays
        lmsArray.append(LMS)
        rmsArray.append(RMS)
        lvArray.append(LV)
        playbackCount += 1
        maxPlayback += 1

    # Set motor values to LMS & RMS
    motor1.ChangeDutyCycle(LMS)
    motor2.ChangeDutyCycle(RMS)

#    print (str(LMS) + ", " + str(RMS))
#        if servoTimer > 10:
#            # Set servo motor speed
#            ser.write(str(int(LV * 30 + 90)) + ";")
#            servoTimer = 0

    if L1 == 1 and R1 == 1 and R2 == 1 and L2 == 1:
        # Ends program
        done = True
        print("Done!")

#   servoTimer += 1
    clock.tick(30)              # Delays program

# Cleanup
motor1.stop()
motor2.stop()
GPIO.cleanup()
pygame.mixer.quit()
pygame.quit()
