import * as GlueModel from "../models/glue-2017-03-31.normal.json";
import { SageMakerConnectionDetails, startSparkHistoryServer } from "../utils/jupyter_api_client"
import { LINK_TYPE_SPARK_UI, LINK_TYPE_DRIVER_LOG } from '../constants';
import { generatePresignedUrl } from '../utils/s3_utils';
import { createAwsClient, createSMClient } from "../utils/aws_client_utils"
import { CreatePresignedDomainUrlCommand } from '@aws-sdk/client-sagemaker';
import { Environment } from "../utils/environment"
export async function handleGlueDebuggingLinksClicked(connectionDetail: SageMakerConnectionDetails,
                                                               sessionId: string,
                                                               linkType: string,
                                                               logsLocation: string): Promise<void> {

  const env = await Environment.getInstance().getEnvironmentMetadata();
  return new Promise((resolve, reject) => {
    const glue = createAwsClient(connectionDetail, GlueModel, null);
    // gamma endpoint
    // const glue = createAwsClient(connectionDetail, GlueModel, `https://glue-gamma.${region}.amazonaws.com`);


    if (linkType == LINK_TYPE_SPARK_UI) {
      glue.getSession({
        Id: sessionId
      }, async function (err: any, sessionData: any) {
        if (err != null) {
          reject(err);
        }
        if (sessionData.Session.Status == "READY") {
          glue.getDashboardUrl({
            ResourceId: sessionId,
            ResourceType: "SESSION"
          }, function (err: any, data: any) {
            if (err != null) {
              reject(err);
            }
            window.open(data.Url, '_blank');
            resolve();
          });
        } else {
          try {
            let response = await startSparkHistoryServer(logsLocation);
            if (response.status == "running" || response.status == "started") {
              const sagemakerClient = createSMClient(connectionDetail, env.dz_stage);
              const params = {
                DomainId: env.sm_domain_id,
                UserProfileName: env.user_id,
                LandingUri: "app:JupyterLab:proxy/18080/?showIncomplete=true",
                SpaceName: env.sm_space_name
              };
              const command = new CreatePresignedDomainUrlCommand(params);
              const createPresignedDomainUrlResponse = await sagemakerClient.send(command);
              window.open(createPresignedDomainUrlResponse.AuthorizedUrl, '_blank');
              resolve();
            } else {
              throw new Error(`Error Starting the spark history server: ${response.message}`);
            }
          } catch (error) {
            console.error('Error while launching the history server:', error);
            reject(error);
          }
        }

      });
    } else if (linkType == LINK_TYPE_DRIVER_LOG) {
      generatePresignedUrl(connectionDetail, logsLocation)
        .then(result => {
          window.open(result, '_blank');
          resolve();
        }).catch(err => {
          reject(err);
        })
    }
  });
}