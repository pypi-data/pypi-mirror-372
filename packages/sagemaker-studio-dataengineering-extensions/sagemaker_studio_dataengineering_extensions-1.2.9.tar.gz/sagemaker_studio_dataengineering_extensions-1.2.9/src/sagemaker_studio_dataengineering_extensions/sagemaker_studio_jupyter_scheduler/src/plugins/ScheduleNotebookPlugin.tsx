import React from 'react';
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { Scheduler } from '@jupyterlab/scheduler';
import { pluginIds } from '../constants';
import { CreateNotebookJob } from '../widgets/CreateNotebookJob';
import { PluginEnvironmentProvider } from '../utils/PluginEnvironmentProvider';
import { ContentsManager } from '@jupyterlab/services';
import { StyledEngineProvider } from '@mui/material';


// This should only load up when the open source @jupyterlab/scheduler extension is installed and activated
// autoStart is set to false as this should only load when a plugin requests the Scheduler.IAdvancedOptions token
const ScheduleNotebookPlugin: JupyterFrontEndPlugin<Scheduler.IAdvancedOptions> = {
  id: pluginIds.SchedulerPlugin,
  autoStart: false,
  requires: [ISettingRegistry],
  provides: Scheduler.IAdvancedOptions,
  activate: (app: JupyterFrontEnd, settingRegistry: ISettingRegistry) => {
    return (props) => {
      const requestClient = app.serviceManager.serverSettings;
      const contentManagerClient = new ContentsManager();


      return (
        // {/* Inject Emotion before JSS */ }
        <StyledEngineProvider injectFirst>
          <PluginEnvironmentProvider app={app}>
            <CreateNotebookJob
              requestClient={requestClient}
              contentsManager={contentManagerClient}
              settingRegistry={settingRegistry}
              commands={app.commands}
              {...props}
            />
          </PluginEnvironmentProvider>
        </StyledEngineProvider >
      );
    };
  },
};

export { ScheduleNotebookPlugin };
