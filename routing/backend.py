import googlemaps
import os
import boto3
from datetime import datetime
from pymongo.mongo_client import MongoClient
from bson.son import SON
from PIL import Image
import io

TRANSPORT_MODES = ["driving", "walking", "bicycling", "transit"]
gmaps = googlemaps.Client(key=os.getenv("GMAPS_API_KEY", ""))
uri = "mongodb+srv://arunsundaresan1:iQoaQme5BU6Axvrm@cluster0.owndbh6.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
s3 = boto3.client('s3')

MONGO_DB_NAME = "rideshield"
MONGO_COLLECTION_NAME = "imgs"

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    db = client.get_database(MONGO_DB_NAME)
    imgs = db.get_collection(MONGO_COLLECTION_NAME)
except Exception as e:
    raise e

def retrieve_routes(start, end, mode="walking"):
    return gmaps.directions(start, end, mode=mode, departure_time=datetime.now())

def get_route_info(start, end, mode="walking"):
    routes = retrieve_routes(start, end, mode)
    route_result = []
    for route in routes:
        #get a list of waypoints
        waypoints = []
        waypoints.append(route["legs"]["start_location"])
        for step in route["legs"]["steps"]:
            waypoints.append(step["end_location"])
        
        #get a list of images from mongodb near waypoints, along with risk scores
        images = []
        risk_scores = []
        
        for waypoint in waypoints:
            img_query = imgs.find_one({
                "coords": SON([
                    ("$near", {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [waypoint["lat"], waypoint["lng"]]
                        }
                    })
                ])
            })
            closest_point = imgs.find_one(img_query)
            
            if closest_point:
                response = s3.get_object(Bucket=closest_point["bucket"], Key=closest_point["key"])
                resp_bytes = response['Body'].read()
                img = Image.open(io.BytesIO(resp_bytes))
                
                images.append(img)
                risk_scores.append(closest_point["risk"])
            else:
                images.append(None)
                risk_scores.append(None)
        
        assert len(waypoints) == len(images)
        assert len(images) == len(risk_scores)
        
        #reflect in route_result
        route_result.append({"waypoints" : waypoints, "images" : images, "risk_scores" : risk_scores})
        
    return route_result

