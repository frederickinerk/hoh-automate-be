# Lambda function to return the tempSummary Object
# 
import boto3
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.info('hohAutomateService: initialisation starting...')


dynamo = boto3.resource('dynamodb')

# Service List (x=done, t=to be tested)
#x# /house
# # /room
#x# /tempSummary
#t# /automationConfig
# # /billing_events
# # /service
# # /roi_summary
# # /elec-detail
# # /model-base-line

actionTable = []
actionTable.append({"resource": "/house", "operation": "GET", "pre-fn": None, "moniker": "house", "post-fn": None})
actionTable.append({"resource": "/tempSummary", "operation": "GET", "pre-fn": None, "moniker": "tempSummary", "post-fn": None})
actionTable.append({"resource": "/automationConfig", "operation": "GET", "pre-fn": None, "moniker": "automationConfig", "post-fn": None})
logger.info('hohAutomateService: action table entries = ' + str(len(actionTable)))

##################################################################
# 
# getActionEntry
# Return the dict corresponding to the supplied resource and operation.
#
def getActionEntry(resource, operation):
    logger.info("hohAutomateService->getActionEntry: Looking for " + resource + " for operation " + operation)
    theDict = None
    i = 0
    for action in actionTable:
        #logger.info("Action table entry: " + str(i))
        if (action["resource"] == resource and action["operation"] == operation):
            theDict = action
            logger.info("hohAutomateService->getActionEntry: Found a match")
            break
        i = i + 1
    if theDict is None:
        logger.info("hohAutomateService->getActionEntry: Failed to find a match")
    return theDict

##################################################################
# 
# respond
# Generic response function returning standard headers.
#
def respond(err, res=None):
    logger.info("hohAutomateService->hohAutomateServiceLambda - Respond - err = " + str(err) + " res is " + str(len(res)) + " bytes")
    return {
        'statusCode': '400' if err == 1 else '200',
        'body': res,
        'headers': {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Origin": "*" ,
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET"
        },
    }

def lambda_handler(event, context):

    logger.debug("hohAutomateService->lambda_handler: Received event: event = " + json.dumps(event, indent=2))
    
    operation = event['httpMethod']
    path = event['path']
    query = event['queryStringParameters']['fake']
    logger.info("hohAutomateService->lambda_handler - Operation = [" + operation + "] path = [" + path + "] query = " + str(query))
    
    action = getActionEntry(path, operation)
    if action is None:
        errorText = '{"message": "Operation [' + operation + '] is not supported for resource [' + path + ']"}'
        logger.info("hohAutomateService->lambda_handler - Failed: " + errorText)
        return respond(1, errorText)
    else:
        logger.info("hohAutomateService->lambda_handler - OPERATION: " + operation + " Resource: " + path + " with query:" + query)
        table = dynamo.Table('Thingy')
        response = table.get_item(
            Key={
                'Moniker': action["moniker"],
                'Fake': query
            }
        )
        item = response['Item']
        logger.info("hohAutomateService->lambda_handler - returned item:" + str(len(json.dumps(item, indent=2))) + " bytes")
        logger.debug("hohAutomateService->lambda_handler - returned item:" + json.dumps(item, indent=2))
        return respond(0, json.dumps(item))       
