import {
  createPersistentAppUI, describePersistentAppUI,
  getPersistentAppUIPresignedURL,
  IDescribePersistentAppUIResponse,
  IGetPersistentAppUIPresignedURLRequest,
  IPersistentAppUIArgs
} from '../computes/emr_ec2';

const MAX_WAIT_IN_SECONDS = 60;
const WAIT_SLEEP_IN_SECONDS = 5;
const MAX_RETRY = MAX_WAIT_IN_SECONDS / WAIT_SLEEP_IN_SECONDS;

export async function openPersistentAppUI(
  client: any,
  args: IPersistentAppUIArgs
): Promise<void> {
  const {
    applicationId: ApplicationId,
    targetResourceArn,
    executionRoleArn
  } = args;
  return createPersistentAppUI(client, targetResourceArn)
    .then(response => {
      return waitUntilPersistentAppUIReady(client, response.PersistentAppUIId);
    })
    .then(response => {
      const request: IGetPersistentAppUIPresignedURLRequest = {
        ApplicationId,
        PersistentAppUIId: response.PersistentAppUI.PersistentAppUIId,
        PersistentAppUIType: 'SHS',
        ExecutionRoleArn: executionRoleArn
      };
      return getPersistentAppUIPresignedURL(client, request);
    })
    .then(response => {
      if (response.PresignedURLReady) {
        window.open(response.PresignedURL, '_blank');
      }
    });
}

async function waitUntilPersistentAppUIReady(
  client: any,
  persistentAppUIId: string
): Promise<IDescribePersistentAppUIResponse> {
  let retryCount = 0;
  let timeElapsed = 0;
  const start = new Date().getTime();
  while (retryCount < MAX_RETRY && timeElapsed < MAX_WAIT_IN_SECONDS) {
    const response = await describePersistentAppUI(client, persistentAppUIId);
    if (response.PersistentAppUI.PersistentAppUIStatus !== 'ATTACHED') {
      await delay(WAIT_SLEEP_IN_SECONDS * 1000);
    } else {
      return response;
    }
    retryCount += 1;
    timeElapsed = (new Date().getTime() - start) / 1000;
  }
  return Promise.reject('Unable to transition to ATTACHED successfully');
}

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
