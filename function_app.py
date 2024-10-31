import azure.functions as func
import logging
import requests
from dotenv import load_dotenv
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


# Load environment variables from .env file
load_dotenv()

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="SyncToBlobFunction")
def SyncToBlobFunction(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    report_uuid = req.params.get('report_uuid')
    if not report_uuid:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            report_uuid = req_body.get('report_uuid')

    if report_uuid:
        data = getDataFromBlancco(report_uuid)
        if data:
            pushToBlobStorage(data)
        return func.HttpResponse(f"Data: {data}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a report_uuid in the query string or in the request body for a personalized response.",
             status_code=200
        )

def getDataFromBlancco(report_uuid):
    base_endpoint = os.getenv('BLANCCO_API_URL')
    api_key = os.getenv('BLANCCO_API_KEY')

    # Construct the action URL dynamically
    action = f"/reports/{report_uuid}/export"
    url = f"{base_endpoint}{action}"

    # Set up the headers
    headers = {
        "X-BLANCCO-API-KEY": api_key
    }

    # Send the GET request
    response = requests.get(url, headers=headers)

    response.encoding = 'utf-8'
    data = response.text

    # Check the response
    if response.status_code == 200:
        print("Request successful!")
        return data

    else:
        print(f"An error occurred: {response.status_code}")
        return f"Data {report_uuid} from Blancco"
        
def pushToBlobStorage(data):
    # Create a blob client
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('AZURE_CONNECTION_STRING'))
    blob_client = blob_service_client.get_blob_client(container=os.getenv('AZURE_CONTAINER_NAME'), blob='report_data')

    # Upload the data to the blob
    blob_client.upload_blob(data, overwrite=True)

    print("Data uploaded to the blob successfully!")
    