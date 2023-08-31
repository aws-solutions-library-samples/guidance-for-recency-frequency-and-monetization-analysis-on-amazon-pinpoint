import json
import hashlib
import boto3
import botocore
import os

client = boto3.client('stepfunctions')
stepfunction_arn = os.environ['STEPFUNCTION_ARN']

def lambda_handler(event, context):

    input_bucket = event['Records'][0]['s3']['bucket']['name']
    input_key = event['Records'][0]['s3']['object']['key']
    full_path = 's3://' + input_bucket + '/' + input_key
    partition_key = hashlib.md5(full_path.encode('utf-8')).hexdigest() # nosec
    region = event['Records'][0]['awsRegion']

    try:
        response = client.start_execution(
            stateMachineArn=stepfunction_arn,
            name=partition_key,
            input=json.dumps({
                'InputBucket': input_bucket,
                'InputKey': input_key,
                'FullPath': full_path,
                'Partition': partition_key,
                'Region': region
            })
        )
    except botocore.exceptions.ClientError as error:
        raise ValueError('The parameters you provided are incorrect: {}'.format(error))

    return 'Done'
