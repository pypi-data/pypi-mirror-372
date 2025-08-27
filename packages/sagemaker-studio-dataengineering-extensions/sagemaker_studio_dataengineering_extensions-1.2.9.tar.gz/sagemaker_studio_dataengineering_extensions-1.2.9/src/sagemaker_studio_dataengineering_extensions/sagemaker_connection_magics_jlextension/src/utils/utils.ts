import { JupyterFrontEnd } from '@jupyterlab/application';
import { NotebookPanel } from '@jupyterlab/notebook';

import { Constants } from '../constants';
import type { SageMakerEnv } from '../types';

/**
 * get all the Notebook Panel widgets within the shell's main section
 * @param app JupyterFrontEnd app
 * @returns array of main notebook panels
 */
export function getMainPanels(app: JupyterFrontEnd): NotebookPanel[] {
  const mainWidgets = Array.from(app.shell.widgets('main'));
  const mainNotebookPanels = mainWidgets.filter((widget): widget is NotebookPanel => widget instanceof NotebookPanel);
  return mainNotebookPanels;
}

export function isLocalhost() {
  return ['localhost', '127.0.0.1'].some(condition => document.location.href.includes(condition));
}

export async function getRepoName() {
  return await fetch(`${Constants.endpointPrefix}/jupyterlab/default/api/env`)
    .then(response => {
      return response.json();
    })
    .then((formattedResponse: SageMakerEnv) => {
      return formattedResponse.repository_name;
    });
}
