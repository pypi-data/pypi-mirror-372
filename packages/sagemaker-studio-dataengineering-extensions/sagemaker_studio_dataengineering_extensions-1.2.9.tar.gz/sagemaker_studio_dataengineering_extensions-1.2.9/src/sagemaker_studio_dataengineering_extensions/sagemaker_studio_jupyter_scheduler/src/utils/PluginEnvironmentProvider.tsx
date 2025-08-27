import { JupyterFrontEnd } from '@jupyterlab/application';
import React, { createContext, useContext, useState } from 'react';

export const STUDIO_SAGEMAKER_UI_PLUGIN_ID = '@amzn/sagemaker-ui:project';
export const JUPYTERLAB_SAGEMAKER_UI_PLUGIN_ID = '@amzn/sagemaker-jupyterlab-extensions:sessionmanagement';

enum PluginEnvironmentType {
  LocalJL = 'local-jupyter-lab',
  JupyterLab = 'jupyterlab',
  Studio = 'studio',
}

class PluginEnvironment {

  public get isStudio(): boolean {
    return this.type === PluginEnvironmentType.Studio;
  }

  public get isLocalJL(): boolean {
    return this.type === PluginEnvironmentType.LocalJL;
  }

  public get isJupyterLab(): boolean {
    return this.type === PluginEnvironmentType.JupyterLab;
  }

  public get isStudioOrJupyterLab(): boolean {
    return this.isStudio || this.isJupyterLab;
  }

  constructor(
    public readonly type: PluginEnvironmentType,
  ) {
    console.debug(`PluginEnvironment created with type: ${type}`);
   }

}

function getPluginEnvironment(app: JupyterFrontEnd): PluginEnvironment {
  if (app.hasPlugin(STUDIO_SAGEMAKER_UI_PLUGIN_ID)) {
    return new PluginEnvironment(PluginEnvironmentType.Studio);
  }

  if (app.hasPlugin(JUPYTERLAB_SAGEMAKER_UI_PLUGIN_ID)
      || app.hasPlugin('@amzn/sagemaker-studio-scheduler:scheduler')) {
    return new PluginEnvironment(PluginEnvironmentType.JupyterLab);
  }

  return new PluginEnvironment(PluginEnvironmentType.LocalJL);
}

type PluginEnvironmentValue = {
  pluginEnvironment: PluginEnvironment;
  setPluginEnvironment: (state: PluginEnvironment) => void;
}

const PluginEnvironmentContext = createContext<PluginEnvironmentValue | undefined>(undefined);

type PluginEnvironmentProviderProps = {
  app: JupyterFrontEnd;
  children: React.ReactNode;
};

function PluginEnvironmentProvider({ app, children }: PluginEnvironmentProviderProps) {
  const [pluginEnvironment, setPluginEnvironment] = useState<PluginEnvironment>(() => {
    return getPluginEnvironment(app);
  });
  const value = { pluginEnvironment, setPluginEnvironment };
  return <PluginEnvironmentContext.Provider value={value}>{children}</PluginEnvironmentContext.Provider>
}

function usePluginEnvironment(): PluginEnvironmentValue {
  const context = useContext(PluginEnvironmentContext);
  if (context === undefined) {
    throw new Error('usePluginEnvironment must be used within a PluginEnvironmentProvider');
  }
  return context;
}

export { PluginEnvironmentProvider, usePluginEnvironment, PluginEnvironment, PluginEnvironmentType };
