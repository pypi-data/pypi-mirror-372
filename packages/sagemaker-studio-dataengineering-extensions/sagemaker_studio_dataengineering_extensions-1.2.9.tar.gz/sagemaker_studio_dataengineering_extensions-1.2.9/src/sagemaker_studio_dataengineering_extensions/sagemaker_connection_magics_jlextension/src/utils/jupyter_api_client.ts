
import { EnvironmentMetadata } from "./environment";
import { ServerConnection } from '@jupyterlab/services';
import { PageConfig } from '@jupyterlab/coreutils';

export interface SageMakerConnectionDetails {
  name: string;
  environmentIdentifier: string;
  type: string;
  connectionCredentials: Credentials;
  props: Props
  environmentUserRole: string;
  physicalEndpoints: AWSLocation[];
}

export interface Props {
  sparkEmrProperties:	SparkEmrProperties;
  sparkGlueProperties: SparkGlueProperties;
}

export interface AWSLocation {
  awsLocation:	LocationDetails;
}

export interface LocationDetails {
  awsRegion: string;
  awsAccountId: string;
}

export interface Credentials {
  accessKeyId: string;
  secretAccessKey: string;
  sessionToken: string;
}

export interface SparkEmrProperties {
  computeArn: string;
}

export interface SparkGlueProperties {
  glueVersion: string;
  workerType: string;
}

export interface GetSparkHistoryServerResponse {
  status: string;
  message: string;
}

export interface StartSparkHistoryServerResponse {
  status: string;
  spark_ui: string;
  message: string;
}

export async function getConnectionDetails(connectionName: string) {
  const response = await fetch(`/jupyterlab/default/api/aws/datazone/connection?name=${connectionName}`);
  return (await response.json()) as SageMakerConnectionDetails;

}

export async function getSMEnvironmentMetadata() {
  const response = await fetch(`/jupyterlab/default/api/env`);
  return (await response.json()) as EnvironmentMetadata;
}

export async function getSparkHistoryServerStatus() {
  const response = await fetch(`/jupyterlab/default/api/spark-history-server`);
  return (await response.json()) as GetSparkHistoryServerResponse;
}

export async function startSparkHistoryServer(eventLogsLocation: string) {
  const baseUrl = PageConfig.getBaseUrl();
  const url = `${baseUrl}api/spark-history-server`;
  const settings = ServerConnection.makeSettings({ baseUrl });
  const options = {
    method: 'POST',
    body: JSON.stringify({
      "command":"start",
      "s3Path": eventLogsLocation
    }),
  };
  const response = await ServerConnection.makeRequest(url, options, settings);
  return (await response.json()) as StartSparkHistoryServerResponse;
}