import { JupyterFrontEnd } from '@jupyterlab/application';
import React from 'react';
export declare const STUDIO_SAGEMAKER_UI_PLUGIN_ID = "@amzn/sagemaker-ui:project";
export declare const JUPYTERLAB_SAGEMAKER_UI_PLUGIN_ID = "@amzn/sagemaker-jupyterlab-extensions:sessionmanagement";
declare enum PluginEnvironmentType {
    LocalJL = "local-jupyter-lab",
    JupyterLab = "jupyterlab",
    Studio = "studio"
}
declare class PluginEnvironment {
    readonly type: PluginEnvironmentType;
    get isStudio(): boolean;
    get isLocalJL(): boolean;
    get isJupyterLab(): boolean;
    get isStudioOrJupyterLab(): boolean;
    constructor(type: PluginEnvironmentType);
}
type PluginEnvironmentValue = {
    pluginEnvironment: PluginEnvironment;
    setPluginEnvironment: (state: PluginEnvironment) => void;
};
type PluginEnvironmentProviderProps = {
    app: JupyterFrontEnd;
    children: React.ReactNode;
};
declare function PluginEnvironmentProvider({ app, children }: PluginEnvironmentProviderProps): React.JSX.Element;
declare function usePluginEnvironment(): PluginEnvironmentValue;
export { PluginEnvironmentProvider, usePluginEnvironment, PluginEnvironment, PluginEnvironmentType };
//# sourceMappingURL=PluginEnvironmentProvider.d.ts.map