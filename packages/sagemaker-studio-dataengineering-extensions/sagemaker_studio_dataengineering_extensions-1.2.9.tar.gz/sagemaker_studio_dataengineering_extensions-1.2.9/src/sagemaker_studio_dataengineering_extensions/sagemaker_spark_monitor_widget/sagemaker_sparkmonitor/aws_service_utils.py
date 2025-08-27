import logging
import os
from urllib.parse import urlparse

import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

logger = logging.getLogger(__name__)

AWS_INTERNAL_MODEL_FOLDER_NAME = "/aws_internal_service_model/"
GLUE_INTERNAL_MODEL_NAME = 'glue_internal'
EMR_INTERNAL_MODEL_NAME = 'emr_internal'
DATAZONE_INTERNAL_MODEL_NAME = 'datazone_internal'

CONNECTION_TYPE_ATHENA='ATHENA'
CONNECTION_TYPE_REDSHIFT='REDSHIFT'
CONNECTION_TYPE_IAM='IAM'
CONNECTION_TYPE_GENERAL_SPARK='SPARK'
CONNECTION_TYPE_SPARK_GLUE='SPARK_GLUE'
CONNECTION_TYPE_SPARK_EMR_EC2='SPARK_EMR_EC2'
CONNECTION_TYPE_SPARK_EMR_SERVERLESS='SPARK_EMR_SERVERLESS'

EMR_EC2_ARN_KEY_WORD = "cluster"
EMR_SERVERLESS_ARN_KEY_WORD = "applications"



TEST_EMR_PREPROD = False

GET_CONNECTION_ENDPOINT = 'http://localhost:8888/jupyterlab/default/api/aws/datazone/connection'

def get_aws_internal_model_dir():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    data_path = script_dir + AWS_INTERNAL_MODEL_FOLDER_NAME
    return data_path

def get_internal_emr_client(connection_id=None, region=None):
    os.environ['AWS_DATA_PATH'] = get_aws_internal_model_dir()
    endpoint = f'https://elasticmapreduce-preprod.${region}.amazonaws.com'
    if region:
        session = boto3.Session(profile_name=connection_id, region_name=region)
    else:
        session = boto3.Session(profile_name=connection_id)

    if TEST_EMR_PREPROD:
        emr_client = session.client(service_name=EMR_INTERNAL_MODEL_NAME, endpoint_url=endpoint)
    else:
        emr_client = session.client(service_name=EMR_INTERNAL_MODEL_NAME)
    return emr_client

def get_internal_glue_client(connection_id=None, region=None):
    os.environ['AWS_DATA_PATH'] = get_aws_internal_model_dir()
    if region:
        session = boto3.Session(profile_name=connection_id, region_name=region)
    else:
        session = boto3.Session(profile_name=connection_id)

    glue_client = session.client(service_name=GLUE_INTERNAL_MODEL_NAME)
    return glue_client


def get_sigv4_signed_header_for_emr_serverless(url, region, connection_id=None):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    service = 'emr-serverless'
    canonical_uri = "/sessions"
    method = "GET"
    session = boto3.Session(profile_name=connection_id)
    url=f'https://{host}{canonical_uri}'
    request = AWSRequest(
        method,
        url,
        headers={'Host': host}
    )
    SigV4Auth(session.get_credentials().get_frozen_credentials(), service, region).add_auth(request)
    prepped = request.prepare()
    return prepped.headers

def get_connection_details(connection_name):
    try:
        params_dict = {}
        params_dict['name'] = connection_name
        response = requests.get(GET_CONNECTION_ENDPOINT, params=params_dict)
        return parseConnectionDetails(response.json())
    except Exception as e:
        raise e


def get_connection_type(connection_details):
    connection_type = connection_details["type"]
    if connection_type == CONNECTION_TYPE_ATHENA or connection_type == CONNECTION_TYPE_REDSHIFT or connection_type == CONNECTION_TYPE_IAM:
        return connection_type
    elif connection_type == CONNECTION_TYPE_GENERAL_SPARK:
        if connection_details["props"] and "sparkGlueProperties" in connection_details["props"]:
            return CONNECTION_TYPE_SPARK_GLUE
        if connection_details["props"] and "sparkEmrProperties" in connection_details["props"]:
            if connection_details["props"]["sparkEmrProperties"]["computeArn"] and EMR_EC2_ARN_KEY_WORD in connection_details["props"]["sparkEmrProperties"]["computeArn"]:
                return CONNECTION_TYPE_SPARK_EMR_EC2
            elif connection_details["props"]["sparkEmrProperties"]["computeArn"] and EMR_SERVERLESS_ARN_KEY_WORD in connection_details["props"]["sparkEmrProperties"]["computeArn"]:
                return CONNECTION_TYPE_SPARK_EMR_SERVERLESS
            else:
                raise RuntimeError(f"Unable to determine the EMR type of connection {connection_details['name']}")
    raise Exception(f"{connection_details['name']} type {connection_type} is not supported")

def has_key_chain_in_map(mapping, key_chain):
    current_dict = mapping
    for key in key_chain:
        if not isinstance(current_dict, dict):
            return False
        if key not in current_dict:
            return False
        current_dict = current_dict[key]
    return True

def parseConnectionDetails(connection_details):
    connection_type = get_connection_type(connection_details=connection_details)
    name = connection_details['name']
    region = connection_details['physicalEndpoints'][0]['awsLocation']['awsRegion']
    id = connection_details['connectionId']
    if id == 'toolkit':
        id = name
    if (connection_type == 'SPARK_EMR_EC2'):
        endpoint = connection_details['props']["sparkEmrProperties"]["livyEndpoint"]
        cluster_id = connection_details['props']["sparkEmrProperties"]['computeArn'].split('/')[-1]
        connection = {
            'connection_name': name,
            'connection_id': id,
            'endpoint': endpoint,
            'region': region,
            'connection_type': connection_type,
            'cluster_id': cluster_id,
        }
        if has_key_chain_in_map(connection_details, ['props', 'sparkEmrProperties', 'credentials', 'username']):
            connection['username'] = connection_details['props']["sparkEmrProperties"]["credentials"]["username"]
        if has_key_chain_in_map(connection_details, ['props', 'sparkEmrProperties', 'credentials', 'password']):
            connection['password'] = connection_details['props']["sparkEmrProperties"]["credentials"]["password"]
        if has_key_chain_in_map(connection_details, ['props', 'sparkEmrProperties', 'credentialsExpiration']):
            connection['expiration'] = connection_details['props']["sparkEmrProperties"]["credentialsExpiration"]
        if has_key_chain_in_map(connection_details, ['props', 'sparkEmrProperties', 'runtimeRole']):
            connection['environment_user_role_arn'] = connection_details['props']["sparkEmrProperties"]["runtimeRole"]
        return connection
    elif connection_type == 'SPARK_EMR_SERVERLESS':
        endpoint = connection_details['props']["sparkEmrProperties"]["livyEndpoint"]
        return {
            'connection_name': name,
            'connection_id': id,
            'livyEndpoint': endpoint,
            'region': region,
            'connection_type': connection_type
        }
    elif connection_type == 'SPARK_GLUE':
        return {
            'connection_name': name,
            'connection_id': id,
            'region': region,
            'connection_type': connection_type
        }
    return None
