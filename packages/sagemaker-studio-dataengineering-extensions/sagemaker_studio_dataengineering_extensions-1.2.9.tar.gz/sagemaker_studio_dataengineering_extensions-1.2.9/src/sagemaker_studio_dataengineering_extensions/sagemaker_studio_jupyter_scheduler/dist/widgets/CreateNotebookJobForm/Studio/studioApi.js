import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
export async function fetchKernelAndImagesForStudio(requestClient) {
    const url = URLExt.join(requestClient.baseUrl, 'api/kernelspecs');
    const response = await ServerConnection.makeRequest(url, {}, requestClient);
    if (response.status !== 200) {
        return undefined;
    }
    else {
        const kernelSpecs = await response.json();
        return kernelSpecs;
    }
}
//# sourceMappingURL=studioApi.js.map