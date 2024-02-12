import json
import urllib.parse
import boto3
import os
import urllib.request

s3 = boto3.client('s3') 

#Replace with Aplication Load Balancer DNS Name
api_host = os.getenv('Load-Balancer-Test-938290255.us-east-1.elb.amazonaws.com')    
load_balancer_url = f'http://{api_host}/api/events' #Define URL for load balancer

#Principal function
def lambda_handler(event, context):
    handle_s3_event(event) #Handle S3 event

def handle_s3_event(event):
    #Extract event info, to get bucket S3 name and object key 
    bucket = event['Records'][0]['s3']['bucket']['name'] 
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    #Try block for S3 management
    try: 
        response = s3.get_object(Bucket=bucket, Key=key) #Get object from S3 Bucket
        print("CONTENT TYPE: " + response['ContentType']) #Print content type for test
        
        send_to_load_balancer(response) # Send object to load balancer function
    #If and error occours during object extraction
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

#Load balancer function
def send_to_load_balancer(response):
    try:
        request = urllib.request.Request(load_balancer_url)# Create a request object for the load balancer URL
        request.add_header('Content-Type', 'application/json; charset=utf-8') # Add the 'Content-Type' header to the request
        jsondata = json.dumps(response) # Convert the response object to a JSON-formatted string
        jsondataasbytes = jsondata.encode('utf-8') # Encode the JSON data as bytes
        request.add_header('Content-Length', len(jsondataasbytes))# Add the 'Content-Length' header to the request

        response = urllib.request.urlopen(request, jsondataasbytes, timeout=60 * 5) # Open a connection to the load balancer URL and send the JSON data, with 5 min timeout
        
        results = response.read().decode() # Read and decode the response from the load balancer
        print('results', results)
        
        #Return 200 status code if no fail
        return dict(
            body=json.loads(results),
            statusCode=200,
        )
    # Catch any exceptions that might occur during the process
    except Exception as e:
        print(e)
        # Manage erros
        raise e