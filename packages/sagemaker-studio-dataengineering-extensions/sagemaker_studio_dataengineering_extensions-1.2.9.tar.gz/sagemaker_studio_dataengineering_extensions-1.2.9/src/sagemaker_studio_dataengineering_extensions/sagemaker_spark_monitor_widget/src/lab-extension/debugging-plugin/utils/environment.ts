// Local copy of environment utilities for debugging plugin
// This avoids cross-package dependencies

import { getSMEnvironmentMetadata, EnvironmentMetadata } from "./jupyter_api_client";

export class Environment {
  private static instance: Environment;
  private environment: EnvironmentMetadata | null = null;

  static getInstance(): Environment {
    if (!Environment.instance) {
      Environment.instance = new Environment();
    }
    return Environment.instance;
  }

  async getEnvironmentMetadata(): Promise<EnvironmentMetadata> {
    return new Promise((resolve, reject) => {
      if (!this.environment) {
        getSMEnvironmentMetadata()
          .then(env => {
            this.environment = env;
            resolve(this.environment);
          })
          .catch(error => {
            reject(error);
          });
      } else {
        resolve(this.environment);
      }
    });
  }
}

// Re-export the interface for convenience
export type { EnvironmentMetadata } from "./jupyter_api_client";
