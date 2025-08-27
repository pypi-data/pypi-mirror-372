import { ISessionContext, SessionContext } from '@jupyterlab/apputils';
import { JobsView } from '@jupyterlab/scheduler';
import { ContentsManager, KernelSpec } from '@jupyterlab/services';
import { DropdownItem } from '../../../components/selectinput';
import { parseSpecName } from '../../../utils';
import { RuntimeEnvParams } from '../initialValueHelpers';
declare const constructArnName: (env: string, kernel: string, version: string | null) => string;
declare enum ImageGroup {
    Custom = "customImage",
    Sagemaker = "smeImage",
    Session = "session"
}
interface ImageMapValue {
    kernelOptions: DropdownItem[];
    versionOptions: DropdownItem[];
    arnEnvironment: string;
    label: string;
    group: ImageGroup;
    description?: string;
}
declare const createImageMap: (options: SessionContext.IKernelSearch) => {
    [key: string]: ImageMapValue;
};
export declare function getPreSelectedNotebookKernelSpec(filePath: string, contentsManager: ContentsManager): Promise<string>;
interface ParsedSpecDisplayName {
    imageName: string | null;
    kernelName: string | null;
}
declare function parseSpecDisplayName(displayName: string | undefined): ParsedSpecDisplayName;
declare function getImageOptionsFromMap(imageMap: {
    [key: string]: ImageMapValue;
}, group: ImageGroup, isFromCluster?: boolean): DropdownItem;
declare function getSessionOptionsFromMap(imageMap: {
    [key: string]: ImageMapValue;
}, prefered: ISessionContext.IKernelPreference): DropdownItem[];
export declare const getInitialImageValueForStudio: (runtimeEnvironmentParameters: RuntimeEnvParams, preSelectedKernelFromNotebook: string | undefined, view: JobsView) => import("../../../types/kernels").ParsedSpecName;
export declare function getImagesFromMap(options: KernelSpec.ISpecModels): Record<string, ImageMapValue>;
export { constructArnName, createImageMap, parseSpecName, parseSpecDisplayName, getImageOptionsFromMap, getSessionOptionsFromMap, ImageGroup, ImageMapValue, };
//# sourceMappingURL=studioHelpers.d.ts.map