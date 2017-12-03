'''
LunchBot 9000 Code (LunchBot 9000 - Super Make Something Episode 14) - https://youtu.be/TtDo3ovEzh8
by: Alex - Super Make Something
date: November 11, 2017
license: Creative Commons - Attribution - Non Commercial.  More information at: http://creativecommons.org/licenses/by-nc/3.0/
'''

# Includes derivative of 'readadc()' written by Limor 'Ladyada' Fried for Adafruit Industries available at: http://bit.ly/2ySRKfC

'''
This code contains the following functions:
    - readadc(): Reads SPI data from the MCP3008 chip
    - main(): main loop
'''

import twitter
import datetime
import random
import RPi.GPIO as GPIO
from time import sleep

CONSUMER_KEY='INSERT CONSUMER KEY STRING HERE'
CONSUMER_SECRET='INSERT CONSUMER SECRET STRING HERE'
ACCESS_TOKEN='INSERT ACCESS TOKEN STRING HERE'
ACCESS_SECRET='INSERT ACCESS SECRET STRING HERE'


SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

GPIO.setmode(GPIO.BCM) #Set GPI to use 'Broadcom SOC channel' pin numbers

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

def readadc(adcnum, clockpin, mosipin, misopin, cspin):

        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True) 
        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low 
        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
 
        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1
 
        GPIO.output(cspin, True)        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

def main():       

    startHour=12 #Starting hour for when to send message
    stopHour=14 #Stop hour for when to send message

    lunchFlag=0 #Flag for only sending messages once a day 
    
    threshold=512 #Threshold reading for when to send message
    
    #Declare API object    
    api = twitter.Api(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token_key=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)
    #print(api.VerifyCredentials()) -- DEBUG: Print Twitter credentials 
    
    while 1:

        print('Iteration: ',i)        
        now=datetime.datetime.now() #Get current time
        nowHour=now.hour #Extract current hour
    
        if nowHour>startHour and nowHour<stopHour and lunchFlag==0:
            sleepDelay=0.1 #Decrease sleep delay within sensing window
            sensedValue=readadc(0, SPICLK, SPIMOSI, SPIMISO, SPICS) #Read sensor
            
            if sensedValue>threshold: #If a person walks in front of sensor, send message 
                randNum=random.randint(0,4) #Generate random number
                
                if randNum==0:
                    message=': Don\'t forget your lunch!'
                elif randNum==1:
                    message=': You gonna eat your tots?'
                elif randNum==2:
                    message=': PORKCHOP SANDWICHES!'
                elif randNum==3:
                    message=': Lunch? Do you have it?'
                else:
                    message='¿Dónde está lunch?'            
                
                dm = api.PostDirectMessage(message,screen_name='SuperMakeSmthng') #Send DM with message string             
                lunchFlag=1 #Set flag for having sent message
            
        else:
            sleepDelay=2 #Decrease checking frequency once message has been sent
        
        if nowHour>stopHour: #Reset flag
            lunchFlag=0 
        
        sleep(sleepDelay)
    
if __name__ == "__main__":
    main()