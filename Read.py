#!/usr/bin/python
import RPi.GPIO as gpio
import RPi.GPIO as GPIO
import MFRC522
import os
import time

buttonDebounceTime = 500

def button_volume_up(channel):
    os.system('mpc volume +5') 

def button_volume_down(channel):
    os.system('mpc volume -5') 

def button_pause(channel):
    os.system('mpc toggle') 

def button_track_next(channel):
    os.system('mpc next') 

def button_track_prev(channel):
    os.system('mpc prev') 

GPIO.setmode(GPIO.BOARD) 

BUTTON_VOLUME_UP    = 18
BUTTON_VOLUME_DOWN  = 16
BUTTON_PAUSE        = 15
BUTTON_TRACK_PREV   = 11
BUTTON_TRACK_NEXT   = 13

GPIO.setup(BUTTON_VOLUME_UP, GPIO.IN,  pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_VOLUME_DOWN, GPIO.IN,  pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PAUSE, GPIO.IN,  pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_TRACK_PREV, GPIO.IN,  pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_TRACK_NEXT, GPIO.IN,  pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(BUTTON_VOLUME_UP,GPIO.FALLING,callback=button_volume_up,bouncetime=buttonDebounceTime) 
GPIO.add_event_detect(BUTTON_VOLUME_DOWN,GPIO.FALLING,callback=button_volume_down,bouncetime=buttonDebounceTime)
GPIO.add_event_detect(BUTTON_PAUSE,GPIO.FALLING,callback=button_pause,bouncetime=buttonDebounceTime)
GPIO.add_event_detect(BUTTON_TRACK_NEXT,GPIO.FALLING,callback=button_track_next,bouncetime=buttonDebounceTime)
GPIO.add_event_detect(BUTTON_TRACK_PREV,GPIO.FALLING,callback=button_track_prev,bouncetime=buttonDebounceTime)



def read_card(reader, key):
    # Scan for cards    
    (status, tag_type) = reader.MFRC522_Request(reader.PICC_REQIDL)

    # If a card is found
    if status != reader.MI_OK:
        return None
    print "Card detected"
            
    # Get the UID of the card
    (status, uid) = reader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status != reader.MI_OK:
        return None

    # Print UID
    print "Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3])
    # Select the scanned tag
    reader.MFRC522_SelectTag(uid)

    # Authenticate
    status = reader.MFRC522_Auth(reader.PICC_AUTHENT1A, 4, key, uid)

    # Check if authenticated
    if status != reader.MI_OK:
        print "Authentication error"
        return None
    data = reader.MFRC522_Read(4)

    reader.MFRC522_StopCrypto1()
    return data

def main():
    try:
        reader = MFRC522.MFRC522()

        # Welcome message
        print "Welcome to the MFRC522 data read example"
        print "Press Ctrl-C to stop."

        # This is the default key for authentication
        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        # This loop keeps checking for chips. If one is near it will get the UID and authenticate
        while True:
            data = read_card(reader, key) 
            if data is not None:
                print data          
                if data[5] != 0:
                    os.system("mpc stop")
                    os.system("mpc clear")
                    if data[6] == 1:
                        os.system('mpc random on')
                    else:
                        os.system('mpc random off')
                    cmd = 'mpc load ' + "{:02d}".format(data[5]) 
                    os.system(cmd)
                    os.system('mpc play')
    
    except KeyboardInterrupt:
        print "Ctrl+C captured, ending read."
    finally:
        gpio.cleanup()
        GPIO.cleanup()


if __name__ == '__main__':
    main()


