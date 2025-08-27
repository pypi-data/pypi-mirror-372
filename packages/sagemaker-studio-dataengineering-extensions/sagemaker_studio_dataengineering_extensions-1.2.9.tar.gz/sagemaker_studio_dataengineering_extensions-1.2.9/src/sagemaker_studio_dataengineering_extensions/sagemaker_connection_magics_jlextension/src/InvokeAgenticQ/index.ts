import React from 'react';
import ReactDOM from 'react-dom';

import { ILabShell, JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { IRenderMime } from '@jupyterlab/rendermime-interfaces';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { Widget } from '@lumino/widgets';

import { DebuggingButton } from './DebuggingButton';
import { Constants } from '../constants';

interface DebuggingInfoResponse {
  status: string;
}

interface ErrorResponse {
  error: string;
}

type WebviewMessage = {
   command: String,
   params: Record<string, unknown>
}

/**
 * Fetches debugging information for a cell
 */
async function fetchDebuggingInfo(cell_id: string): Promise<{ response?: DebuggingInfoResponse; error?: { status: number; message: string } }> {
  try {
    const response = await fetch(`/jupyterlab/default/api/debugging/info/${encodeURIComponent(cell_id)}`);
    
    const data = await response.json();
    
    if ('error' in data) {
      return { 
        error: { 
          status: response.status, 
          message: (data as ErrorResponse).error
        } 
      };
    }
    return { response: data as DebuggingInfoResponse };
  } catch (error) {
    return { 
      error: { 
        status: 0, 
        message: `Error fetching debugging info: ${error instanceof Error ? error.message : String(error)}` 
      } 
    };
  }
}

/**
 * Posts a message to the Amazon Q Chat UI
 */
const postToQChat = (payload: WebviewMessage, labShell: ILabShell) => {
  // locate the iframe which renders the Agentic UI. 
  const chatFrame = document.getElementById(
    'flare-iframe'
  ) as HTMLIFrameElement;

  if (!chatFrame || !chatFrame.contentWindow) {
    throw new Error('Amazon Q Chat UI not mounted');
  }

  // post payload to iframe
  chatFrame.contentWindow.postMessage(payload, window.location.origin);
  
  // ensure flare panel is visible in UI.
  labShell.activateById('flare-panel');
};

// Define the MIME type
const MIME_TYPE = 'application/sagemaker-interactive-debugging';

// Interface for the data structure
interface DebuggingData {
  cell_id: string;
  debugging_info_folder: string;
  magic_command: string;
  session_type: string;
  instruction_file: string;
}

/**
 * Widget that renders the MIME type
 */
class RenderedDebuggingWidget extends Widget implements IRenderMime.IRenderer {
  private readonly _mimeType: string;
  private readonly _app: JupyterFrontEnd;
  private _enableDebugging: boolean = false;
  private _lastModel: IRenderMime.IMimeModel | null = null;
  declare node: HTMLElement;

  constructor(options: IRenderMime.IRendererOptions, app: JupyterFrontEnd) {
    super();
    this._mimeType = options.mimeType;
    this._app = app;
  }

  /**
   * Set whether debugging is enabled and trigger a re-render if needed
   */
  setEnableDebugging(enabled: boolean): void {
    if (this._enableDebugging !== enabled) {
      this._enableDebugging = enabled;
      if (this._lastModel) {
        this.renderModel(this._lastModel);
      }
    }
  }

  dispose(): void {
    if (this.isDisposed) {
      return;
    }

    // Unmount React component when widget is disposed
    ReactDOM.unmountComponentAtNode(this.node);

    super.dispose();
  }

  renderModel(model: IRenderMime.IMimeModel): Promise<void> {
    // Store the model for later re-rendering
    this._lastModel = model;
    
    if (!model.data[this._mimeType]) {
      return Promise.resolve();
    }

    const data = model.data[this._mimeType] as unknown as DebuggingData;

    if (data && data.cell_id) {
      ReactDOM.render(
        React.createElement(DebuggingButton, { 
          cellId: data.cell_id,
          debugging_info_folder: data.debugging_info_folder,
          magicCommand: data.magic_command,
          sessionType: data.session_type,
          instructionFile: data.instruction_file,
          commands: this._app.commands,
          visible: this._enableDebugging // Pass visibility as a prop
        }),
        this.node
      );
    }

    return Promise.resolve();
  }
}

/**
 * Initialization data for the InvokeAgenticQ extension.
 */
export const invokeAgenticQPlugin: JupyterFrontEndPlugin<void> = {
  id: '@amzn/sagemaker-connection-magics-jlextension:invoke-agentic-q',
  autoStart: true,
  requires: [ILabShell, IRenderMimeRegistry, ISettingRegistry],
  activate: async (app: JupyterFrontEnd, labShell: ILabShell, rendermime: IRenderMimeRegistry, settings: ISettingRegistry) => {
    console.log('JupyterLab extension invoke-agentic-q is activated!');
    
    rendermime.removeMimeType(MIME_TYPE);
    
    let rendererFactory: IRenderMime.IRendererFactory = {
      safe: true,
      mimeTypes: [MIME_TYPE],
      createRenderer: (options: IRenderMime.IRendererOptions) => {
        const renderer = new RenderedDebuggingWidget(options, app);
        
        settings.load(Constants.SAGEMAKER_JUPYTER_PLUGIN_SETTINGS_ID)
          .then((setting: ISettingRegistry.ISettings) => {
            const enableDebugging = setting.get(Constants.USER_SETTING_ENABLE_INTERACTIVE_DEBUGGING).composite as boolean;
            renderer.setEnableDebugging(enableDebugging);
            
            setting.changed.connect(() => {
              const newValue = setting.get(Constants.USER_SETTING_ENABLE_INTERACTIVE_DEBUGGING).composite as boolean;
              renderer.setEnableDebugging(newValue);
            });
          })
          .catch((error: Error) => {
            console.error(`Error loading settings: ${error}`);
            renderer.setEnableDebugging(false);
          });
        
        return renderer;
      }
    };
    
    rendermime.addFactory(rendererFactory);
    
    // Register the command for debugging with Amazon Q
    const command = 'sagemaker:diagnose-with-amazon-q';
    app.commands.addCommand(command, {
      label: 'Diagnose with Amazon Q',
      caption: 'Send debugging information to Amazon Q for diagnosis',
      execute: async (args: any) => {
        const cellId = args['cellId'] as string;

        if (!cellId) {
          const errorMessage = 'cellId is required for the diagnose-with-amazon-q command';
          return {
            status: 'error',
            message: errorMessage
          };
        }
        
        // Use default value of "/home/sagemaker-user/src/.temp_sagemaker_unified_studio_debugging_info/${cellId}" if debugging_info_folder is not provided
        const debugging_info_folder = args['debugging_info_folder'] as string || `/home/sagemaker-user/src/.temp_sagemaker_unified_studio_debugging_info/${cellId}`;
        const instructionFile = args['instructionFile'] as string;
        
        console.log(`Command executed for cell: ${cellId}`);
        console.log(`Debugging info folder: ${debugging_info_folder}`);
        
        let status = 'loading';
        let message = 'Preparing file for diagnosis, this may take 5 to 10s.';
        
        // Make initial API call
        const initialResult = await fetchDebuggingInfo(cellId);
        
        // Handle any errors immediately without polling
        if (initialResult.error) {
          status = 'error';
          message = `${initialResult.error.message} To try again, run the cell and choose the button.`;
          return { status, message };
        }
        
        // If we have a successful response and status is ready, we're done
        if (initialResult.response && initialResult.response.status === 'ready') {
          status = 'ready';
          message = '';
          try {
            postToQChat({
              command: 'genericCommand',
              params: { 
                genericCommand: 'Fix',
                selection: `Follow the instructions in @${instructionFile}, and use the debugging info in @${debugging_info_folder}/debugging_info.json to diagnose issue.`, 
                triggerType: 'click' 
              }
            }, labShell);
          } catch (error) {
            status = 'error';
            message = `Failed to open Q chat panel due to ${error}. Retry it later.`;
          }
          return { status, message };
        }
        
        // If status is not ready, start polling
        const startTime = Date.now();
        const timeoutMs = 10000; // 10 seconds timeout
        const pollIntervalMs = 2000; // Poll every 2 seconds
        
        try {
          // Poll until debugging info is ready or timeout
          while (Date.now() - startTime < timeoutMs) {
            // Wait before polling again
            await new Promise(resolve => setTimeout(resolve, pollIntervalMs));
            
            const result = await fetchDebuggingInfo(cellId);
            
            // If we get any error during polling, stop and show error
            if (result.error) {
              status = 'error';
              message = `${result.error.message} To try again, run the cell and choose the button.`;
              return { status, message };
            }
            
            // If we have a successful response and status is ready, we're done
            if (result.response && result.response.status === 'ready') {
              status = 'ready';
              message = '';

              try {
                postToQChat({
                  command: 'genericCommand',
                  params: { 
                    genericCommand: 'Fix',
                    selection: `Follow the instructions in @${instructionFile}, and use the debugging info in @${debugging_info_folder}/debugging_info.json to diagnose issue.`,
                    triggerType: 'click' 
                  }
                }, labShell);
              } catch (error) {
                status = 'error';
                message = `Failed to open Q chat panel due to ${error}. Retry it later.`;
              }
              return { status, message };
            }
          }
          status = 'error';
          message = 'Failed to prepare the file. To try again, run the cell and choose the button.';
        } catch (error) {
          // Handle any unexpected errors
          status = 'error';
          message = `Error: ${error instanceof Error ? error.message : String(error)}. Rerun the cell and try again later.`;
        }
        
        return { status, message };
      }
    });
    console.log(`Registered MIME renderer for ${MIME_TYPE}`);
  }
};
