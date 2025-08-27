import { URLExt } from '@jupyterlab/coreutils';
import { Scheduler } from '@jupyterlab/scheduler';
import { ContentsManager, ServerConnection } from '@jupyterlab/services';
import { parseListSageMakerImagesAPIResponse } from '../../../utils';
import { FormState } from '../CreateNotebookJobform';

export interface IAutoDetectedConfig {
  name: string;
  label: string;
  description: string;
  value: any;
}

export type JobEnvironmentProps = Scheduler.IAdvancedOptionsProps & {
  isDisabled: boolean;
  executionEnvironments: {
    environment_configs: IAutoDetectedConfig[] | null;
    auto_detected_config: IAutoDetectedConfig[];
  };
  formState: FormState;
  formErrors: Scheduler.ErrorsType;
  setFormState: React.Dispatch<React.SetStateAction<FormState>>;
  setFormErrors: (errors: Scheduler.ErrorsType) => void;
  requestClient: ServerConnection.ISettings;
  contentsManager: ContentsManager;
}

export async function fetchKernelAndImages(requestClient: ServerConnection.ISettings) {
  const url = URLExt.join(requestClient.baseUrl, '/sagemaker_studio_jupyter_scheduler/sagemaker_images');
  const response = await ServerConnection.makeRequest(url, {}, requestClient);

  if (response.status !== 200) {
    return {};
  } else {
    return parseListSageMakerImagesAPIResponse(await response.json());
  }
}
