import { ReactWidget, ToolbarButtonComponent } from '@jupyterlab/apputils';
import { CodeCell } from '@jupyterlab/cells';
import { HTMLSelect, refreshIcon } from '@jupyterlab/ui-components';
import React, { useState } from 'react';


import { Constants } from '../constants';
import {
  SageMakerConnectionSummary,
  createNewCellSourceForCell,
  getCellConnectionName,
  getCellInterpreterName,
  getComputeForInterpreter,
  getDefaultConnectionForInterpreter,
  getDefaultInterpreterForConnection,
} from '../utils/DropdownUtils';
import {TelemetryEventContext, TelemetryEventType, useTelemetryJL} from '../utils/telemetry';

interface IConnectionHeaderComponentProps {
  active: boolean;
  codeCell: CodeCell | undefined;
  interpreters: { label: string; value: string }[];
  connections: SageMakerConnectionSummary[];
  onRefresh?: () => Promise<void>;
  onConnectionChange?: (connectionName: string) => void;
}

export const ConnectionHeaderComponent = (props: IConnectionHeaderComponentProps): React.ReactElement => {
  const { active, codeCell } = props;
  const [interpreterName, setInterpreterName] = useState(getCellInterpreterName(codeCell));
  const [connectionName, setConnectionName] = useState(getCellConnectionName(codeCell));
  const { recordBIEvent } = useTelemetryJL();

  codeCell?.model.contentChanged.connect(() => {
    const connectionName = getCellConnectionName(codeCell);
    const connectionTypeName = getCellInterpreterName(codeCell);
    setConnectionName(connectionName);
    setInterpreterName(connectionTypeName);
  });

  const handleConnectionChange = (connectionName: string, interpreterName: string) => {
    setConnectionName(connectionName);
    if (codeCell) {
      const source = codeCell.model.sharedModel.source.trim();
      const connection = connectionName ? connectionName : Constants.DEFAULT_IAM_CONNECTION_NAME;
      const interpreter = getDefaultInterpreterForConnection(interpreterName, connection);
      const newSource = createNewCellSourceForCell(interpreter, connection, source);
      if (codeCell.editor) {
        codeCell.editor.model.sharedModel.setSource(newSource);
      }
    }
  };

  const handleInterpreterChange = (connectionName: string, interpreterName: string) => {
    setInterpreterName(interpreterName);
    if (codeCell) {
      const source = codeCell.model.sharedModel.source.trim();
      const interpreter = interpreterName ? interpreterName : Constants.INTERPRETER_LOCAL_PYTHON_VALUE;
      const connection = getDefaultConnectionForInterpreter(interpreterName, connectionName, props.connections);
      const newSource = createNewCellSourceForCell(interpreter, connection, source);
      if (codeCell.editor) {
        codeCell.editor.model.sharedModel.setSource(newSource);
      }
    }
  };

  return (
    <>
      {active && (
        <div className="jp-cell-header-content">
          <HTMLSelect
            options={props.interpreters}
            value={interpreterName}
            data-testid="language-dropdown"
            onChange={e => {
              handleInterpreterChange(connectionName, e.target.value);
              recordBIEvent({
                eventType: TelemetryEventType.CHANGE,
                eventContext: TelemetryEventContext.JL_CONNECTION,
                eventDetail: 'jl-language-select',
                eventValue: e.target.value,
              });
            }}
          />
          <HTMLSelect
            options={getComputeForInterpreter(interpreterName, props.connections)}
            value={connectionName}
            data-testid="connections-dropdown"
            onChange={e => {
              handleConnectionChange(e.target.value, interpreterName);
              recordBIEvent({
                eventType: TelemetryEventType.CHANGE,
                eventContext: TelemetryEventContext.JL_CONNECTION,
                eventDetail: 'jl-connection-select',
                eventValue: e.target.value,
              });
            }}
          />
          <ToolbarButtonComponent icon={refreshIcon} onClick={props.onRefresh} iconLabel="Refresh compute list" />
        </div>
      )}
    </>
  );
};

export class ConnectionHeaderWidget extends ReactWidget {
  props: IConnectionHeaderComponentProps = {
    active: false,
    codeCell: undefined,
    interpreters: [],
    connections: [],
  };

  constructor() {
    super();
    this.addClass('jp-connection-dropdown-widget');
  }

  public updateProps(props: IConnectionHeaderComponentProps): void {
    this.props = props;
    if (props.active) {
      this.addClass('jp-connection-dropdown-widget-active');
    } else {
      this.removeClass('jp-connection-dropdown-widget-active');
    }
    this.update();
  }

  public render(): React.ReactElement {
    return <ConnectionHeaderComponent {...this.props} />;
  }
}
