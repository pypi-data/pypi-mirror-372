import { SageMakerConnectionDetails } from "./jupyter_api_client"
import { Credentials } from 'aws-sdk';
const AWS = require('aws-sdk');
import { SageMakerClient } from '@aws-sdk/client-sagemaker';

export function createAwsClient(
  connectionDetails: SageMakerConnectionDetails,
  serviceModel: any,
  endpoint: string | null
): any {
  let region = connectionDetails.physicalEndpoints[0].awsLocation.awsRegion;
  const accessRoleCredentials = connectionDetails.connectionCredentials;
  const credential = new Credentials(
    accessRoleCredentials.accessKeyId,
    accessRoleCredentials.secretAccessKey,
    accessRoleCredentials.sessionToken
  );
  let awsClient;
  if (endpoint == null) {
    awsClient = new AWS.Service({
      apiConfig: serviceModel,
      region: region,
      credentials: credential
    });
  } else {
    awsClient = new AWS.Service({
      apiConfig: serviceModel,
      region: region,
      credentials: credential,
      endpoint: endpoint
    });
  }
  
  return awsClient;
}

export function createSMClient(
  connectionDetails: SageMakerConnectionDetails,
  stage: string
): any {
  let region = connectionDetails.physicalEndpoints[0].awsLocation.awsRegion;
  const accessRoleCredentials = connectionDetails.connectionCredentials;
  const credential = new Credentials(
    accessRoleCredentials.accessKeyId,
    accessRoleCredentials.secretAccessKey,
    accessRoleCredentials.sessionToken
  );

  if (stage == "gamma") {
    return new SageMakerClient({
      region: region,
      credentials: credential,
      endpoint: `https://sagemaker.gamma.${region}.ml-platform.aws.a2z.com`
    });
  } else {
    return new SageMakerClient({
      region: region,
      credentials: credential,
    });
  }
}