import json
import urllib.parse
import boto3
import numpy as np
import cv2
from pymongo.mongo_client import MongoClient

s3 = boto3.client('s3')
uri = "mongodb+srv://arunsundaresan1:iQoaQme5BU6Axvrm@cluster0.owndbh6.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)

MONGO_DB_NAME = "rideshield"
MONGO_COLLECTION_NAME = "imgs"


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    #bucket, key = "rideshield", "ligma.jpeg"
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        resp_bytes = response['Body'].read()
        
        np_array = np.frombuffer(resp_bytes, np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)     
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGRAY)
        
        edges = cv2.Canny(img[int(3 * (img.shape[0]/4)):], 100, 200)
        density = cv2.countNonZero(edges)/((img.shape[0]/4) * img.shape[1])
        
        #TODO: incorporate location and insert as GeoIndex of [lng, lat] arrays
        result = { 
            "risk" : density, 
            "bucket" : bucket, 
            "key" : key, 
            "coords" : {
                "type": "Point", 
                "coordinates": [ -137, 40 ] 
            }
        }
        
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
        
        db = client.get_database(MONGO_DB_NAME)
        imgs = db.get_collection(MONGO_COLLECTION_NAME)
        imgs.insert_one(result)

        return result
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e