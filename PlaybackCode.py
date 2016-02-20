# Recording/Playback variables
recordMode = False          # Records user input sequence when enabled
recordPause = False         # Pauses the recording when enabled
pauseBuffer = False         # Helps identify single pause clicks
playbackMode = False        # Plays back recorded input when enabled
rvArray = []                # Holds RV data
lmaArray = []               # Holds LMA data
rmaArray = []               # Holds RMA data

###############################################################################

    Square = controller.get_button(15)          # Square button??? (check)

    ##### RECORDING / PLAYBACK BUTTON TOGGLING ####

    if Square == 1:                # Square starts record mode
        recordMode = True
        playbackMode = False
        rvArray[:] = []
        lmaArray[:] = []
        rmaArray[:] = []
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

###############################################################################
        
    RV = round(RV,2)

    if recordMode == True && recordPause == False:
        # Record values to playback arrays
        rvArray[playbackCount] = RV
        lmaArray[playbackCount] = LMA
        rmaArray[playbackCount] = RMA
        playbackCount += 1
    if playbackMode == True:
        # Iterate through playbackArrays instead of actual controller values
        motor1.ChangeDutyCycle(lmaArray[playbackCount])
        motor2.ChangeDutyCycle(rmaArray[playbackCount])
        ser.write(rvArray[playbackCount])
        playbackCount += 1
    else:
        # If playbackMode == False
        if motorOn == True:
            motor1.ChangeDutyCycle(LMA)
            motor2.ChangeDutyCycle(RMA)
        if motorOn == False:
            motor1.ChangeDutyCycle(0)
            motor2.ChangeDutyCycle(0)
        ser.write(str(RV))
