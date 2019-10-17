import RPi.GPIO as GPIO
import time
import smtplib
import email
import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GPIO.setmode(GPIO.BOARD)

'''pin configurations'''
noise = [7, 21, 13, 31]
trig = [8, 22, 15, 32]
echo = [10, 23, 16, 33]
red = [11, 24, 18, 35]
green = [12, 26, 19, 36]

#initially we used switch only with one lane, which is 4th lane(lane = 3)
switch = 40
# Set pin 40 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 

noisyLaneActive = 0

def GPIO_setup():
    '''Set up all the GPIO's of the board which are being used'''
    for pin in noise:
        GPIO.setup(pin, GPIO.IN)
    for pin in trig:
        GPIO.setup(pin, GPIO.OUT)
    for pin in echo:
        GPIO.setup(pin, GPIO.IN)
    for pin in red:
        GPIO.setup(pin, GPIO.OUT)
    for pin in green:
        GPIO.setup(pin, GPIO.OUT)
    return

def setLaneActive(lane):
    print('Lane number', lane, 'active')
    for i in range(4):
        if i==lane:
            GPIO.output(green[i], GPIO.HIGH)
            GPIO.output(red[i], GPIO.LOW)
        else:            
            GPIO.output(green[i], GPIO.LOW)
            GPIO.output(red[i], GPIO.HIGH)
    rv = croud(trig[lane], echo[lane])
    return rv

def croud(TRIG,ECHO):
    '''Pass the pin to control ultrasonic sensor.
    If more than 5 sec there is no traffic then control will pass to next lane.'''

    c=240
    recent = [0]*5
    
    GPIO.output(TRIG, False)
    #flag = 0
    while(c>0):

        if GPIO.input(switch)==GPIO.HIGH:
            while GPIO.input(switch)==GPIO.HIGH:
                continue
            print("Button was pushed!")
            sendMail()

        if noisyLaneActive:
        	return -1

        c-=1

        distance = calDist(TRIG, ECHO)
        for i in range(4, 0, -1):
            recent[i] = recent[i-1]
        recent[0] = distance

        threshold = 50
        # print(distance)
        
        if(recent[0]>threshold and recent[1]>threshold and recent[2]>threshold and recent[3]>threshold and recent[4]>threshold):
            print("lane changing, no traffic in the active lane")
            break
    return 0

def calDist(TRIG, ECHO):
        time.sleep(0.1)
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        while GPIO.input(ECHO)==0:
          pulse_start = time.time()
          
        while GPIO.input(ECHO)==1:
          pulse_end = time.time()
          
        pulse_duration = pulse_end - pulse_start

        distance = pulse_duration * 17150
        return round(distance, 2)

def callback(channel):
    c=GPIO.input(channel)
    if channel==noise[0]:
        print("Sound above threshold Detected over channel 000000000!", c)
        setNoisyLaneActive(0)
    elif channel==noise[1]:
        print("Sound above threshold Detected over channel 111111111!", c)
        setNoisyLaneActive(1)
    elif channel==noise[2]:
        print("Sound above threshold Detected over channel 222222222!", c)
        setNoisyLaneActive(2)
    elif channel==noise[3]:
        print("Sound above threshold Detected over channel 333333333!", c)
        setNoisyLaneActive(3)

def addNoiseEvent():
	for pin in noise:
		GPIO.add_event_detect(pin, GPIO.BOTH, bouncetime=1000)  # let us know when the pin goes HIGH or LOW, ignoring 
		                                                        #next event forn next 1 second
		GPIO.add_event_callback(pin, callback)  # assign function to GPIO PIN, Run function on change

def setNoisyLaneActive(lane):
	noisyLaneActive = 1
	print('Noisy Lane number', lane, 'active')
	for i in range(4):
		if i==lane:
			GPIO.output(green[i], GPIO.HIGH)
			GPIO.output(red[i], GPIO.LOW)
		else:            
			GPIO.output(green[i], GPIO.LOW)
			GPIO.output(red[i], GPIO.HIGH)
	time.sleep(5)
	noisyLaneActive = 0
	return 1

def sendMail():

    # set up the SMTP server
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()

    # input username
    UserName = input("Enter Username: ")
    # input password
    Password = getpass.getpass("Enter Password: ")

    s.login(UserName, Password)

    # get contact names and email ids
    names, emails = ['Dalia Ma\'am'], ['akarshsomani@iiitkalyani.ac.in'] 
    # message template
    message = 'Situation at this junction, kindly send help'
    # print(names[0], emails[0])

    subject = input("Enter the Subject: ")
    # For each contact, send the email:
    for name, email in zip(names, emails):
        msg = MIMEMultipart()       # create a message

        # setup the parameters of the message
        msg['From']=UserName
        msg['To']=email
        msg['Subject']=subject

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # send the message via the server set up earlier.
        s.send_message(msg)
        
        del msg


def main():
    GPIO_setup()

    addNoiseEvent()

    # setLaneActive(2)
    # return

    lane = 3
    while(True):
        if lane==0:
            lane = 1
        elif lane==1:
            lane = 2
        elif lane==2:
            lane = 3
        elif lane==3:
            lane = 0
        rv = setLaneActive(lane)
        if rv!=0:
        	while noisyLaneActive:
        		continue
        	setLaneActive(lane)

main()

GPIO.cleanup()
