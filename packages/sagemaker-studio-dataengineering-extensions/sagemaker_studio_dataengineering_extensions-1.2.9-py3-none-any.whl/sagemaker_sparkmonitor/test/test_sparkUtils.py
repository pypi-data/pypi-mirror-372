import unittest
import unittest.mock

from sagemaker_sparkmonitor.sparkUtils import SparkInfoReporter


class TestSparkUtils(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_spark_util(self):
        sparkInfoReporter = SparkInfoReporter(None, None)

        assert sparkInfoReporter.is_spark_job_running == False

    # def glue_test():
    #     client = get_internal_glue_client()
    #     ret = client.get_dashboard_url(ResourceId='axb53q9y4xc80g-bd8c4383-8de6-44f3-a7df-c446803c845a', ResourceType='SESSION')
    #     session = requests.session()
    #     url = ret.get('Url', None)
    #     print(url)
    #     with requests.Session() as session:
    #         session.get(url, verify=False)
    #         for cookie in session.cookies:
    #             if cookie.name == 'VerifiedAuthToken':
    #                 expires = cookie.expires
    #                 print (expires)
    #         print (session.cookies.get('VerifiedAuthToken', None))

    # def serverless_test():
    #     application_id='00fm0aluav9roe0l'
    #     region = 'us-west-2'
    #     endpoint = f'https://{application_id}.livy.emr-serverless-services.{region}.amazonaws.com'
    #     emr_serverless_sigv4_header = get_sigv4_signed_header_for_emr_serverless(endpoint, region)
    #     canonical_uri = "/sessions"
    #     url=f'{endpoint}{canonical_uri}'
    #     response = requests.get(url, headers=emr_serverless_sigv4_header)
    #     # print(response.content.decode("utf-8"))
    #     res_json = json.loads(response.content.decode("utf-8"))
    #     # print(str(res_json))
    #     session_id = '1'
    #     spark_ui_url = None
    #     for livy_session in res_json['sessions']:
    #         print(str(livy_session['id']))
    #         if str(livy_session['id']) == session_id:
    #             spark_ui_url = livy_session['appInfo']['sparkUiUrl']
    #             # print(spark_ui_url)
    #             with requests.Session() as session:
    #                 session.get(spark_ui_url, verify=False)
    #                 emr_serverless_cookie = session.cookies.get('VerifiedAuthToken', None)
    #                 print(emr_serverless_cookie)
