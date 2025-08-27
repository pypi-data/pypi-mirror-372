import { getSMEnvironmentMetadata } from "./jupyter_api_client";

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

export class Environment {
  private static instance: Environment;
  private environment: any;


  static getInstance(): Environment {
    if (!Environment.instance || Environment.instance.environment == null) {
      Environment.instance = new Environment();
    }
    return Environment.instance;
  }

  async getEnvironmentMetadata(): Promise<EnvironmentMetadata> {
    return new Promise((resolve, reject) => {
      if (!Environment.instance.environment) {
        getSMEnvironmentMetadata()
          .then(env => {
            Environment.instance.environment = env
            resolve(Environment.instance.environment);
          });
      } else {
        resolve(Environment.instance.environment);
      }
    });
  }
}
