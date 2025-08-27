import * as EmrServerlessModel from "../models/emr-serverless-2021-07-13.normal.json";
import { SageMakerConnectionDetails } from "../utils/jupyter_api_client"
import { LINK_TYPE_SPARK_UI, LINK_TYPE_DRIVER_LOG } from '../constants';
import { createAwsClient } from "../utils/aws_client_utils"

export async function handleEMRServerlessDebuggingLinksClicked(connectionDetail: SageMakerConnectionDetails,
                                                         applicationId: string,
                                                         linkType: string):Promise<void> {
  const parts = connectionDetail.props.sparkEmrProperties.computeArn.split('/');
  const computeId = parts[parts.length - 1];

  const emrServerless = createAwsClient(connectionDetail, EmrServerlessModel, null);
  // gamma endpoint 
  // const emr = createAwsClient(connectionDetail, EmrServerlessModel, `https://emr-serverless-gamma.${region}.amazonaws.com`);
  
  // The Job Run ID is the YARN Application ID, while the compute ID taken from the computeArn is the serverless application ID
  let getDashboardForJobRunRequest: IGetDashboardForJobRunRequest = {
    applicationId: computeId,
    jobRunId: applicationId
  };
  
  return new Promise((resolve, reject) => {
    getDashboardForJobRun(emrServerless, getDashboardForJobRunRequest)
      .then(result => {
        if (linkType == LINK_TYPE_SPARK_UI) {
          window.open(result.url, '_blank');
        } else if (linkType == LINK_TYPE_DRIVER_LOG) {
          // Convert EMR serverless dashboard url to the driver log url
          // converts `https://j-<job-run-id>.dashboard.emr-serverless.<region>.amazonaws.com/?authToken=token`
          // to `https://j-<job-run-id>.dashboard.emr-serverless.<region>.amazonaws.com/logs/SPARK_DRIVER/stderr.gz?authToken=token`
          let driverLogUrl = result.url.replace("?authToken", "logs/SPARK_DRIVER/stderr.gz?authToken");
          window.open(driverLogUrl, '_blank');
        } else {
          console.log('Unknown link type clicked');
        }
        resolve();
      })
      .catch(error => {
        reject(error);
      });
  });
}

export async function getDashboardForJobRun(
  client: any,
  request: IGetDashboardForJobRunRequest
): Promise<IGetDashboardForJobRunResponse> {
  return new Promise((resolve, reject) => {
    client.getDashboardForJobRun(request, (err: any, data: any) => {
      if (err !== null) {
        reject(err);
      }
      resolve(data);
    });
  });
}

export interface IGetDashboardForJobRunRequest {
  applicationId: string;
  jobRunId: string;
  attempt?: number;
}

export interface IGetDashboardForJobRunResponse {
  url: string;
}
