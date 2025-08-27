import React from 'react';
import { usePluginEnvironment } from '../../../utils/PluginEnvironmentProvider';
import { StudioJobEnvironment } from '../Studio/StudioJobEnvironment';
import { DefaultJobEnvironment } from './DefaultJobEnvironment';
import { JupyterLabJobEnvironment } from './JupyterLabJobEnvironment';
export const JobEnvironmentContainer = (props) => {
    const { pluginEnvironment } = usePluginEnvironment();
    return (React.createElement(React.Fragment, null,
        pluginEnvironment.isStudio && (React.createElement(StudioJobEnvironment, { ...props })),
        pluginEnvironment.isJupyterLab && (React.createElement(JupyterLabJobEnvironment, { ...props })),
        pluginEnvironment.isLocalJL && (React.createElement(DefaultJobEnvironment, { ...props }))));
};
//# sourceMappingURL=JobEnvironmentContainer.js.map