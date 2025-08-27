import React from 'react';
import { usePluginEnvironment } from '../../../utils/PluginEnvironmentProvider';
import { StudioJobEnvironment } from '../Studio/StudioJobEnvironment';
import { DefaultJobEnvironment } from './DefaultJobEnvironment';
import { JobEnvironmentProps } from './jobEnvironment';
import { JupyterLabJobEnvironment } from './JupyterLabJobEnvironment';

export const JobEnvironmentContainer: React.FC<JobEnvironmentProps> = (props) => {
  const { pluginEnvironment } = usePluginEnvironment();

  return (<>
    {pluginEnvironment.isStudio && (
      <StudioJobEnvironment
        {...props}
      ></StudioJobEnvironment>
    )}

    {pluginEnvironment.isJupyterLab && (
      <JupyterLabJobEnvironment
        {...props}
      ></JupyterLabJobEnvironment>
    )}

    {pluginEnvironment.isLocalJL && (
      <DefaultJobEnvironment
        {...props}
      ></DefaultJobEnvironment>
    )}
  </>);
}
