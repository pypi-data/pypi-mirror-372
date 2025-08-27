import type {AwsCredentialIdentity, Provider} from '@aws-sdk/types';

import {getConnectionDetails, getSMEnvironmentMetadata} from "../../../utils/jupyter_api_client";

export const getCredentials = (connectionName: string): Provider<AwsCredentialIdentity> => {
  return async () => {
    const connectionDetail = await getConnectionDetails(connectionName)

    const iamCredentials: AwsCredentialIdentity = {
      ...connectionDetail.connectionCredentials,
      expiration: new Date(Date.now() + 1000 * 60 * 5) // 5 minutes
    };

    if (iamCredentials) {
      return Promise.resolve(iamCredentials);
    }
    return Promise.reject('Credentials not found or expired');
  };
};

export const getRegion = (): Provider<string> => {
  return async () => {
    const metadata = await getSMEnvironmentMetadata()

    if (metadata && metadata.aws_region) {
      return Promise.resolve(metadata.aws_region);
    }
    return Promise.reject('Region not found');
  };
};
