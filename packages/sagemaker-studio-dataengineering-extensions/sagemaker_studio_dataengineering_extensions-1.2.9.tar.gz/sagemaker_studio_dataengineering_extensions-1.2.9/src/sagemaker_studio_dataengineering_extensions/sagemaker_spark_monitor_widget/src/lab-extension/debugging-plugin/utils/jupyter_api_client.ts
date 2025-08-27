// Local copy of jupyter_api_client utilities for debugging plugin
// This avoids cross-package dependencies and JupyterLab-specific imports

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

export interface EnvironmentMetadata {
  domain_id: string;
  project_id: string;
  aws_region: string;
  environment_id: string;
  repository_name: string;
  user_id: string;
  dz_stage: string;
  sm_domain_id: string;
  sm_space_name: string;
  sm_user_profile_name: string;
  sm_project_path: string;
}

export async function getConnectionDetails(connectionName: string): Promise<SageMakerConnectionDetails> {
  const response = await fetch(`/jupyterlab/default/api/aws/datazone/connection?name=${connectionName}`);
  return (await response.json()) as SageMakerConnectionDetails;
}

export async function getSMEnvironmentMetadata(): Promise<EnvironmentMetadata> {
  const response = await fetch(`/jupyterlab/default/api/env`);
  return (await response.json()) as EnvironmentMetadata;
}

export async function getSparkHistoryServerStatus(): Promise<GetSparkHistoryServerResponse> {
  const response = await fetch(`/jupyterlab/default/api/spark-history-server`);
  return (await response.json()) as GetSparkHistoryServerResponse;
}

export async function startSparkHistoryServer(eventLogsLocation: string): Promise<StartSparkHistoryServerResponse> {
  // Simplified version without JupyterLab dependencies
  const response = await fetch('/jupyterlab/default/api/spark-history-server', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      "command": "start",
      "s3Path": eventLogsLocation
    }),
  });
  return (await response.json()) as StartSparkHistoryServerResponse;
}
