import React, { useState } from 'react';
import { LabIcon } from '@jupyterlab/ui-components';
import amazonQIconStr from '../../style/icons/amazon-q-icon.svg';
import debuggingButtonErrorIconStr from '../../style/icons/debugging-button-error-icon.svg';
import {TelemetryEventContext, TelemetryEventType, useTelemetryJL} from '../utils/telemetry';

/**
 * Simple spinner component for loading states
 */
const Spinner: React.FC = () => (
  <div className="jp-Spinner" />
);

/**
 * Define the Amazon Q icon as a LabIcon
 */
export const amazonQIcon = new LabIcon({
  name: 'invoke-agentic-q:amazon-q-icon',
  svgstr: amazonQIconStr,
});

/**
 * Define the debugging button error icon as a LabIcon
 */
export const debuggingButtonErrorIcon = new LabIcon({
  name: 'invoke-agentic-q:debugging-button-error-icon',
  svgstr: debuggingButtonErrorIconStr,
});

/**
 * Props for the DebuggingButton component
 */
export interface DebuggingButtonProps {
  cellId: string;
  debugging_info_folder: string;
  magicCommand: string;
  sessionType: string;
  instructionFile: string;
  commands: any;
  visible: boolean; 
}

const { recordBIEvent } = useTelemetryJL();

 async function recordInteractiveSparkDebuggingClickEvent(magicCommand: string, sessionType: string, cellId: string) {
      try {
        await recordBIEvent({
          eventType: TelemetryEventType.CLICK,
          eventContext: TelemetryEventContext.JL_CONNECTION,
          eventDetail: 'jl-cell-interactive-debugging-invoked',
          eventValue: JSON.stringify({
            magicCommand: magicCommand,
            sessionType: sessionType,
            cellId: cellId
          }),
        });
      } catch (error) {
        console.error('Error recording jl-cell-interactive-debugging-invoked BI event:', error);
      }
  }

   async function recordInteractiveSparkDebuggingRenderEvent(magicCommand: string, sessionType: string, cellId: string) {
      try {
        await recordBIEvent({
          eventType: TelemetryEventType.CHANGE,
          eventContext: TelemetryEventContext.JL_CONNECTION,
          eventDetail: 'jl-cell-interactive-debugging-rendered',
          eventValue: JSON.stringify({
            magicCommand: magicCommand,
            sessionType: sessionType,
            cellId: cellId
          }),
        });
      } catch (error) {
        console.error('Error recording jl-cell-interactive-debugging-invoked BI event:', error);
      }
  }

export const DebuggingButton: React.FC<DebuggingButtonProps> = ({ cellId, debugging_info_folder, magicCommand, sessionType, instructionFile, commands, visible }: DebuggingButtonProps) => {
  const [status, setStatus] = useState<string | null>(null); // null, 'loading', 'error', 'ready'
  const [message, setMessage] = useState<string>('');

  recordInteractiveSparkDebuggingRenderEvent(magicCommand, sessionType, cellId)
  
  const handleClick = async (): Promise<void> => {
    // Reset status and show loading message
    setStatus('loading');
    setMessage('Preparing file for diagnosis, this may take 5 to 10s.');
    recordInteractiveSparkDebuggingClickEvent(magicCommand, sessionType, cellId)
    try {
      const result = await commands.execute('sagemaker:diagnose-with-amazon-q', {
        cellId,
        debugging_info_folder,
        instructionFile
      });
      setStatus(result.status);
      setMessage(result.message || '');
    } catch (error) {
      setStatus('error');
      setMessage(`Error: ${error instanceof Error ? error.message : String(error)}. Rerun the cell and try again later.`);
    }
  };

  // If not visible, return null (don't render anything)
  if (!visible) {
    return null;
  }

  return (
    <div className="jp-DebuggingButton-container">
      <button 
        className="jp-DebuggingButton jp-ToolbarButtonComponent jp-mod-styled"
        onClick={handleClick}
        disabled={status === 'loading'}
      >
        <span className="jp-DebuggingButton-iconContainer">
          <amazonQIcon.react className="jp-icon-inline" tag="span" />
        </span>
        <span className="jp-DebuggingButton-text">Diagnose with Amazon Q</span>
      </button>
      
      {status === 'loading' && (
        <span className="jp-DebuggingButton-statusIcon">
          <Spinner />
        </span>
      )}
      
      {status === 'error' && (
        <span className="jp-DebuggingButton-statusIcon">
          <debuggingButtonErrorIcon.react className="jp-icon-inline" tag="span" />
        </span>
      )}
      
      {status && (
        <div className={status === 'error' ? 'jp-DebuggingButton-errorMessage' : 'jp-DebuggingButton-message'}>
          {message}
        </div>
      )}
    </div>
  );
};
