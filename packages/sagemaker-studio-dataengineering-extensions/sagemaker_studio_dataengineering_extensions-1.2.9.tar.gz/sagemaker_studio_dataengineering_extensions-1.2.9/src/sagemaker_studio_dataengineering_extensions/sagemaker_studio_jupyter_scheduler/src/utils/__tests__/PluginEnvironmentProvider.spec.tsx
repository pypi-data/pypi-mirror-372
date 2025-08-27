import { JupyterFrontEnd } from '@jupyterlab/application';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { PluginEnvironment, PluginEnvironmentProvider, PluginEnvironmentType, STUDIO_SAGEMAKER_UI_PLUGIN_ID, usePluginEnvironment } from '../PluginEnvironmentProvider';

let mockApp: JupyterFrontEnd;
let pluginEnvironment: PluginEnvironment;

const PluginEnvironmentProviderTester = () => {
  const instance = usePluginEnvironment();
  pluginEnvironment = instance.pluginEnvironment;
  return <>{pluginEnvironment.type}</>;
};

function mountProvider() {
  return render(<PluginEnvironmentProvider app={mockApp}>
    <PluginEnvironmentProviderTester />
  </PluginEnvironmentProvider>);
}

describe('PluginEnvironmentProvider', () => {
  beforeEach(() => {
    mockApp = {
      hasPlugin: jest.fn().mockReturnValue(false),
      listPlugins: jest.fn().mockReturnValue([]),
    } as unknown as JupyterFrontEnd;
  });

  it('initializes correctly with LocalJL plugin environment', () => {
    mountProvider();

    expect(screen.getByText(PluginEnvironmentType.LocalJL)).toBeInTheDocument()
    expect(pluginEnvironment).toBeDefined();
    expect(pluginEnvironment.type).toEqual(PluginEnvironmentType.LocalJL);
    expect(pluginEnvironment.isStudio).toBeFalsy();
    expect(pluginEnvironment.isLocalJL).toBeTruthy();
  });

  it('initializes correctly with Studio plugin environment', () => {
    mockApp.hasPlugin = (plugin: string) => plugin === STUDIO_SAGEMAKER_UI_PLUGIN_ID;
    mountProvider();

    expect(screen.getByText(PluginEnvironmentType.Studio)).toBeInTheDocument()
    expect(pluginEnvironment.type).toEqual(PluginEnvironmentType.Studio);
    expect(pluginEnvironment.isStudio).toBeTruthy();
    expect(pluginEnvironment.isLocalJL).toBeFalsy();
  });
});
