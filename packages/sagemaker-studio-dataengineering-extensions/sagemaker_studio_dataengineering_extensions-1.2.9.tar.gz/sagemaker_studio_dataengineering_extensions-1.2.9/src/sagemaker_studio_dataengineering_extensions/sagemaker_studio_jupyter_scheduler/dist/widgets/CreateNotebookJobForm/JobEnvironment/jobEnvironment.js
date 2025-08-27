import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { parseListSageMakerImagesAPIResponse } from '../../../utils';
export async function fetchKernelAndImages(requestClient) {
    const url = URLExt.join(requestClient.baseUrl, '/sagemaker_studio_jupyter_scheduler/sagemaker_images');
    const response = await ServerConnection.makeRequest(url, {}, requestClient);
    if (response.status !== 200) {
        return {};
    }
    else {
        return parseListSageMakerImagesAPIResponse(await response.json());
    }
}
//# sourceMappingURL=jobEnvironment.js.map