import azure.functions as func
import logging
from dotenv import load_dotenv
import os

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
        return func.HttpResponse(f"Data: {data}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a report_uuid in the query string or in the request body for a personalized response.",
             status_code=200
        )

def getDataFromBlancco(report_uuid):
    return f"Data {report_uuid} from Blancco"