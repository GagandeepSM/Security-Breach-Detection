#!/bin/bash
import RPi.GPIO as GPIO
import time
import numpy as np
import cv2
from datetime import datetime
import os
import smtplib
import serial
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from picamera.array import PiRGBArray
from picamera import PiCamera

gmail_user = "smartdoorbell987@gmail.com" #Sender email address
gmail_pwd = "project@123" #Sender email password
to = "gagandeepmanku47@gmail.com" #Receiver email address
subject = "Security Breach"
text = "Some One is Came at your home.Plz See the attached picture."

sensor = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor, GPIO.IN, GPIO.PUD_DOWN)

previous_state = False
current_state = False
print('Runnig...')
s = serial.Serial('/dev/serial0', 9600)
s.write('AT\r\n')
time.sleep(1)
s.write('AT+CMGF=1\r\n')
while True:
    previous_state = current_state
    current_state = GPIO.input(sensor)

    if current_state != previous_state:
        new_state = "HIGH" if current_state else "LOW"
        print("GPIO pin %s is %s" % (sensor, new_state))
	if current_state:
##		cap = cv2.VideoCapture(0)
##	        ret, frame = cap.read()
##		cap = cv2.VideoCapture(0)
                camera = PiCamera()
                rawCapture = PiRGBArray(camera)
 
# allow the camera to warmup
                time.sleep(0.1)
 
# grab an image from the camera
                camera.capture(rawCapture, format="bgr")
                frame = rawCapture.array
		
		picname = datetime.now().strftime("%y-%m-%d-%H-%M")
		picname = picname+'.jpg'
                cv2.imwrite(picname, frame)
                print "Saving Photo"
                print ('Sendig SMS')
                s.write('AT+CMGS=\"+917566116929\"\r\n')
                time.sleep(1)
                s.write('Some Is Come At Your Door\r\n');
                s.write("\x1A")
		print "Sending email"
		
		attach = picname
		
		msg = MIMEMultipart()

		msg['From'] = gmail_user
		msg['To'] = to
		msg['Subject'] = subject

		msg.attach(MIMEText(text))

		part = MIMEBase('application', 'octet-stream')
		part.set_payload(open(attach, 'rb').read())
		Encoders.encode_base64(part)
		part.add_header('Content-Disposition',
   		'attachment; filename="%s"' % os.path.basename(attach))
		msg.attach(part)

		mailServer = smtplib.SMTP("smtp.gmail.com", 587)
		mailServer.ehlo()
		mailServer.starttls()
		mailServer.ehlo()
		mailServer.login(gmail_user, gmail_pwd)
		mailServer.sendmail(gmail_user, to, msg.as_string())
		# Should be mailServer.quit(), but that crashes...
		mailServer.close()
		print "Email Sent"
		os.remove(picname)
