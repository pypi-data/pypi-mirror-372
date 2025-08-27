import type { AwsCredentialIdentity, Provider } from '@aws-sdk/types';

import type { Credentials } from '../../types';
import { endpointPrefix } from '../index';

export const getCredentials = (): Provider<AwsCredentialIdentity> => {
  return async () => {
    const response = await fetch(`${endpointPrefix}/jupyterlab/default/api/creds`);

    if (!response.ok) {
      return Promise.reject((await response.json() as Error)?.message);
    }

    const formattedResponse = (await response.json()) as Credentials;

    const iamCredentials = {
      accessKeyId: formattedResponse.access_key,
      secretAccessKey: formattedResponse.secret_key,
      sessionToken: formattedResponse.session_token,
      expiration: new Date(Date.now() + 1000 * 60 * 5), // 5 minutes
    };

    if (iamCredentials) {
      return Promise.resolve(iamCredentials);
    }
    return Promise.reject('Credentials not found or expired');
  };
};
