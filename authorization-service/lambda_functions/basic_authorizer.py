import os
import json
import base64
import logging

logger = logging.getLogger()
logger.setLevel("INFO")

def handler(event, context):
    logger.info(event)

    auth_header = event['authorizationToken']

    if not auth_header:
        logger.error("Error 401. Authorization header is absent.")
        return generateResponse(401, "Unauthorized")
    
    try:
        credentials = base64.b64decode(auth_header.split(' ')[1]).decode('utf-8')
        username, password = credentials.split(":")
        stored_password = os.getenv(username)

        if stored_password and password == stored_password:
            logger.info("Authorization is successfull. Access is allowed.")
            return generatePolicy(username, "Allow", event["methodArn"])
        else:
            logger.error("Error 403. Username or password is invalid.")
            return generatePolicy("user", "Deny", event["methodArn"])
    except Exception as e:
        logger.error(e)
        return generatePolicy("user", "Deny", event["methodArn"])


def generatePolicy(principalId, effect, resource):
    return {
        "principalId": principalId,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Resource": [
                        resource
                    ],
                    "Effect": effect
                }
            ]
        }
    }

def generateResponse(statusCode, message):
    return {
                'statusCode': statusCode,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    "Content-Type": "application/json"
                },
                'body': json.dumps({"message": message})
            }
