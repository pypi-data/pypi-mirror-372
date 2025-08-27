import type { JupyterFrontEnd } from '@jupyterlab/application';
import { IThemeManager, ReactWidget } from '@jupyterlab/apputils';
import { DocumentManager } from '@jupyterlab/docmanager';
import { NotebookTracker } from '@jupyterlab/notebook';
import React from 'react';

import DataExplorerWidget from './components/DataExplorerWidget';
import { type Connection, type EnvResponse, type NodeData } from './types';
import { endpointPrefix, getJupyterLabMenuItems } from './utils';
import { getCredentials } from './utils/getCredentials';

export class DataSourceExplorerWidget extends ReactWidget {
  private app: JupyterFrontEnd;
  private connections: Connection[] = [];
  private docManager: DocumentManager;
  private metadata = {
    projectId: '',
    domainId: '',
    region: '',
    envId: '',
    userId: '',
    dzEndpoint: '',
    dzRegion: '',
    dzStage: '',
    enabledFeatures: [] as string[],
  };
  private notebookTracker: NotebookTracker;
  private theme: IThemeManager;

  constructor({ app, docManager, notebooks, theme }: { app: JupyterFrontEnd, docManager: DocumentManager, notebooks: NotebookTracker, theme: IThemeManager }) {
    super();
    this.addClass('md-de-container');
    this.fetchConnections();
    this.fetchEnv();
    this.app = app;
    this.docManager = docManager;
    this.notebookTracker = notebooks;
    this.theme = theme;
    this.theme.themeChanged.connect((sender, theme_name) => {
      // refresh the widget when the theme changes
      this.render();
    });
  }

  private fetchEnv() {
    fetch(`${endpointPrefix}/jupyterlab/default/api/env`)
      .then(response => response.json())
      .then((formattedResponse: EnvResponse) => {
        this.metadata = {
          domainId: formattedResponse.domain_id,
          projectId: formattedResponse.project_id,
          region: formattedResponse.aws_region,
          envId: formattedResponse.environment_id,
          userId: formattedResponse.user_id,
          dzEndpoint: formattedResponse.dz_endpoint || `https://datazone.${formattedResponse.dz_region}.api.aws`,
          dzStage: formattedResponse.dz_stage,
          dzRegion: formattedResponse.dz_region,
          enabledFeatures: formattedResponse.enabled_features || [],
        };
        if (Object.values(this.metadata).some(item => !item))
          throw new Error('Missing required metadata from the response');
      })
      .catch(error => console.error(`[DataSourceExplorerWidget] an error occurred: `, error));
  }

  private fetchConnections() {
    fetch(`${endpointPrefix}/jupyterlab/default/api/aws/datazone/connections`)
      .then(response => response.json())
      .then((formattedResponse: {items: Connection[]}) => {
        this.connections = formattedResponse.items;
      })
      .catch(error => console.error(`[DataSourceExplorerWidget] an error occurred: `, error));
  }

  render(): JSX.Element {
    const isLightTheme = this.theme.theme ? this.theme.isLight(this.theme.theme) : false;
    const defaultMode = isLightTheme ? 'light' : 'dark';

    return (
      <DataExplorerWidget
        {...{
          domId: 'data-explorer-widget-in-jl',
          consumerType: 'jupyter-lab',
          credentialProvider: getCredentials(),
          envMetaData: this.metadata,
          stage: this.metadata.dzStage,
          themeConfig: { defaultMode: defaultMode },
          dataExplorerProps: {
            menuItems: (nodeData?: NodeData) => {
              const isQueryWithJupyterLabFeatureEnabled = this.metadata.enabledFeatures.includes('feature-data-explorer-query-jupyterlab');
              return isQueryWithJupyterLabFeatureEnabled ? 
                getJupyterLabMenuItems({
                  app: this.app,
                  connections: this.connections,
                  docManager : this.docManager,
                  notebookTracker: this.notebookTracker,
                  nodeData
                }) : [];
            },
          }
        }}
      />
    );
  }
}
