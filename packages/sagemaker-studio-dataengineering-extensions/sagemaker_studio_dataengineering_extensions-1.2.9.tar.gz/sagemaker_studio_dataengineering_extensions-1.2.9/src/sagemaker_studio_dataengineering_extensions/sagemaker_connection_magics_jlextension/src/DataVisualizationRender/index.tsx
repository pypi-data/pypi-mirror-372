import React from 'react'
import ReactDOM from 'react-dom';

import {JupyterFrontEnd, JupyterFrontEndPlugin} from '@jupyterlab/application';
import {INotebookTracker, NotebookPanel} from '@jupyterlab/notebook';
import {IRenderMimeRegistry} from '@jupyterlab/rendermime';
import {IRenderMime} from '@jupyterlab/rendermime-interfaces';
import {ISettingRegistry} from '@jupyterlab/settingregistry';
import {Widget} from '@lumino/widgets';

import {VisualizationWidget} from "./widget/DisplayWidget";
import {DisplayData} from "./utils/types";
import {Constants} from "../constants";

const MIME_TYPE = 'application/sagemaker-display';

class RenderedDisplayWidget extends Widget implements IRenderMime.IRenderer {
  private readonly _mimeType: string;
  private notebookTracker: INotebookTracker;

  constructor(options: IRenderMime.IRendererOptions, notebookTracker: INotebookTracker) {
    super();
    this._mimeType = options.mimeType;
    this.notebookTracker = notebookTracker;
  }

  dispose(): void {
    if (this.isDisposed) {
      return;
    }

    // Unmount React component when widget is disposed
    if (this.node) {
      ReactDOM.unmountComponentAtNode(this.node);
    }

    super.dispose();
  }

  renderModel(model: IRenderMime.IMimeModel): Promise<void> {
    if (!model.data[this._mimeType]) {
      return Promise.resolve();
    }

    const data = model.data[this._mimeType] as unknown as DisplayData;

    if (data && this.notebookTracker.currentWidget) {
      ReactDOM.render(
        <VisualizationWidget
          data={data}
          notebookPanel={this.notebookTracker.currentWidget}
        />,
        this.node
      );
    }

    return Promise.resolve();
  }
}

export const sagemakerDisplayMimeRender: JupyterFrontEndPlugin<void> = {
  id: 'sagemaker-display-mime-render',
  autoStart: true,
  requires: [IRenderMimeRegistry, INotebookTracker, ISettingRegistry],
  activate: async (app: JupyterFrontEnd, rendermime: IRenderMimeRegistry, notebookTracker: INotebookTracker, settings: ISettingRegistry) => {
    let isS3Default = false;
    let isKernelRestarting = false;
    const notebookSet = new Set<NotebookPanel>();

    const updateIsS3DefaultInKernel = (isS3Default: boolean, notebook: NotebookPanel | null) => {
      notebook?.sessionContext.ready.then(() => {
        notebook?.sessionContext.session?.kernel?.requestExecute({
          code: `get_ipython().user_ns["_sagemaker_visualization_use_s3_storage"]=${isS3Default ? "True" : "False"}`,
          stop_on_error: false,
          silent: true
        }).done;
      })
    }

    const setupNotebookListener = async (notebook: NotebookPanel | null) => {
      if (notebook) {
        await notebook.sessionContext.ready;
        await updateIsS3DefaultInKernel(isS3Default, notebook);
        if (!notebookSet.has(notebook)) {
          // Add status listener if it's a new notebook
          notebook.sessionContext.statusChanged.connect((_, status) => {
            if (status === 'restarting' || status === 'starting') {
              isKernelRestarting = true;
            } else if (status === 'idle' && isKernelRestarting) {
              isKernelRestarting = false;
              updateIsS3DefaultInKernel(isS3Default, notebook);
            }
          });
          notebookSet.add(notebook);
        }
      }
    };

    // Initial load of settings
    try {
      const setting = await settings.load(Constants.SAGEMAKER_JUPYTER_PLUGIN_SETTINGS_ID);
      isS3Default = setting.get(Constants.USER_SETTING_ALWAYS_USE_S3_STORAGE_IN_VISUALIZATION).composite as boolean;

      // Add settings change listener
      setting.changed.connect(() => {
        const newValue = setting.get(Constants.USER_SETTING_ALWAYS_USE_S3_STORAGE_IN_VISUALIZATION).composite as boolean;
        if (newValue !== isS3Default) {
          isS3Default = newValue;
          updateIsS3DefaultInKernel(newValue, notebookTracker.currentWidget);
        }
      });

      // Add listener on notebook switch
      notebookTracker.currentChanged.connect(async (_, notebook) => {
        await setupNotebookListener(notebook);
      });

      // Add listener on notebook create
      notebookTracker.widgetAdded.connect(async (_, notebook) => {
        await setupNotebookListener(notebook);
      });

      // Initial setup for the current notebook (if exists)
      if (notebookTracker.currentWidget) {
        await setupNotebookListener(notebookTracker.currentWidget);
      }
    } catch (reason) {
      console.error(`Something went wrong when reading the settings.\n${reason}`);
      isS3Default = false;
    }

    // Clean up existing renderer first
    rendermime.removeMimeType(MIME_TYPE);
    // Register renderer
    rendermime.addFactory({
      safe: true,
      mimeTypes: [MIME_TYPE],
      createRenderer: (options: IRenderMime.IRendererOptions) =>
        new RenderedDisplayWidget(options, notebookTracker)
    });
  }
};
