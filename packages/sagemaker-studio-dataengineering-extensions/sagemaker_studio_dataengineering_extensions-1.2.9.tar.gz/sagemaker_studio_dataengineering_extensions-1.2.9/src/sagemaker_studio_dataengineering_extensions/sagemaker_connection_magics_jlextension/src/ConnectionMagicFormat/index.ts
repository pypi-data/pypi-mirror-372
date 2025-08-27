import { JupyterFrontEnd, JupyterFrontEndPlugin, LabShell } from '@jupyterlab/application';
import { EditorExtensionRegistry, IEditorExtensionRegistry } from '@jupyterlab/codemirror';
import { NotebookPanel } from '@jupyterlab/notebook';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { Constants } from '../constants';
import { getMainPanels } from '../utils';
import { SageMakerConnectMagicExtension, updateSageMakerCodeMirrorExtensionForNotebook } from './FormatConnectMagic';

const CODE_MIRROR_SETTINGS_ID = '@jupyterlab/codemirror-extension:plugin';
const CODE_MIRROR_DEFAULT_CONFIG = 'defaultConfig';
const SAGEMAKER_CODE_MIRROR_EXTENSION = 'connect_magic_helper';
const SAGEMAKER_TO_DISPLAY_CONNECT_MAGIC_SETTING = 'toDisplayConnectMagic';
const SAGEMAKER_TO_EDIT_CONNECT_MAGIC_SETTING = 'toEditConnectMagic';
const TO_DISPLAY = 'toDisplay';
const TO_EDIT = 'toEdit';

export const codeMirrorPlugin: JupyterFrontEndPlugin<void> = {
  id: '@amzn/sagemaker-connection-magics-jlextension:connection-magic-format',
  description: 'A JupyterLab extension that makes the first line of code read only if it starts with %%connect',
  autoStart: true,
  requires: [IEditorExtensionRegistry, ISettingRegistry],
  activate: (app: JupyterFrontEnd, extensions: IEditorExtensionRegistry, settings: ISettingRegistry) => {
    console.log('sagemaker-connection-magics-jlextension:connection-magic-format activated!');
    // preload the connection list
    // avoid prolonged latency when kernel starts - the connection list are actually needed.
    const notebookPanels = new Set<string>();
    extensions.addExtension(
      Object.freeze({
        name: SAGEMAKER_CODE_MIRROR_EXTENSION,
        default: {
          toDisplay: true,
          toEdit: false,
        },
        schema: {
          title: 'Connection magics settings',
          type: 'object',
          properties: {
            toDisplay: {
              type: 'boolean',
              title: 'Display Connection magics',
            },
            toEdit: {
              type: 'boolean',
              title: 'Editable Connection magics',
            },
          },
          display: 'false',
        },
        factory: () =>
          EditorExtensionRegistry.createConfigurableExtension<Record<string, boolean>>(
            (config: Record<string, boolean>) => SageMakerConnectMagicExtension(config)
          ),
      })
    );

    function loadSageMakerSetting(sageMakerSetting: ISettingRegistry.ISettings): void {
      const toDisplay = sageMakerSetting.get(SAGEMAKER_TO_DISPLAY_CONNECT_MAGIC_SETTING).composite as boolean;
      const toEdit = sageMakerSetting.get(SAGEMAKER_TO_EDIT_CONNECT_MAGIC_SETTING).composite as boolean;
      console.log(
        `${Constants.SAGEMAKER_JUPYTER_PLUGIN_SETTINGS_ID} toDisplay set to: ${toDisplay}, toEdit set to: ${toEdit}`
      );
      Promise.all([app.restored]).then(() => {
        if (app.shell instanceof LabShell) {
          const mainNotebookPanels = getMainPanels(app);
          mainNotebookPanels.forEach(notebookPanel => {
            notebookPanels.add(notebookPanel.id);
            reconfigureCodeMirrorOnCellsOrKernelChange(notebookPanel);
          });

          app.shell.activeChanged.connect((sender, changed) => {
            const notebookPanel = changed.newValue;
            if (notebookPanel && notebookPanel instanceof NotebookPanel) {
              if (notebookPanels.has(notebookPanel.id)) return;
              reconfigureCodeMirrorOnCellsOrKernelChange(notebookPanel);
              notebookPanels.add(notebookPanel.id);
            }
          });
        }
      });

      Promise.all([app.restored, settings.load(CODE_MIRROR_SETTINGS_ID)])
        .then(([, codeMirrorSetting]) => {
          const codeMirrorRecord = codeMirrorSetting.get(CODE_MIRROR_DEFAULT_CONFIG).composite as Record<string, any>;
          const codeMirrorToDisplay = codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION] != undefined
            ? codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION][TO_DISPLAY] != undefined
              ? codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION][TO_DISPLAY]
              : true
            : true;
          const codeMirrorToEdit = codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION]
            ? codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION][TO_EDIT]
              ? codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION][TO_EDIT]
              : false
            : false;
          if (codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION] == undefined) {
            codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION] = {};
          }
          if (codeMirrorToDisplay != toDisplay || codeMirrorToEdit != toEdit) {
            codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION][TO_DISPLAY] = toDisplay;
            codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION][TO_EDIT] = toEdit;
            codeMirrorSetting.set(CODE_MIRROR_DEFAULT_CONFIG, codeMirrorRecord);
          }
        })
        .catch(reason => {
          console.error(`Something went wrong when reading the settings.\n${reason}`);
        });
    }

    function reconfigureCodeMirrorOnCellsOrKernelChange(notebookPanel: NotebookPanel): void {
      notebookPanel.model?.contentChanged.connect((cellList, cell) => {
        updateSageMakerCodeMirrorExtensionForNotebook(
          notebookPanel.content,
          notebookPanel.sessionContext.session?.kernel?.name
        );
      });
      notebookPanel.sessionContext.kernelChanged.connect((sessionContext, kernel) => {
        updateSageMakerCodeMirrorExtensionForNotebook(notebookPanel.content, kernel.newValue?.name);
      });
      notebookPanel.disposed.connect(() => {
        notebookPanels.delete(notebookPanel.id);
      });
    }

    function loadCodeMirrorSetting(codeMirrorSetting: ISettingRegistry.ISettings): void {
      const codeMirrorRecord = codeMirrorSetting.get(CODE_MIRROR_DEFAULT_CONFIG).composite as Record<string, any>;
      const toDisplay = codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION] != undefined
        ? codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION][TO_DISPLAY] != undefined
          ? codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION][TO_DISPLAY]
          : true
        : true;
      const toEdit = codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION]
        ? codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION][TO_EDIT]
          ? codeMirrorRecord[SAGEMAKER_CODE_MIRROR_EXTENSION][TO_EDIT]
          : false
        : false;
      console.log(`${CODE_MIRROR_SETTINGS_ID} ${SAGEMAKER_CODE_MIRROR_EXTENSION} ${TO_DISPLAY} set to: ${toDisplay}`);
      console.log(`${CODE_MIRROR_SETTINGS_ID} ${SAGEMAKER_CODE_MIRROR_EXTENSION} ${TO_EDIT} set to: ${toEdit}`);
      Promise.all([app.restored, settings.load(Constants.SAGEMAKER_JUPYTER_PLUGIN_SETTINGS_ID)])
        .then(([, sagemakerSetting]) => {
          const originalSagemakerToDisplaySetting = sagemakerSetting.get(SAGEMAKER_TO_DISPLAY_CONNECT_MAGIC_SETTING).composite as boolean;
          if (originalSagemakerToDisplaySetting != toDisplay) {
            sagemakerSetting.set(SAGEMAKER_TO_DISPLAY_CONNECT_MAGIC_SETTING, toDisplay);
          }
          const originalSagemakerToEditSetting = sagemakerSetting.get(SAGEMAKER_TO_EDIT_CONNECT_MAGIC_SETTING).composite as boolean;
          if (originalSagemakerToEditSetting != toEdit) {
            sagemakerSetting.set(SAGEMAKER_TO_EDIT_CONNECT_MAGIC_SETTING, toEdit);
          }
        })
        .catch(reason => {
          console.error(`Something went wrong when reading the settings.\n${reason}`);
        });
    }

    Promise.all([app.restored, settings.load(Constants.SAGEMAKER_JUPYTER_PLUGIN_SETTINGS_ID)])
      .then(([, setting]) => {
        loadSageMakerSetting(setting);
        setting.changed.connect(loadSageMakerSetting);
      })
      .catch(reason => {
        console.error(`Something went wrong when reading the settings.\n${reason}`);
      });

    Promise.all([app.restored, settings.load(CODE_MIRROR_SETTINGS_ID)])
      .then(([, setting]) => {
        loadCodeMirrorSetting(setting);
        setting.changed.connect(loadCodeMirrorSetting);
      })
      .catch(reason => {
        console.error(`Something went wrong when reading the settings.\n${reason}`);
      });
  },
};
