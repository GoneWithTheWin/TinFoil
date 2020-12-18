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

import ssl
import boto3
import simplejson as json
from boto3.dynamodb.conditions import Key


folder=os.path.dirname(os.path.abspath(__file__)).split('/')
global HOME_DIR
HOME_DIR="/".join(folder)
PROC_IDFILE=HOME_DIR+'/log/.pidf'
file_path = os.path.abspath("logging.conf")
print ("the file_path is :", file_path)

fileConfig(file_path)
script_log = logging.getLogger("root")
data_log = logging.getLogger("hackathonT7")
"""
try: 
   context = ssl.Context(SSL.PROTOCOL_TLSv1_2)
   context.use_privatekey_file('key.pem')
   context.use_certificate_file('certificate.pem')
except:
    print ("Can't create ssl context")
    print (sys.exc_info())
"""
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
            part = 1
            print (request.is_json)
            data_log.info("The data is in json format: " + str(request.is_json) )
            records = request.get_json()
            row = records
            print (records)
            print ("----")
            print (row)
            data_log.info(records)
            ip_address = request.remote_addr
            data_log.info("from IP address: " + ip_address)
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('ad_event')
            
            #table = ['user_id', 'combo', 'ad_title', 'ad_type', 'event_id', 'publisher', 'advertizer', 'brand_category', 'ad_description', 'image_url', 'device_type', 'ip_address', 'time_stamp']
            keysNeeded = ['user_id', 'ad_title', 'ad_type', 'publisher', 'advertizer', 'brand_category', 'ad_description', 'image_url', 'device_type'] 
            datetime_now = datetime.now()
            #datetime_string = datetime_now.strftime("%Y%m%d%H%M%S%f")  # TODO uncommented when table definition changed from 10 to 20 in width
            datetime_string = datetime_now.strftime("%Y%m%d%H")
            datetime_string3 = datetime_now.strftime("%Y%m%d %H:%M:%S")
            for k in keysNeeded :
                  if k not in records or not records[k] :
                       row[k] =  'Unknown'
            # now make column values for combo, time_stamp, event_id, ip_address is TODO
            row['event_id']= datetime_string
            row['time_stamp'] = datetime_string3
            row['combo'] = "|".join([row['ad_title'], row['ad_type'], row['event_id'], row['publisher']])
            row['ip_address'] = ip_address
            data_log.info("pass connect to dynamodb, before insert ")
            data_log.info(row)
            
            table.put_item(Item=row)
            data_log.info("record inserted to ad_event table")
            time.sleep(2) # avoid write latency
            part = 2
            table = dynamodb.Table('rpt_user_advertizer')
            query_response = table.query( KeyConditionExpression=Key('user_id').eq(row['user_id']) & Key('advertizer').eq(row['advertizer']) , ConsistentRead=True)
            data_log.info(query_response['Items'])

            print ("the counts for user_id", row['user_id'], " is ", query_response['Items'][0]['impressions'])
            data_log.info("Retrieved the impression for user_id={0} advertizer={1} impression = {2}".format(row['user_id'], row['advertizer'], query_response['Items'][0]['impressions']))
            return str(query_response['Items'][0]['impressions'])
            
    except:
            print (sys.exc_info())
            if part == 1: 
                message = "can't get the user input"
                data_log.info("can't get the user input")
            elif part == 2:
                message = "can't retrieve impression count"

            data_log.info(sys.exc_info())
            data_log.info(message )
            return message


@app.route('/')
@app.route("/hackathon/show_report", methods = ['GET'])
def process_report():
    print ("before data_log")
    data_log.info("-------------------")
    print ("after first data log")
    data_log.info("Receiving Hackathon Team 7 data ")
    data_log.info("-------------------")
    try:
            params = request.args.to_dict()
            print ('the list of params is', params )
            report_tbl = ''
            user_id = ''
            if 'report' in params:
                print ("report in params")
                report_tbl = params['report']
            else:
                message = "report type is not passed in params, can't make report"
                data_log.info(message)
                return message

            if 'user_id' in params:
                print ("user_id in params")
                user_id = params['user_id']

            else:
                message = "user_id is not passed in params, can't make report"
                data_log.info(message)
                return message
            
            data_log.info("Hackathon Team 7 report request: report:-%s, user_id:-%s" %(report_tbl, user_id))
            data_log.info("Hackathon Team 7 report request data: ", params)
            
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(params['report'])
            response = "Retrieving report data..."

            if params['report'] == 'rpt_user' or params['report'] == 'ad_event' or params['report'] == 'rpt_user_hour' or params['report'] == 'rpt_user_minute' :
                query_response = table.query( KeyConditionExpression=Key('user_id').eq(params['user_id']) )
                data_log.info(query_response['Items'])
                response = app.response_class(response = json.dumps(query_response['Items'] ),
                                          status = 200,
                                          mimetype='application/json'
                                         )
            
            elif params['report'] == 'rpt_user_ad_type':
                 if 'ad_type' not in params:
                      params['ad_type'] = 'Unknown' 
                 print ('before get query_response')
                 query_response = table.query( KeyConditionExpression=Key('user_id').eq(params['user_id']) & Key('ad_type').eq(params['ad_type']) )
                 data_log.info(query_response['Items'])
                 print ("after query_response") 
                 response = app.response_class(response = json.dumps(query_response['Items'] ),
                                          status = 200,
                                          mimetype='application/json'
                                         )
            elif params['report'] == 'rpt_user_advertizer':
                 if 'advertizer' not in params:
                      params['advertizer'] = 'Unknown'
                 print ('before get query_response')
                 query_response = table.query( KeyConditionExpression=Key('user_id').eq(params['user_id']) & Key('advertizer').eq(params['advertizer']) )
                 data_log.info(query_response['Items'])
                 print ("after query_response")

                 response = app.response_class(response = json.dumps(query_response['Items'] ),
                                          status = 200,
                                          mimetype='application/json'
                                         )

            elif params['report'] == 'rpt_user_advertizer_category':
                 if 'advertizer' not in params:
                      params['advertizer'] = 'Unknown'
                 if 'brand_category' not in params:
                      params['brand_category'] = 'Unknown'
                 print ('before get query_response')
                 #query_response = table.query( KeyConditionExpression=Key('user_id').eq(params['user_id']) & Key('advertizer').eq(params['advertizer']) & Key('brand_category').eq(params['brand_category']) )
                 query_response = table.query( KeyConditionExpression=Key('user_id').eq(params['user_id']) & Key('combo').eq("|".join([params['advertizer'], params['brand_category']])))
                 data_log.info(query_response['Items'])
                 print ("after query_response")

                 response = app.response_class(response = json.dumps(query_response['Items'] ),
                                          status = 200,
                                          mimetype='application/json'
                                         )

 
            else:
                  response = "Report request passed in " + params['report'] + " is beyond scope"

            return  response
            
    except:
            data_log.info("can't get the user input")
            print (sys.exc_info())
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
    #context = SSL.Context(SSL.PROTOCOL_TLSv1_2)
    #context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    #context = ssl.SSLContext()
    #context.load_cert_chain('certificate.pem','key.pem')  
    #context.use_privatekey_file('key.pem')
    #context.use_certificate_file('certificate.pem')
    #app.run( threaded = True, host=controller_host, ssl_context=('certificate.pem','key.pem' ))
    #app.run( threaded = True, host=controller_host, ssl_context=context)
    app.run( threaded = True, host=controller_host)


