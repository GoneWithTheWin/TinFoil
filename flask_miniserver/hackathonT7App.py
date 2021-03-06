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
            
            #table = ['user_id', 'combo', 'ad_title', 'ad_type', 'event_id', 'publisher', 'advertizer', 'brand_category', 'ad_description', 'image_url', 'device_type', 'ip_address', 'time_stamp']
            keysNeeded = ['user_id', 'ad_title', 'ad_type', 'publisher', 'advertizer', 'brand_category', 'ad_description', 'image_url', 'device_type'] 
            datetime_now = datetime.now()
            datetime_string = datetime_now.strftime("%Y%m%d%H%M%S%f")  
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

            table = dynamodb.Table('rpt_user_advertizer')
            query_response = table.query( KeyConditionExpression=Key('user_id').eq(row['user_id']) & Key('advertizer').eq(row['advertizer']) , ConsistentRead=True)
            data_log.info(query_response['Items'])
            count = 0
            if len(query_response['Items']) == 0:
                   count = 0
            else: 
                   count = query_response['Items'][0]['impressions']
            
            print ("the counts for user_id", row['user_id'], " is ", count)
            data_log.info("Retrieved the impression for user_id={0} advertizer={1} impression = {2}".format(row['user_id'], row['advertizer'], count))
            
            table = dynamodb.Table('ad_event')
            table.put_item(Item=row)
            data_log.info("record inserted to ad_event table")

            return str(count)
            
    except:
            print (sys.exc_info())
            message = "Something went wrong when insert user data or retrivev user advertizer counts "
            data_log.info(message )
            data_log.info(sys.exc_info())
            data_log.info(message )
            return message


@app.route('/')
@app.route("/hackathon/show_report", methods = ['GET'])
def process_report():
    data_log.info("-------------------")
    data_log.info("Receiving Hackathon Team 7 data ")
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
                 response = app.response_class(response = json.dumps(query_response['Items'] ),
                                          status = 200,
                                          mimetype='application/json'
                                         )
            elif params['report'] == 'rpt_user_advertizer':
                 if 'advertizer' not in params:
                      params['advertizer'] = 'Unknown'
                 print ('before get query_response')
                 #query_response = table.query( KeyConditionExpression=Key('user_id').eq(params['user_id']) & Key('advertizer').eq(params['advertizer']) )
                 #query_response = table.query( KeyConditionExpression=Key('user_id').eq(params['user_id']))
                 query_response = table.query( KeyConditionExpression='user_id = :user_id',
                                                  ExpressionAttributeValues={':user_id':params['user_id'],},
                                                  IndexName='user_id-impressions-index',
                                                  ScanIndexForward= False, 
                                                  Limit= 10
                                                )
                                                  
                 data_log.info(query_response['Items'])
                 print (query_response['Items'])
                 response = app.response_class(response = json.dumps(query_response['Items'] ),
                                          status = 200,
                                          mimetype='application/json'
                                         )

            elif params['report'] == 'rpt_user_advertizer_category':
                 if 'advertizer' not in params:
                      params['advertizer'] = 'Unknown'
                 if 'brand_category' not in params:
                      params['brand_category'] = 'Unknown'
                 query_response = table.query( KeyConditionExpression=Key('user_id').eq(params['user_id']) & Key('combo').eq("|".join([params['advertizer'], params['brand_category']])))
                 data_log.info(query_response['Items'])

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
    app.run( threaded = True, host=controller_host)


