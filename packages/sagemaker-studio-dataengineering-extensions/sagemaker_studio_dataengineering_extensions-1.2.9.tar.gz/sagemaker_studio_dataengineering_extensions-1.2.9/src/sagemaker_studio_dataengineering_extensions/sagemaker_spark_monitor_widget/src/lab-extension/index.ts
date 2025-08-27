/**
 * Entrypoint module for the SparkMonitor frontend extension.
 *
 * @module module
 */

import { INotebookTracker, NotebookTracker } from '@jupyterlab/notebook';
import { IMainMenu, MainMenu } from '@jupyterlab/mainmenu';
import SparkMonitor from './jupyterlab-sparkmonitor';
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { store } from '../store';
import { NotebookStore } from '../store/notebook';
import { IStateDB } from '@jupyterlab/statedb';
import { ReadonlyJSONObject } from '@lumino/coreutils';
import { INotebookTools } from '@jupyterlab/notebook';

import {
  ITranslator,
  nullTranslator,
} from '@jupyterlab/translation';

// Debugging plugin imports
import { YarnApplicationTableWidget } from "./debugging-plugin/widget";
import { Environment } from "./debugging-plugin/utils/environment";

export const PLUGIN_ID = 'jupyterlab_sparkmonitor'

/** Spark Monitor Plugin */
const sparkMonitorPlugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  autoStart: true,
  requires: [INotebookTracker, IMainMenu, IStateDB],
  optional: [ITranslator],
  activate(
    app: JupyterFrontEnd,
    notebooks: NotebookTracker,
    mainMenu: MainMenu,
    state: IStateDB,
    translator: ITranslator | null,
  ) {
    let monitor: SparkMonitor;
    console.log('JupyterLab SparkMonitor is activated!');
    notebooks.widgetAdded.connect(async (sender, nbPanel) => {
      let notebookStore = store.notebooks[nbPanel.id];
      if (!notebookStore) {
        notebookStore = new NotebookStore(nbPanel.id, translator || nullTranslator);

        store.notebooks[nbPanel.id] = notebookStore;
      }

      // JupyterLab 1.0 backwards compatibility
      let kernel;
      let info;
      if ((nbPanel as any).session) {
        await (nbPanel as any).session.ready;
        kernel = (nbPanel as any).session.kernel;
        await kernel.ready;
        info = kernel.info;
      } else {
        // JupyterLab 2.0
        const { sessionContext } = nbPanel;
        await sessionContext.ready;
        kernel = sessionContext.session?.kernel;
        info = await kernel?.info;
      }

      if (info.language_info.name === 'python' || info.implementation === 'PySpark') {
        monitor = new SparkMonitor(nbPanel, notebookStore, state, notebooks);
        console.log('Notebook kernel ready');
        monitor.startComm();
      }

      try {
        const value = await state.fetch(PLUGIN_ID);
        if (value) {
          // TODO handle multiple notebook for state
          const data = (value as ReadonlyJSONObject)['data'];
          const lastExecutedCellId = (value as ReadonlyJSONObject)['lastExecutedCellId'] as string;
          // console.log(`data ${data}, lastExecutedCellId ${lastExecutedCellId} read from state.`);
           
          const codeCell = monitor.getNoteBookPanel().content.widgets.find(
            widget => widget.model.id === lastExecutedCellId
          );
          if (!codeCell) {
            console.warn('SparkMonitor: last cell saved in state not exist.');
            return;
          }

          monitor.onHandleSparkData(data, lastExecutedCellId)
        }
      } catch (reason) {
        console.error(
                `Something went wrong when reading the state for ${PLUGIN_ID}.\n${reason}`
              );
      }
    });

    app.commands.commandExecuted.connect((registry, executed) => {
      if (executed.id === 'notebook:clear-all-cell-outputs') {
        monitor.clearAllData();
      }

      const activateCell = monitor.getActiveCell()
      if (executed.id === 'notebook:clear-cell-output' && activateCell && activateCell.model.id === monitor.getLastExecutedCellId()) {
        monitor.clearAllData();
      }
    });

    // const commandID = 'toggle-monitor';
    // let toggled = false;

    // app.commands.addCommand(commandID, {
    //   label: 'Hide Spark Monitoring',
    //   isEnabled: () => true,
    //   isVisible: () => true,
    //   isToggled: () => toggled,
    //   execute: () => {
    //     console.log(`Executed ${commandID}`);
    //     toggled = !toggled;
    //     monitor?.toggleAll();
    //   }
    // });

    // const menu = new Menu({ commands: app.commands });
    // menu.title.label = 'Spark';
    // menu.addItem({
    //   command: commandID,
    //   args: {}
    // });

    // mainMenu.addMenu(menu, false, { rank: 40 });
  }
};

/** Debugging Plugin */
const debuggingPlugin: JupyterFrontEndPlugin<void> = {
  id: 'sagemaker-debugging',
  description: 'JupyterLab extension to improve debugging experience in SageMaker.',
  requires: [INotebookTools, INotebookTracker],
  autoStart: true,
  activate: (app: JupyterFrontEnd, tools: INotebookTools, tracker: INotebookTracker) => {
    console.log('JupyterLab extension sagemaker-debugging is activated!');
    Environment.getInstance();
    const tableWidget = new YarnApplicationTableWidget();
    tableWidget.setListenerForNotebookChangeEvents(tracker);
    tableWidget.setCellExecutedSignal();
    tracker.currentChanged.connect(
      (tracker, panel) => tableWidget.onNotebookChange(tracker, panel),
      { id: 'sagemaker-debugging' }
    );
    tracker.widgetAdded.connect(
      (tracker, panel) => tableWidget.onNotebookChange(tracker, panel),
      { id: 'sagemaker-debugging' }
    );
  }
};

export default [
  sparkMonitorPlugin,
  debuggingPlugin
];
