import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
userTable = dynamodb.Table('rpt_user')
userHourTable = dynamodb.Table('rpt_user_hour')
userMinuteTable = dynamodb.Table('rpt_user_minute')
userAdTypeTable = dynamodb.Table('rpt_user_ad_type')
userAdvertizerTable = dynamodb.Table('rpt_user_advertizer')
userAdvertizerCategoryTable = dynamodb.Table('rpt_user_advertizer_category')

def lambda_handler(event, context):
    for record in event['Records']:
        print (record)
        if record['eventName'] == 'INSERT':
            userId = record['dynamodb']['Keys']['user_id']['S']
            year = record['dynamodb']['NewImage']['time_stamp']['S'][2:4]
            month = record['dynamodb']['NewImage']['time_stamp']['S'][4:6]
            day = record['dynamodb']['NewImage']['time_stamp']['S'][6:8]
            hour = record['dynamodb']['NewImage']['time_stamp']['S'][9:11]
            minute = record['dynamodb']['NewImage']['time_stamp']['S'][12:14]
            hourString = '%s/%s/%s %s:00' % (month, day, year, hour)
            minuteString = '%s/%s/%s %s:%s' % (month, day, year, hour, minute)
            advertizer = record['dynamodb']['NewImage']['advertizer']['S']
            adType = record['dynamodb']['NewImage']['ad_type']['S']
            brandCategory = record['dynamodb']['NewImage']['brand_category']['S']
            update_user_hour(userId, hourString)
            update_user_minute(userId, minuteString)
            update_user_advertizer_info(userId, advertizer, brandCategory)
            update_user_ad_type(userId, adType)
            
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def update_user_hour(userId, hourString):
    userHourTable.update_item(
        Key={'user_id': userId, 'hour_string': hourString},
        UpdateExpression='ADD impressions :val1',
        ExpressionAttributeValues={':val1': 1}
    )
    
def update_user_minute(userId, minuteString):
    userMinuteTable.update_item(
        Key={'user_id': userId, 'minute_string': minuteString},
        UpdateExpression='ADD impressions :val1',
        ExpressionAttributeValues={':val1': 1}
    )

def update_user_ad_type(userId, adType):
    userAdTypeTable.update_item(
        Key={'user_id': userId, 'ad_type': adType},
        UpdateExpression='ADD impressions :val1',
        ExpressionAttributeValues={':val1': 1}
    )
    
def update_user_advertizer_info(userId, advertizer, brandCategory):
    combo = advertizer + '|' + brandCategory
    userAdvertizerCategoryTable.update_item(
        Key={'user_id': userId, 'combo': combo},
        UpdateExpression='SET advertizer = :val1, brand_category = :val2 ADD impressions :val3',
        ExpressionAttributeValues={':val1':advertizer, ':val2': brandCategory, ':val3': 1}
    )
    
    response = userAdvertizerTable.query(
        KeyConditionExpression = 'user_id= :val1 AND advertizer = :val2',
        ExpressionAttributeValues={':val1': userId, ':val2': advertizer}
    )
 #   print(response)
    if response['Count'] == 0:
        moreAdvertizer = 1
    else:
        moreAdvertizer = 0
        
    userAdvertizerTable.update_item(
        Key={'user_id': userId, 'advertizer': advertizer},
        UpdateExpression='ADD impressions :val1',
        ExpressionAttributeValues={':val1': 1}
    )

    response = userTable.query(KeyConditionExpression=Key('user_id').eq(userId))
#    print(response)
    if response['Count'] == 0:
        impressions = 1
        advertizers = 1
    else:
        item = response['Items'][0]
        impressions = item['impressions'] + 1
        advertizers = item['advertizers'] + moreAdvertizer
        
    avgImpressions = Decimal(impressions / advertizers)
    
    userTable.update_item(
        Key={'user_id': userId},
        UpdateExpression='SET impressions=:val1, advertizers=:val2, average_advertizer_impressions=:val3',
        ExpressionAttributeValues={':val1': impressions, ':val2': advertizers, ':val3': avgImpressions}
    )
        
   
    