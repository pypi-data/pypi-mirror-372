import logging
import os
from functools import cache

import boto3
from sagemaker_jupyter_server_extension.env_handlers import SageMakerEnvHandler

AWS_INTERNAL_MODEL_FOLDER_NAME = "/aws_internal_model/"
DATAZONE_INTERNAL_MODEL_NAME = 'datazone_internal'

EMR_EC2_CONNECTION_NAME = 'SPARK_EMR_EC2'
EMR_SERVERLESS_CONNECTION_NAME = 'SPARK_EMR_SERVERLESS'
GLUE_CONNECTION_NAME = 'SPARK_GLUE'
SPARK_CONNECTION_NAME = 'SPARK'

logger = logging.getLogger(__name__)

connections_cache=None

@cache
def load_env():
    return SageMakerEnvHandler.read_metadata()


@cache
def get_aws_internal_model_dir():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    data_path = script_dir + '/..' + AWS_INTERNAL_MODEL_FOLDER_NAME
    return data_path


@cache
def create_datazone_internal_client():
    logger.info("creating datazone internal client")
    env = load_env()
    os.environ['AWS_DATA_PATH'] = get_aws_internal_model_dir()
    models_path = os.environ["AWS_DATA_PATH"]
    default_profile = 'default'
    session = boto3.Session(profile_name=default_profile)
    session._loader.search_paths.extend([models_path])
    region = env['dz_region']
    if env['dz_stage'] != 'prod':
        logger.info(f"datazone stage is {env['dz_stage']}")
        datazone_client = session.client(service_name=DATAZONE_INTERNAL_MODEL_NAME, region_name=region,
                                         api_version='2018-05-10', endpoint_url=env['dz_endpoint'])
    else:
        datazone_client = session.client(service_name=DATAZONE_INTERNAL_MODEL_NAME, region_name=region,
                                         api_version='2018-05-10')

    return datazone_client


def list_connection():
    try:
        logger.info("listing connections")
        datazone_client = create_datazone_internal_client()
        env = load_env()
        response = datazone_client.list_connections(domainIdentifier=env['domain_id'],
                                                    projectIdentifier=env['project_id'])
        connections = response['items']
        while 'nextToken' in response:
            next_token = response['nextToken']
            response = datazone_client.list_connections(domainIdentifier=env['domain_id'],
                                                        projectIdentifier=env['project_id'],
                                                        nextToken=next_token)
            connections.extend(response['items'])

        return {'items': connections}
    except Exception as e:
        logger.warning(e)
        logger.info('error happened when connection api list_connection')

def get_connection_list(force_update=False):
    global connections_cache
    # TODO change list to dict to improve efficiency
    if force_update or connections_cache is None:
        connections_cache = list_connection()['items']
    return connections_cache

def get_filtered_connection_list(connections, name, is_connections_refresh=False):
    # connection name is supposed to be unique
    filtered_connection = [connection for connection in connections if (connection and connection['name'] == name)]
    if len(filtered_connection) == 1:
        return filtered_connection
    if len(filtered_connection) == 0 and not is_connections_refresh:
        logger.info(f'connection with name {name} not found, refresh the cache and filter again.')
        connections = get_connection_list(True)
        return get_filtered_connection_list(connections, name, True)
    else:
        raise Exception(f'{len(filtered_connection)} connection/connections with the same name {name}')


def get_connection(name):
    try:
        env = load_env()
        datazone_client = create_datazone_internal_client()
        connections = get_connection_list()

        filtered_connection = get_filtered_connection_list(connections, name)
        connection_id = filtered_connection[0]['connectionId']
        logger.info(f'connection id is {connection_id}')
        connection = datazone_client.get_connection(domainIdentifier=env['domain_id'], identifier=connection_id,
                                                    withSecret=True)
        return connection
    except Exception as e:
        logger.warning(e)
        logger.info('error happened when connection api list_connection')
