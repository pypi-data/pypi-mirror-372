import { SageMakerConnectionDetails } from "../utils/jupyter_api_client"
import * as EmrModel from '../models/elasticmapreduce-2009-03-31-private.normal.json';
import { LINK_TYPE_SPARK_UI, LINK_TYPE_DRIVER_LOG } from '../constants';
import { openPersistentAppUI } from '../utils/persistent_ui_utils';
import { createAwsClient } from "../utils/aws_client_utils"

export async function handleEMRonEc2DebuggingLinksClicked(connectionDetail: SageMakerConnectionDetails,
                                                               applicationId: string,
                                                               linkType: string,
                                                               logsLocation: string): Promise<void> {
  const executionRoleArn = connectionDetail.environmentUserRole;
  const parts = connectionDetail.props.sparkEmrProperties.computeArn.split('/');
  const computeId = parts[parts.length - 1];
  
  const emr = createAwsClient(connectionDetail, EmrModel, null);
  // gamma endpoint 
  // const emr = createAwsClient(connectionDetail, EmrModel, `https://elasticmapreduce-preprod.${region}.amazonaws.com`);

  return new Promise((resolve, reject) => {
    describeCluster(emr, computeId)
      .then(response => {
        const cluster = response.Cluster;
        if (cluster === undefined || cluster.ClusterArn === undefined) {
          return;
        }
        const targetResourceArn = cluster.ClusterArn;
        const isEMRClusterActive =
          !cluster.Status?.State?.startsWith('TERMINA');
        if (isEMRClusterActive) {
          getOnClusterAppUIPresignedURL(emr, {
            ClusterId: computeId,
            OnClusterAppUIType: 'ApplicationMaster',
            ApplicationId: applicationId,
            ExecutionRoleArn: executionRoleArn
          })
            .then(result => {
              if (result.PresignedURLReady) {
                if (linkType == LINK_TYPE_SPARK_UI) {
                  window.open(result.PresignedURL, '_blank');
                } else if (linkType == LINK_TYPE_DRIVER_LOG) {
                  // Convert application url to the driver log url
                  // converts `https://<cluster-id>.emrappui.<region>.amazonaws.com/proxy/<application_id>/?authToken=token`
                  // to `https://<cluster-id>.emrappui.<region>.amazonaws.com/nm/ip-172-31-23-43.ec2.internal:8042/node/containerlogs/container_1719256095706_0030_01_000001/livy/stderr/?authToken=token`

                  // 1. Prefix it with `/nm` and suffix it with `/stderr`
                  logsLocation =
                    '/nm/' +
                    logsLocation.slice('http://'.length) +
                    '/stderr';
                  // 2. Construct the driver log url
                  const presignedUrl = new URL(result.PresignedURL);
                  presignedUrl.pathname = logsLocation;
                  // Remove proxyapproved query parameter set for all the requests
                  presignedUrl.searchParams.delete('proxyapproved');
                  // Add `start=0` query parameter so that log file is display from the beginning.
                  presignedUrl.searchParams.set('start', '0');
                  const driverLogUrl = presignedUrl.toString();
                  window.open(driverLogUrl, '_blank');
                } else {
                  console.log('Unknown link type clicked');
                }
              }
              resolve();
            })
            .catch(error => {
              console.error(error);
              reject(error);
            });
        } else {
          let args: IPersistentAppUIArgs;
          if (executionRoleArn !== undefined) {
            args = {
              targetResourceArn: targetResourceArn,
              applicationId: applicationId,
              executionRoleArn: executionRoleArn
            };
          } else {
            args = {
              targetResourceArn: targetResourceArn,
              applicationId: applicationId
            };
          }
          resolve();
          if (linkType === LINK_TYPE_SPARK_UI) {
            return openPersistentAppUI(emr, args)
              .catch(error => {
                console.error(error);
                reject(error);
              })
          }
        }
      })
      .catch(e => {
        console.error(e);
        reject(e);
      });
  });
}
                                                               
export async function getOnClusterAppUIPresignedURL(
  emr: any,
  getOnClusterAppUIPresignedURLRequest: IGetOnClusterAppUIPresignedURLRequest
): Promise<any> {
  return new Promise((resolve, reject) => {
    emr.getOnClusterAppUIPresignedURL(
      getOnClusterAppUIPresignedURLRequest,
      (err: any, data: any) => {
        if (err !== null) {
          reject(err);
        }
        resolve(data);
      }
    );
  });
}

export async function describeCluster(
  client: any,
  clusterId: string
): Promise<any> {
  return new Promise((resolve, reject) => {
    client.describeCluster(
      {
        ClusterId: clusterId
      },
      (err: any, data: any) => {
        if (err !== null) {
          reject(err);
        }
        resolve(data);
      }
    );
  });
}

export async function createPersistentAppUI(
  client: any,
  targetResourceArn: string
): Promise<ICreatePersistentAppUIResponse> {
  return new Promise((resolve, reject) => {
    client.createPersistentAppUI(
      {
        TargetResourceArn: targetResourceArn,
        ProfilerType: 'SHS'
      },
      (err: any, data: any) => {
        if (err !== null) {
          reject(err);
        }
        resolve(data);
      }
    );
  });
}

export async function describePersistentAppUI(
  client: any,
  persistentAppUiId: string
): Promise<IDescribePersistentAppUIResponse> {
  return new Promise((resolve, reject) => {
    client.describePersistentAppUI(
      {
        PersistentAppUIId: persistentAppUiId
      },
      (err: any, data: any) => {
        if (err !== null) {
          reject(err);
        }
        resolve(data);
      }
    );
  });
}

export async function getPersistentAppUIPresignedURL(
  client: any,
  request: IGetPersistentAppUIPresignedURLRequest
): Promise<IPresignedURLResponse> {
  return new Promise((resolve, reject) => {
    client.getPersistentAppUIPresignedURL(request, (err: any, data: any) => {
      if (err !== null) {
        reject(err);
      }
      resolve(data);
    });
  });
}

export interface IPersistentAppUIArgs {
  targetResourceArn: string;
  applicationId?: string;
  executionRoleArn?: string;
}

export interface IPresignedURLResponse {
  PresignedURLReady: boolean;
  PresignedURL: string;
}

export interface IGetOnClusterAppUIPresignedURLRequest {
  ClusterId: string;
  OnClusterAppUIType: string;
  ApplicationId: string;
  ExecutionRoleArn: string;
}

export interface IGetPersistentAppUIPresignedURLRequest {
  PersistentAppUIId: string;
  PersistentAppUIType: string;
  ApplicationId?: string;
  AuthProxyCall?: boolean;
  ExecutionRoleArn?: string;
}
export interface ICreatePersistentAppUIResponse {
  PersistentAppUIId: string;
}
export interface IDescribePersistentAppUIResponse {
  PersistentAppUI: IPersistentAppUI;
}

interface ITag {
  Key: string;
  Value: string;
}

export interface IPersistentAppUI {
  PersistentAppUIId: string;
  PersistentAppUIStatus: string;
  PersistentAppUITypeList: string[];
  AuthorId: string;
  CreationTime: string;
  LastModifiedTime: string;
  LastStateChangeReason: string;
  Tags: ITag[];
}
