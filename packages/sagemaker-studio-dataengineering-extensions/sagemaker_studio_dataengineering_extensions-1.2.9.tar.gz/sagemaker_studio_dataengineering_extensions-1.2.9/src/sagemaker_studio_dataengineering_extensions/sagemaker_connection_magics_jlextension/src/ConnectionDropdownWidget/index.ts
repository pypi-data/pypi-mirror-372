import { JupyterFrontEnd, type JupyterFrontEndPlugin, LabShell } from '@jupyterlab/application';
import { IEditorServices } from '@jupyterlab/codeeditor';
import { NotebookActions, NotebookPanel } from '@jupyterlab/notebook';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { Md5 } from 'ts-md5';


import { Constants } from '../constants';
import { getMainPanels } from '../utils';
import {
  getCellConnectionName,
  getCellConnectionTypeFromConnectionName,
  getCellLanguageName,
  listDataZoneConnections,
  setSettingUserSelection,
} from '../utils/DropdownUtils';
import {TelemetryEventContext, TelemetryEventType, useTelemetryJL} from '../utils/telemetry';
import { CellHeaderContentFactory } from './cellHeaderContentFactory';

export const connectionDropdownPlugin: JupyterFrontEndPlugin<NotebookPanel.IContentFactory> = {
  id: '@amzn/sagemaker-connection-magics-jlextension:connection-dropdown',
  provides: NotebookPanel.IContentFactory,
  requires: [IEditorServices, ISettingRegistry],
  autoStart: true,
  activate: (app: JupyterFrontEnd, editorServices: IEditorServices, settings: ISettingRegistry) => {
    console.log('sagemaker-connection-magics-jlextension:connection-dropdown is activated!');
    listDataZoneConnections(false);
    const editorFactory = editorServices.factoryService.newInlineEditor;

    const cellHeaderContentFactory = new CellHeaderContentFactory({
      editorFactory,
      app,
      editorServices,
    });

    // function to record cell execution BI event
    const { recordBIEvent } = useTelemetryJL();
    async function recordCellExecutionEvent(language: string, connectionType: string, notebook_name: string) {
      try {
        await recordBIEvent({
          eventType: TelemetryEventType.CHANGE,
          eventContext: TelemetryEventContext.JL_CONNECTION,
          eventDetail: 'jl-cell-executed',
          eventValue: JSON.stringify({
            language: language,
            connectionType: connectionType,
            notebook_name: Md5.hashStr(notebook_name),
          }),
        });
      } catch (error) {
        console.error('Error recording cell-execution BI event:', error);
      }
    }

    NotebookActions.executed.connect((_, args) => {
      const cell = args.cell;
      const connectionName = getCellConnectionName(cell);
      const connectionType = getCellConnectionTypeFromConnectionName(connectionName);
      const language = getCellLanguageName(cell);

      // @ts-ignore
      const notebook_name = args['notebook']._parent.context._path;

      recordCellExecutionEvent(language, connectionType, notebook_name);
    });

    Promise.all([app.restored, settings.load(Constants.SAGEMAKER_JUPYTER_PLUGIN_SETTINGS_ID)])
      .then(([, setting]) => {
        loadSetting(setting);
        setting.changed.connect(loadSetting);
      })
      .catch(reason => {
        console.error(`Something went wrong when reading the settings.\n${reason}`);
      });

    function loadSetting(setting: ISettingRegistry.ISettings): void {
      const alwaysShowCellLevelConnectionSelection = setting.get(
        Constants.USER_SETTING_ALWAYS_SHOW_CELL_LEVEL_SELECTION
      ).composite as boolean;
      setSettingUserSelection(
        Constants.USER_SETTING_ALWAYS_SHOW_CELL_LEVEL_SELECTION,
        alwaysShowCellLevelConnectionSelection
      );
      Promise.all([app.restored]).then(() => {
        if (app.shell instanceof LabShell) {
          const mainNotebookPanels = getMainPanels(app);
          mainNotebookPanels.forEach(notebookPanel => {
            cellHeaderContentFactory.updateHeaderContent(
              notebookPanel.content,
              notebookPanel.sessionContext.session?.kernel?.name,
              notebookPanel.content.activeCell?.model.id
            );
          });
        }
      });
    }
    return cellHeaderContentFactory;
  },
};
