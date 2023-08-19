import json
import boto3
import botocore
import os

client = boto3.client('pinpoint')

def lambda_handler(event, context):

    s3url = "s3://" + event['InputBucket'] + "/runs/" + event['Partition'] + "/endpoints/"

    try:
        response = client.create_import_job(
            ApplicationId=os.environ['PINPOINT_APPLICATION_ID'],
            ImportJobRequest={
                'DefineSegment': False,
                'Format': 'CSV',
                'RoleArn': os.environ['PINPOINT_IMPORT_ROLE_ARN'],
                'S3Url': s3url,
            }
        )
        print(response)
    except botocore.exceptions.ClientError as error:
        raise ValueError('The parameters you provided are incorrect: {}'.format(error))

    return {
        'statusCode': 200,
        'body': json.dumps('Imports started')
    }
