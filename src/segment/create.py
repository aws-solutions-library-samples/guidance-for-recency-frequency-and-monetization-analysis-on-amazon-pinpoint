import json
import boto3
import botocore
import time
import os

segment_filters = {
    'Champions': {
        'Name': '_RFM_ Champions',
        'Metrics': {
            'RScore': {
                'ComparisonOperator': 'GREATER_THAN',
                'Value': 7
            },
            'FScore': {
                'ComparisonOperator': 'GREATER_THAN',
                'Value': 7
            },
            'MScore': {
                'ComparisonOperator': 'GREATER_THAN',
                'Value': 7
            }
        }
    },
    'Dormant': {
        'Name': '_RFM_ Dormant',
        'Metrics': {
            'RScore': {
                'ComparisonOperator': 'LESS_THAN',
                'Value': 3
            },
            'FScore': {
                'ComparisonOperator': 'LESS_THAN',
                'Value': 3
            },
            'MScore': {
                'ComparisonOperator': 'GREATER_THAN',
                'Value': 5
            }
        }
    },
    'Volatile': {
        'Name': '_RFM_ Volatile',
        'Metrics': {
            'RScore': {
                'ComparisonOperator': 'LESS_THAN',
                'Value': 3
            },
            'FScore': {
                'ComparisonOperator': 'GREATER_THAN',
                'Value': 5
            },
            'MScore': {
                'ComparisonOperator': 'GREATER_THAN',
                'Value': 7
            }
        }
    },
}

application_id=os.environ['PINPOINT_APPLICATION_ID']
region=os.environ['AWS_REGION']
account_id=os.environ['AWS_ACCOUNT_ID']
client = boto3.client('pinpoint')

def lambda_handler(event, context):

    response = client.get_app(
        ApplicationId=application_id
    )

    if '_rfm_segments_created' in response['ApplicationResponse']['tags']:
        print("Segments are already present. Exiting.")
    else:

        create_segments()

        try:
            response = client.tag_resource(
                ResourceArn="arn:aws:mobiletargeting:" + region + ":" + account_id + ":apps/" + application_id,
                TagsModel={
                    'tags': {
                        '_rfm_segments_created': 'true'
                    }
                }
            )
            print("Tagging pinpoint project.")
        except botocore.exceptions.ClientError as error:
            raise ValueError('The parameters you provided are incorrect: {}'.format(error))

    return {
        'statusCode': 200,
        'body': json.dumps('Segments processed. Check logs for details.')
    }

def create_segments():
    for segment in segment_filters:
        try:
            response = client.create_segment(
                ApplicationId=application_id,
                WriteSegmentRequest={
                    'Dimensions': {
                        'Metrics': segment_filters[segment]['Metrics']
                    },
                    'Name': segment_filters[segment]['Name']
                }
            )
            time.sleep(0.4)
        except botocore.exceptions.ClientError as error:
            raise ValueError('The parameters you provided are incorrect: {}'.format(error))
