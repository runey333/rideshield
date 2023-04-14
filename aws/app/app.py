import json
import urllib.parse
import boto3
import numpy as np
import cv2
import scipy

print('Loading function')

s3 = boto3.client('s3')


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        resp_bytes = response['Body'].read()
        
        np_array = np.frombuffer(resp_bytes, np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)     
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGRAY)
        
        edges = cv2.Canny(img[int(3 * (img.shape[0]/4)):], 100, 200)
        density = cv2.countNonZero(edges)/((img.shape[0]/4) * img.shape[1])

        return {"risk" : density, "bucket" : bucket, "key" : key}
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
              