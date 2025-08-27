export interface SageMakerCredentials {
    access_key: string;
    secret_key: string;
    session_token: string;
  }
  
  export interface SageMakerEnv {
    domain_id: string;
    project_id: string;
    aws_region: string;
    environment_id: string;
    repository_name: string;
    user_id: string;
    dz_endpoint: string;
    dz_stage: string;
  }
  
  export interface SageMakerMetadata {
    domainId: string;
    projectId: string;
    region: AwsRegion;
    envId: string;
    userId: string;
    repoUserName: string;
    dzEndpoint: string;
    dzStage: SageMakerStage;
  }
  
  // check why only these two regions or how we will keep this code
  // updated
  export type AwsRegion = 'us-west-2' | 'us-east-1';
  
  export type SageMakerStage = 'alpha' | 'beta' | 'gamma' | 'prod';