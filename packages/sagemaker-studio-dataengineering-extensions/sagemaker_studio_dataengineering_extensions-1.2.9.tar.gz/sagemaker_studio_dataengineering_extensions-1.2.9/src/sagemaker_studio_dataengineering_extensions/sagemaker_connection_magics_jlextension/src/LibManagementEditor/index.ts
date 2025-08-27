import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { showErrorMessage } from '@jupyterlab/apputils';
import { IDocumentWidgetOpener } from '@jupyterlab/docmanager';
import { ILauncher } from '@jupyterlab/launcher';
import { Terminal as TerminalWidget } from '@jupyterlab/terminal';

import { getRepoName } from '../utils';
import { LibManagementDocumentManager } from './LibraryDocument/LibManagementDocumentManager';
import { LibraryEditorFactory } from './LibraryDocument/LibraryEditorFactory';
import { libMgmtIcon } from './config';
import { Environment } from "../utils/environment";

namespace CommandIDs {
  export const EDIT_LIBRARY_CONFIG = 'edit-library-config';
}

export const libManagementPlugin: JupyterFrontEndPlugin<void> = {
  id: '@amzn/sagemaker-connection-magics-jlextension:lib-management-editor',
  autoStart: true,
  optional: [ILauncher, IDocumentWidgetOpener],
  activate: (app: JupyterFrontEnd, launcher: ILauncher, widgetOpener: IDocumentWidgetOpener) => {
    const { commands, docRegistry } = app;

    const createTerminal = async () => {
      return await app.serviceManager.terminals.startNew();
    };

    const openTerminal = (terminalWidget: TerminalWidget) => {
      app.shell.add(terminalWidget, 'main', { activate: true });
    };

    const factory = new LibraryEditorFactory(
      {
        name: 'library-config-editor',
        fileTypes: ['file'],
        defaultFor: [],
      },
      createTerminal,
      openTerminal
    );
    docRegistry.addWidgetFactory(factory);

    const libManagementDocumentManager = new LibManagementDocumentManager({
      registry: docRegistry,
      manager: app.serviceManager,
      opener: widgetOpener,
    });

    const command = CommandIDs.EDIT_LIBRARY_CONFIG;
    commands.addCommand(command, {
      label: 'Library management',
      icon: args => (args['isPalette'] ? undefined : libMgmtIcon),
      execute: async () => {
        try {
          const env = await Environment.getInstance().getEnvironmentMetadata();
          const project_path = env.sm_project_path ?? "src";
          if (await libManagementDocumentManager.exist(project_path)) {
            await libManagementDocumentManager.openOrCreate(`${project_path}/.libs.json`, 'library-config-editor');
          } else {
            const repoName = await getRepoName();
            const repoPath = `${repoName}/.libs.json`;
            if (await libManagementDocumentManager.exist(repoName)) {
              await libManagementDocumentManager.openOrCreate(repoPath, 'library-config-editor');
            } else {
              throw Error('Repository folder not found');
            }
          }
        } catch (err) {
          showErrorMessage('Failed to open library config', (err as Error).message);
        }
      },
    });

    if (launcher) {
      launcher.add({
        command,
        category: 'Other',
        rank: 1,
      });
    }
  },
};
