from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from datetime import date, datetime
import logging
from logging.config import fileConfig
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os

import pandas as pd
import json
from json import dumps
import time
import pyodbc

import subprocess
import sys

import boto3

folder=os.path.dirname(os.path.abspath(__file__)).split('/')
global HOME_DIR
HOME_DIR="/".join(folder)
PROC_IDFILE=HOME_DIR+'/log/.pidf'
file_path = os.path.abspath("logging.conf")
print ("the file_path is :", file_path)

fileConfig(file_path)
script_log = logging.getLogger("root")
data_log = logging.getLogger("hackathonT7")
try:
    pfile=open(PROC_IDFILE, "w")
    pfile.write(str(os.getpid()))
    pfile.close()

except:
    print ("Can't record hackathonT7App process id in file. Please check file structure permission")
    print (sys.exc_info())
    script_log.error("Can't record hackathonT7App process id in file. Please check file structure permission")
    script_log.error(sys.exc_info())

controller_host = '0.0.0.0'
controller_version = 1.0

app = Flask(__name__)


@app.route('/')
@app.route('/testService', methods = ['GET','POST'])
def index():
    return "Test Succeeded and Service is up and running"

@app.route('/')
@app.route("/hackathon/send_data", methods = ['POST'])
def process_data():
    print ("start processing json data")
    data_log.info("-------------------")
    data_log.info("Receiving Hackathon Team 7 data")
    data_log.info("-------------------")
    try:
            print (request.is_json)
            data_log.info("The data is in json format: " + str(request.is_json) )
            records = request.get_json()
            print (records)
            data_log.info(records)
            print ( "there are ", str(len(records)) , " in sent json" )
            for key, value in records.items():
                print (key, value)

            # Shamus part:
            # insert into DB

    except:
            data_log.info("can't get the user input")
            message = "can't get the user input"
            return message

    try:
           print ("try DynamoDB connection here")
   
           return  'Data Received'

    except:
            print  ("somehow got here exception")
            print (sys.exc_info())
            message = "Something wrong during hackathon team 7 data calculation. No output this time"
            return message

@app.route('/')
@app.route("/hackathon/show_report", methods = ['GET', 'POST'])
def process_report():
    print ("before data_log")
    data_log.info("-------------------")
    print ("after first data log")
    data_log.info("Receiving Hackathon Team 7 data ")
    data_log.info("-------------------")
    try:
            mv_report1 = request.args.get('report1')  # Change variable name later
            mv_report2 = request.args.get('report2')
            print ("got report1: ", mv_report1)
            print ("got report2: ", mv_report2)
            
            data_log.info("Hackathon Team 7 data sent: report1:-%s, report2:-%s" %(mv_report1, mv_report2))
            # Shamus or Jason to display
            
    except:
            data_log.info("can't get the user input")
            message = "can't get the user input"
            return message

    try:
           print ("try DynamoDB connection here")
   
           return  'report sent'  # replace by retrieved data later

    except:
            print  ("somehow got here exception")
            print (sys.exc_info())
            message = "Something wrong during hackathon team 7 data calculation. No output this time"
            return message

if __name__ == '__main__':
    print ("start to run hackathonT7App.py")
    data_log.info("start to run hackathonT7App.py")
    app.run( threaded = True, host=controller_host)


