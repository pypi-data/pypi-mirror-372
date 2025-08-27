import React, { createContext, useContext, useState } from 'react';
export const STUDIO_SAGEMAKER_UI_PLUGIN_ID = '@amzn/sagemaker-ui:project';
export const JUPYTERLAB_SAGEMAKER_UI_PLUGIN_ID = '@amzn/sagemaker-jupyterlab-extensions:sessionmanagement';
var PluginEnvironmentType;
(function (PluginEnvironmentType) {
    PluginEnvironmentType["LocalJL"] = "local-jupyter-lab";
    PluginEnvironmentType["JupyterLab"] = "jupyterlab";
    PluginEnvironmentType["Studio"] = "studio";
})(PluginEnvironmentType || (PluginEnvironmentType = {}));
class PluginEnvironment {
    get isStudio() {
        return this.type === PluginEnvironmentType.Studio;
    }
    get isLocalJL() {
        return this.type === PluginEnvironmentType.LocalJL;
    }
    get isJupyterLab() {
        return this.type === PluginEnvironmentType.JupyterLab;
    }
    get isStudioOrJupyterLab() {
        return this.isStudio || this.isJupyterLab;
    }
    constructor(type) {
        this.type = type;
        console.debug(`PluginEnvironment created with type: ${type}`);
    }
}
function getPluginEnvironment(app) {
    if (app.hasPlugin(STUDIO_SAGEMAKER_UI_PLUGIN_ID)) {
        return new PluginEnvironment(PluginEnvironmentType.Studio);
    }
    if (app.hasPlugin(JUPYTERLAB_SAGEMAKER_UI_PLUGIN_ID)
        || app.hasPlugin('@amzn/sagemaker-studio-scheduler:scheduler')) {
        return new PluginEnvironment(PluginEnvironmentType.JupyterLab);
    }
    return new PluginEnvironment(PluginEnvironmentType.LocalJL);
}
const PluginEnvironmentContext = createContext(undefined);
function PluginEnvironmentProvider({ app, children }) {
    const [pluginEnvironment, setPluginEnvironment] = useState(() => {
        return getPluginEnvironment(app);
    });
    const value = { pluginEnvironment, setPluginEnvironment };
    return React.createElement(PluginEnvironmentContext.Provider, { value: value }, children);
}
function usePluginEnvironment() {
    const context = useContext(PluginEnvironmentContext);
    if (context === undefined) {
        throw new Error('usePluginEnvironment must be used within a PluginEnvironmentProvider');
    }
    return context;
}
export { PluginEnvironmentProvider, usePluginEnvironment, PluginEnvironment, PluginEnvironmentType };
//# sourceMappingURL=PluginEnvironmentProvider.js.map