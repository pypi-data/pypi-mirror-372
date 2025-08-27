import json
import logging
import traceback
from threading import Thread
from time import sleep

import requests
import schedule

from sagemaker_sparkmonitor.aws_service_utils import (
    get_connection_details,
    get_internal_emr_client,
    get_internal_glue_client,
    get_sigv4_signed_header_for_emr_serverless,
)

logger = logging.getLogger(__name__)

DEBUG_MODE = False
SSL_VERIFY = True
SAGEMAKER_SESSION_INFOS_KEY = 'sagemaker_session_infos'
CURRENT_CONNECTION_KEY = 'current_connection'

class SparkInfoReporter(Thread):
    """Class to poll infomation from spark live ui api in background thread
    and send to ScalaMonitor."""


    def __init__(self, monitor, ipython) -> None:
        super(SparkInfoReporter, self).__init__()
        self.monitor = monitor
        self.ipython = ipython
        self.is_spark_job_running = False
        self.is_execution_completed = False
        self.count = 0
        self.interval = 3
        self.attemptId = 0

        # connection/session info
        self.connection_type = None
        self.connection_name = None
        self.connection_id = None
        self.connection_details = None
        self.current_connection = None
        self.execution_id = None

        self.emr_ec2_auth_cookie_name = 'authToken'
        self.glue_auth_cookie_name = 'VerifiedAuthToken'
        self.emr_serverless_auth_cookie_name = 'VerifiedAuthToken'

        self.emr_ec2_gcsc_cookie = None
        self.glue_cookie = None
        self.emr_serverless_cookie = None

    def run(self):
        logger.info('reporter starts')
        while not self.should_stop():
            sleep(self.interval)

            self.update_spark_data()

    def should_stop(self):
        return False

    def update_spark_data(self):
        try:
            if DEBUG_MODE and self.monitor.comm:
                self.log('updating spark data')
            self.count += 1
            session_info = self.get_session_info()
            if session_info:
                self.get_spark_data(session_info)

        except Exception as e:
            # logger.info('error when updating spark data')
            # logger.info(e)
            self.log(f'errors when updating spark data, error msg is {e!s}')
            self.send_stacktrace()

    def handleMessage(self, msg):
        msgtype = msg['msgtype']

        if (msgtype == 'newExecution'):
            self.new_execution(msg)
        elif (msgtype == 'executed'):
            self.on_execution_completed()

    def on_execution_completed(self):
        if DEBUG_MODE:
            self.log('receive signal: execution completed')
        self.is_execution_completed = True

    def new_execution(self, msg):
        if DEBUG_MODE:
            self.log('receive signal: newExecution')
        self.is_spark_job_running = True
        self.is_execution_completed = False
        self.execution_id = msg['content']['cell_id'] if 'cell_id' in msg['content'] else None
        self.current_connection = msg['content']['connection_name'] if 'connection_name' in msg['content'] else None

    def should_poll_data(self):
        return self.is_spark_job_running or not self.is_execution_completed

    def check_if_spark_job_running(self, jobStatus):
        self.is_spark_job_running = self.is_any_job_running(jobStatus)

    def get_session_info(self):
        if DEBUG_MODE:
            self.log('session infos is ' + str(self.get_kernel_variable(SAGEMAKER_SESSION_INFOS_KEY)))
        session_infos_key, session_infos_value = self.get_kernel_variable(SAGEMAKER_SESSION_INFOS_KEY)
        session_infos = json.loads(session_infos_value) if session_infos_value else None

        if not session_infos or not self.should_poll_data():
            return None

        current_connetion = session_infos.get(CURRENT_CONNECTION_KEY, None)

        if DEBUG_MODE:
            self.log('current_connetion ' + str(current_connetion))

        if current_connetion:
            if not self.current_connection:
                self.current_connection = current_connetion
                return session_infos[current_connetion]
            elif self.current_connection == current_connetion:
                return session_infos[current_connetion]
            else:
                self.clean()

        return None

    def get_kernel_variable(self, key_str, default=None):
        for key in self.ipython.user_ns.keys():
            if key_str in key:
                data = self.ipython.user_ns.get(key)
                if data:
                    return key, data

        return default, default

    def get_spark_data(self, session_info):
        if not self.should_poll_data():
            return

        self.update_connection_info(session_info)

        send_request = None
        if self.connection_type == 'SPARK_EMR_EC2':
            application_id = session_info.get('application_id', None)
            self.connection_details['application_id'] = application_id
            # use on cluster ui pre signed url
            self.connection_details['endpoint'] = self.get_emr_ec2_endpoint()
            # use proxy endpoint of emr on ec2 cluster
            # self.connection_details['endpoint'] = f"{self.connection_details['endpoint']}:18888/proxy/{application_id}"
            send_request = self.send_emr_ec2_request
        elif self.connection_type == 'SPARK_GLUE':
            glue_session_id = session_info.get('session_id', None)
            if not glue_session_id:
                raise Exception('glue session id is None')
            self.connection_details['session_id'] = glue_session_id
            self.connection_details['endpoint'] = self.get_glue_endpoint()
            send_request = self.send_glue_request
        elif self.connection_type == 'SPARK_EMR_SERVERLESS':
            emr_serverless_session_id = str(session_info.get('session_id', None))
            if not emr_serverless_session_id:
                raise Exception('emr serverless session id is None')
            # emr service may have some session is as integer
            self.connection_details['session_id'] = emr_serverless_session_id
            self.connection_details['endpoint'] = self.get_emr_serverless_endpoint()
            send_request = self.send_emr_serverless_request
        else:
            self.log(f'SparkMonitor -- unknown connection type {self.connection_type}')

        applicationStatus = self.get_spark_application_data(send_request)
        executorStatus = self.get_spark_executor_data(send_request)
        jobStatus = self.get_spark_job_data(send_request)
        self.check_if_spark_job_running(jobStatus)
        stageStatus = self.get_spark_stage_data(send_request)
        taskStatus = []

        for stage in stageStatus:
            stageId = stage['stageId']
            attemptId = stage['attemptId']
            taskData = self.get_spark_task_data(stageId, attemptId, send_request)
            for task in taskData:
                task['stageId'] = stageId
                task['attemptId'] = attemptId
            taskStatus.append(taskData)

        msg =  {
                'msgtype': 'sparkData',
                'sessionInfo': session_info,  # NEW: Add raw session info for Spark UI functionality
                'sparkApplicationStatus': applicationStatus,
                'sparkExecutorStatus': executorStatus,
                'sparkJobStatus': jobStatus,
                'sparkStageStatus': stageStatus,
                'sparkTaskStatus' : taskStatus
            }
        self.sendToFrontEnd(msg)
        if DEBUG_MODE:
            self.log('got spark data')
            if session_info:
                self.log(f'session info sent: connection_type={session_info.get("connection_type")}, connection_name={session_info.get("connection_name")}')

    def is_any_job_running(self, job_status):
        for job in job_status:
            if job['status'] == 'RUNNING':
                return True
        return False

    def update_connection_info(self, session_info):
        if DEBUG_MODE:
            self.log('updating connection info')
        self.connection_type = session_info.get('connection_type', None)
        self.connection_name = session_info.get('connection_name', None)
        self.connection_details = get_connection_details(self.connection_name)
        self.connection_id = self.connection_details['connection_id']

    def send_request(self, url, query_params, cookie, verify=SSL_VERIFY):
        try:
            response_data = requests.get(url, query_params, cookies=cookie, verify=verify)
            return response_data
        except Exception as e:
            logger.error("Failed to call url: {}".format(url.split('?')[0]))
            logger.error(e)
            raise e from None

    def send_stacktrace(self):
        msg = f'exception happened with trace {traceback.format_exc()!s}'
        self.is_spark_job_running = False
        self.is_execution_completed = True
        self.error(msg)


    def error(self, error_mgs):
        msg =  {
                'msgtype': 'error',
                'msg': error_mgs
            }
        wrap_msg = {
                    'msgtype': 'fromscala',
                    'msg': msg
                }
        if self.monitor and self.monitor.comm:
            self.monitor.send(wrap_msg)

    def clean(self):
        msg =  {
                'msgtype': 'clean',
                'msg': 'clean'
            }
        wrap_msg = {
                    'msgtype': 'fromscala',
                    'msg': msg
                }
        if self.monitor and self.monitor.comm:
            self.monitor.send(wrap_msg)

    def log(self, log_msg = None):
        spark_data = 'send a message to frontend'
        if not log_msg:
            log_msg = spark_data
        msg =  {
                'msgtype': 'log',
                'msg': log_msg
            }
        wrap_msg = {
                    'msgtype': 'fromscala',
                    'msg': msg
                }
        if self.monitor and self.monitor.comm:
            self.monitor.send(wrap_msg)

    def sendToFrontEnd(self, msg):
        wrap_msg = {
                    'msgtype': 'fromscala',
                    'msg': msg
                }
        if self.monitor and self.monitor.comm:
            self.monitor.send(wrap_msg)

    def get_spark_application_data(self, send_request):
        # if application id is provided in session info
        if self.connection_details.get('application_id', None):
            application_id = self.connection_details['application_id']
            applications = self.getApplicationStatus(send_request)

            # filter running application data
            filterredApplications = [x for x in applications if x['id'] == application_id]
            if len(filterredApplications) != 1:
                logger.error('multiple applications!')

            self.attemptId = len(filterredApplications[0]['attempts'])
            return filterredApplications[0]
        else:
            # TODO get application from api
            applications = self.getApplicationStatus(send_request)
            if len(applications) != 1:
                logger.error('multiple applications!')

            self.connection_details['application_id'] = applications[0]['id']
            self.attemptId = len(applications[0]['attempts'])
            return applications[0]


    def getApplicationStatus(self, send_request):
        base_url = self.connection_details['endpoint']
        url = f"{base_url}/api/v1/applications"
        res = send_request(url)
        return res.json()

    def get_spark_executor_data(self, send_request):
        base_url = self.connection_details['endpoint']
        application_id = self.connection_details['application_id']
        url = f"{base_url}/api/v1/applications/{application_id}/{self.attemptId}/allexecutors"
        executorStatus = send_request(url)
        return executorStatus.json()

    def get_spark_job_data(self, send_request):
        base_url = self.connection_details['endpoint']
        application_id = self.connection_details['application_id']
        url = f"{base_url}/api/v1/applications/{application_id}/{self.attemptId}/jobs"
        jobStatus = send_request(url)
        return jobStatus.json()

    def get_spark_stage_data(self, send_request):
        base_url = self.connection_details['endpoint']
        application_id = self.connection_details['application_id']
        url = f"{base_url}/api/v1/applications/{application_id}/{self.attemptId}/stages"
        stageStatus = send_request(url)
        return stageStatus.json()

    def get_spark_task_data(self, stage_id, stage_attempt_id, send_request):
        base_url = self.connection_details['endpoint']
        application_id = self.connection_details['application_id']
        url = f"{base_url}/api/v1/applications/{application_id}/{self.attemptId}/stages/{stage_id}/{stage_attempt_id}/taskList"
        taskStatus = send_request(url)
        return taskStatus.json()


    def delete_auth_cookie(self, cookie_name):
        if cookie_name == 'emr_ec2_gcsc_cookie':
            self.emr_ec2_gcsc_cookie = None
        elif cookie_name == 'glue_cookie':
            self.glue_cookie = None
        elif cookie_name == 'emr_serverless_cookie':
            self.emr_serverless_cookie = None
        return schedule.CancelJob

    def get_emr_ec2_auth_cookie_name(self):
        return self.connection_details['cluster_id'] + self.emr_ec2_auth_cookie_name

    def get_emr_ec2_endpoint(self):
        spark_ui_url = self.get_emr_ec2_spark_ui_url()
        if spark_ui_url:
            # get auth cookie in advance
            self.get_auth_cookie_for_emr_ec2(spark_ui_url)
            return spark_ui_url.split('?')[0]

    def get_emr_ec2_spark_ui_url(self):
        emr_client = get_internal_emr_client(self.connection_id, region=self.connection_details['region'])
        cluster_id = self.connection_details['cluster_id']
        if 'environment_user_role_arn' in self.connection_details:
            res = emr_client.get_on_cluster_app_ui_presigned_url(
                ClusterId = cluster_id, OnClusterAppUIType = "ApplicationMaster", ApplicationId = self.connection_details['application_id'],
                ExecutionRoleArn = self.connection_details['environment_user_role_arn'])
        else:
            res = emr_client.get_on_cluster_app_ui_presigned_url(
                ClusterId=cluster_id, OnClusterAppUIType="ApplicationMaster",
                ApplicationId=self.connection_details['application_id'])
        if res['PresignedURLReady']:
            spark_ui_url = res['PresignedURL']
            return spark_ui_url
        return None

    def get_auth_cookie_for_emr_ec2(self, spark_ui_url = None):
        try:
            if self.emr_ec2_gcsc_cookie:
                return self.emr_ec2_gcsc_cookie

            if not spark_ui_url:
                spark_ui_url = self.get_emr_ec2_spark_ui_url()

            with requests.Session() as session:
                session.get(spark_ui_url, verify=SSL_VERIFY)
                self.emr_ec2_gcsc_cookie = session.cookies.get(self.get_emr_ec2_auth_cookie_name(), None)

            # TODO delete cookie after ~ 1 hour, consider it's expired
            schedule.every(59).minutes.do(self.delete_auth_cookie, cookie_name = 'emr_ec2_gcsc_cookie')
            schedule.run_pending()

            return self.emr_ec2_gcsc_cookie
        except Exception as e:
            if DEBUG_MODE:
                self.log('get_auth_cookie_for_emr_ec2 failed')
            logger.error(e)
            raise e from None

    def send_emr_ec2_request(self, url, query_params=None, cookie=None, verify=SSL_VERIFY):
        query_params_dict = query_params or {}
        query_params_dict["proxyapproved"] = "true"
        cookie_dict = cookie or {}
        cookie_dict["checked_" + self.connection_details.get('application_id', None)] = "true"

        cookie_dict[self.get_emr_ec2_auth_cookie_name()] = self.get_auth_cookie_for_emr_ec2()
        return self.send_request(url, query_params_dict, cookie_dict, verify)

    # code to use gcsc cookie
    # def get_auth_cookie_for_emr_ec2(self, url, query_params=None, cookie=None, verify=SSL_VERIFY):
    #     try:
    #         if self.emr_ec2_gcsc_cookie:
    #             return self.emr_ec2_gcsc_cookie

    #         connection_details = self.connection_details
    #         username = connection_details.get('username', None)
    #         password = connection_details.get('password', None)
    #         basic = HTTPBasicAuth(username=username, password=password)
    #         res = requests.get(url, query_params, cookies=cookie, auth=basic, verify=verify)

    #         self.emr_ec2_gcsc_cookie = res.cookies[self.emr_ec2_auth_cookie_name]

    #         # TODO delete gcsc cookie after ~ 1 hour, consider it's expired
    #         schedule.every(59).minutes.do(self.delete_auth_cookie, cookie_name = 'emr_ec2_gcsc_cookie')
    #         schedule.run_pending()

    #         return self.emr_ec2_gcsc_cookie
    #     except Exception as e:
    #         logger.info(e)
    #         return None

    # def send_emr_ec2_request(self, url, query_params=None, cookie=None, verify=SSL_VERIFY):
    #     query_params_dict = query_params or {}
    #     query_params_dict["proxyapproved"] = "true"
    #     cookie_dict = cookie or {}
    #     cookie_dict["checked_" + self.connection_details.get('application_id', None)] = "true"

    #     cookie_dict[self.emr_ec2_auth_cookie_name] = self.get_auth_cookie_for_emr_ec2(url, query_params_dict, cookie_dict, verify)

    #     return self.send_request(url, query_params_dict, cookie_dict, verify)

    def get_emr_serverless_endpoint(self):
        spark_ui_url = self.get_emr_serverless_spark_ui_url()
        if spark_ui_url:
            # get auth cookie in advance
            self.get_auth_cookie_for_emr_serverless(spark_ui_url)
            return spark_ui_url.split('?')[0]

    def get_emr_serverless_spark_ui_url(self):
        livyEndpoint = self.connection_details['livyEndpoint'].replace("-beta", "")
        canonical_uri = "/sessions"
        url=f'{livyEndpoint}{canonical_uri}'
        emr_serverless_sigv4_header = get_sigv4_signed_header_for_emr_serverless(livyEndpoint, region=self.connection_details['region'], connection_id=self.connection_id)
        response = requests.get(url, headers=emr_serverless_sigv4_header)
        res_json = json.loads(response.content.decode("utf-8"))
        session_id = self.connection_details['session_id']
        for session in res_json['sessions']:
            if str(session['id']) == session_id:
                return session['appInfo']['sparkUiUrl']

        return None

    def get_auth_cookie_for_emr_serverless(self, spark_ui_url = None):
        try:
            if self.emr_serverless_cookie:
                return self.emr_serverless_cookie

            if not spark_ui_url:
                spark_ui_url = self.get_emr_serverless_spark_ui_url()

            with requests.Session() as session:
                session.get(spark_ui_url, verify=SSL_VERIFY)
                self.emr_serverless_cookie = session.cookies.get(self.emr_serverless_auth_cookie_name, None)

            # TODO delete cookie after ~ 1 hour, consider it's expired
            schedule.every(59).minutes.do(self.delete_auth_cookie, cookie_name = 'emr_serverless_cookie')
            schedule.run_pending()

            return self.emr_serverless_cookie
        except Exception as e:
            if DEBUG_MODE:
                self.log('get_auth_cookie_for_emr_serverless failed')
            logger.error(e)
            raise e from None


    def send_emr_serverless_request(self, url, query_params=None, cookie=None, verify=SSL_VERIFY):
        query_params_dict = query_params or {}
        cookie_dict = cookie or {}

        cookie_dict[self.emr_serverless_auth_cookie_name] = self.get_auth_cookie_for_emr_serverless()
        return self.send_request(url, query_params_dict, cookie_dict, verify)


    def get_glue_dashboard_url(self):
        glue_client = get_internal_glue_client(self.connection_id, region=self.connection_details['region'])

        dashboard_url = glue_client.get_dashboard_url(ResourceId=self.connection_details['session_id'], ResourceType='SESSION').get('Url', None)
        return dashboard_url

    def get_auth_cookie_for_glue(self, dashboard_url=None):
        try:
            if self.glue_cookie:
                return self.glue_cookie

            if not dashboard_url:
                dashboard_url = self.get_glue_dashboard_url()

            with requests.Session() as session:
                session.get(dashboard_url, verify=SSL_VERIFY)
                self.glue_cookie = session.cookies.get(self.glue_auth_cookie_name, None)

            # TODO delete cookie after ~ 1 hour, consider it's expired
            schedule.every(59).minutes.do(self.delete_auth_cookie, cookie_name = 'glue_cookie')
            schedule.run_pending()

            return self.glue_cookie
        except Exception as e:
            if DEBUG_MODE:
                self.log('get_auth_cookie_for_glue failed')
            logger.error(e)
            raise e from None


    def send_glue_request(self, url, query_params=None, cookie=None, verify=SSL_VERIFY):
        query_params_dict = query_params or {}
        cookie_dict = cookie or {}

        cookie_dict[self.glue_auth_cookie_name] = self.get_auth_cookie_for_glue()
        return self.send_request(url, query_params_dict, cookie_dict, verify)

    def get_glue_endpoint(self):
        dashboard_url = self.get_glue_dashboard_url()
        if dashboard_url:
            # get auth cookie in advance
            self.get_auth_cookie_for_glue(dashboard_url)
            return dashboard_url.split('?')[0]
        else:
            return None
