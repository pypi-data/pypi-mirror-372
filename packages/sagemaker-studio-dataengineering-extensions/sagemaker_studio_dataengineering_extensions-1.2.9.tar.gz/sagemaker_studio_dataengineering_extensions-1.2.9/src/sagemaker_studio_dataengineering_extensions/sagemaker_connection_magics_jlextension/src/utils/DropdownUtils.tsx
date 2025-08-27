import { Cell, CodeCell } from '@jupyterlab/cells';
import { NotebookPanel } from '@jupyterlab/notebook';

import { Constants } from '../constants';

let userSetting: Map<string, string | boolean> = new Map();
userSetting.set(Constants.USER_SETTING_CONNECTION_KEY, Constants.DEFAULT_IAM_CONNECTION_NAME);
userSetting.set(Constants.USER_SETTING_INTERPRETER_KEY, Constants.INTERPRETER_PYSPARK_VALUE);
userSetting.set(Constants.USER_SETTING_ALWAYS_SHOW_CELL_LEVEL_SELECTION, false);
let cachedConnection: string = getDefaultConnection();
let cachedInterpreter: string = getDefaultInterpreter();
let connectionTypeMap: Record<string, string> = {};
let connectionList: SageMakerConnectionSummary[] = [];

export interface SageMakerConnectionSummary {
  name: string;
  type: string;
  enableTrustedIdentityPropagation: boolean;
}

export async function listDataZoneConnections(forceRefresh: boolean) {
  if (connectionList.length > 0 && !forceRefresh) {
    return connectionList;
  }
  let connections: any[];
  const connectionsWithType: SageMakerConnectionSummary[] = [];
  const response = await fetch(`/jupyterlab/default/api/aws/datazone/connections`);
  const connectionsResponse = await response.json();
  connections = connectionsResponse.items;
  connections.forEach(connection => {
    const enableTrustedIdentityPropagation = connection.physicalEndpoints[0]?.enableTrustedIdentityPropagation ?? false;
    if (
      connection.type == Constants.CONNECTION_TYPE_IAM ||
      connection.type == Constants.CONNECTION_TYPE_REDSHIFT ||
      connection.type == Constants.CONNECTION_TYPE_ATHENA
    ) {
      const conn: SageMakerConnectionSummary = { name: connection.name, type: connection.type, enableTrustedIdentityPropagation };
      connectionsWithType.push(conn);
      connectionTypeMap[connection.name] = connection.type;
    } else if (connection.type == Constants.CONNECTION_TYPE_SPARK) {
      if ('sparkGlueProperties' in connection.props) {
        const conn: SageMakerConnectionSummary = { name: connection.name, type: Constants.CONNECTION_TYPE_GLUE, enableTrustedIdentityPropagation };
        connectionsWithType.push(conn);
        connectionTypeMap[connection.name] = Constants.CONNECTION_TYPE_GLUE;
      } else if ('sparkEmrProperties' in connection.props && 'computeArn' in connection.props.sparkEmrProperties) {
        if (connection.props.sparkEmrProperties.computeArn.includes('cluster')) {
          const conn: SageMakerConnectionSummary = { name: connection.name, type: Constants.CONNECTION_TYPE_EMR_EC2, enableTrustedIdentityPropagation };
          connectionsWithType.push(conn);
          connectionTypeMap[connection.name] = Constants.CONNECTION_TYPE_EMR_EC2;
        } else if (connection.props.sparkEmrProperties.computeArn.includes('applications')) {
          const conn: SageMakerConnectionSummary = {
            name: connection.name,
            type: Constants.CONNECTION_TYPE_EMR_SERVERLESS,
            enableTrustedIdentityPropagation
          };
          connectionsWithType.push(conn);
          connectionTypeMap[connection.name] = Constants.CONNECTION_TYPE_EMR_SERVERLESS;
        }
      }
    }
  });
  connectionList = connectionsWithType;
  return connectionList;
}

export function getInterpreterList(connections: SageMakerConnectionSummary[]) {
  const result = [
    { label: 'Connection Type', value: '' },
    { label: '-', value: '-', disabled: true },
  ];
  let enableSpark = false;
  let enableSQL = false;
  let enableLocal = false;

  for (const index in connections) {
    const connection = connections[index];
    if (Constants.INTERPRETER_CONNECTION_TYPE_MAP[Constants.INTERPRETER_SQL_VALUE].includes(connection.type)) {
      enableSQL = true;
    }
    if (Constants.INTERPRETER_CONNECTION_TYPE_MAP[Constants.INTERPRETER_PYSPARK_VALUE].includes(connection.type)) {
      enableSpark = true;
    }
    if (Constants.INTERPRETER_CONNECTION_TYPE_MAP[Constants.INTERPRETER_LOCAL_PYTHON_VALUE].includes(connection.type)) {
      enableLocal = true;
    }
    if (enableLocal && enableSpark && enableSQL) {
      break;
    }
  }
  if (enableSpark) {
    result.push(
      { label: Constants.INTERPRETER_PYSPARK_DISPLAY_NAME, value: Constants.INTERPRETER_PYSPARK_VALUE },
      { label: Constants.INTERPRETER_SCALA_SPARK_DISPLAY_NAME, value: Constants.INTERPRETER_SCALA_SPARK_VALUE }
    );
  }
  if (enableSQL) {
    result.push({ label: Constants.INTERPRETER_SQL_DISPLAY_NAME, value: Constants.INTERPRETER_SQL_VALUE });
  }
  if (enableLocal) {
    result.push({
      label: Constants.INTERPRETER_LOCAL_PYTHON_DISPLAY_NAME,
      value: Constants.INTERPRETER_LOCAL_PYTHON_VALUE,
    });
  }
  return result;
}

export function getSqlOnlyConnections(connectionList: SageMakerConnectionSummary[]) {
  return connectionList.filter(
    connection =>
      connection.type == Constants.CONNECTION_TYPE_ATHENA || connection.type == Constants.CONNECTION_TYPE_REDSHIFT
  );
}

export function getSqlOnlyInterpreterList(connectionList: SageMakerConnectionSummary[]) {
  const result = [
    { label: 'Connection Type', value: '' },
    { label: '-', value: '-', disabled: true },
  ];
  const enableSQL = connectionList.some(connection =>
    Constants.INTERPRETER_CONNECTION_TYPE_MAP[Constants.INTERPRETER_SQL_VALUE].includes(connection.type)
  );

  if (enableSQL) {
    result.push({ label: Constants.INTERPRETER_SQL_DISPLAY_NAME, value: Constants.INTERPRETER_SQL_VALUE });
  }
  return result;
}

export function getComputeForInterpreter(interpreter: string, connectionList: SageMakerConnectionSummary[]) {
  const result = [{ label: 'Compute', value: '' }];
  const emrResult = [{ value: '-EMR-', disabled: true }];
  const glueResult = [{ value: '-Glue-', disabled: true }];
  const redshiftResult = [{ value: '-Redshift-', disabled: true }];
  const athenaResult = [{ value: '-Athena-', disabled: true }];
  const iamResult = [{ value: '-Local-', disabled: true }];
  for (const index in connectionList) {
    const connection = connectionList[index];
    const shouldEnable = shouldEnableConnectionForInterpreter(interpreter, connection.name);
    if (shouldEnable) {
      if (connection.type == Constants.CONNECTION_TYPE_GLUE) {
        glueResult.push({ value: connection.name, disabled: false });
      } else if (
        connection.type == Constants.CONNECTION_TYPE_EMR_SERVERLESS ||
        connection.type == Constants.CONNECTION_TYPE_EMR_EC2
      ) {
        emrResult.push({ value: connection.name, disabled: false });
      } else if (connection.type == Constants.CONNECTION_TYPE_ATHENA) {
        athenaResult.push({ value: connection.name, disabled: false });
      } else if (connection.type == Constants.CONNECTION_TYPE_REDSHIFT) {
        redshiftResult.push({ value: connection.name, disabled: false });
      } else if (connection.type == Constants.CONNECTION_TYPE_IAM) {
        if (connection.name == Constants.DEFAULT_IAM_CONNECTION_NAME) {
          iamResult.push({ value: Constants.DEFAULT_IAM_CONNECTION_DISPLAYNAME, disabled: false });
        } else {
          iamResult.push({ value: connection.name, disabled: false });
        }
      }
    }
  }
  return [
    ...result,
    ...(athenaResult.length == 1 ? [] : athenaResult.sort()),
    ...(emrResult.length == 1 ? [] : emrResult.sort()),
    ...(glueResult.length == 1 ? [] : glueResult.sort()),
    ...(iamResult.length == 1 ? [] : iamResult.sort()),
    ...(redshiftResult.length == 1 ? [] : redshiftResult.sort()),
  ];
}

export function shouldEnableConnectionForInterpreter(interpreter: string, connection: string) {
  const connectionType = connectionTypeMap[connection];
  const keys = Object.keys(Constants.INTERPRETER_CONNECTION_TYPE_MAP);
  if (keys.includes(interpreter)) {
    return Constants.INTERPRETER_CONNECTION_TYPE_MAP[interpreter].includes(connectionType);
  } else {
    return false;
  }
}

export function getDefaultInterpreterForConnection(interpreter: string, connection: string) {
  if (shouldEnableConnectionForInterpreter(interpreter, connection)) {
    return interpreter;
  }
  const connectionType = connectionTypeMap[connection];
  if (connectionType in Constants.CONNECTION_TYPE_INTERPRETER_MAP) {
    return Constants.CONNECTION_TYPE_INTERPRETER_MAP[connectionType][0];
  } else {
    return Constants.INTERPRETER_LOCAL_PYTHON_VALUE;
  }
}

export function getDefaultConnectionForInterpreter(
  interpreter: string,
  connection: string,
  connectionList: SageMakerConnectionSummary[]
) {
  if (shouldEnableConnectionForInterpreter(interpreter, connection)) {
    return connection;
  }
  const connectionNameList = connectionList.map(connection => connection.name);
  if (interpreter === Constants.INTERPRETER_SQL_VALUE) {
    if (connectionNameList.includes(Constants.DEFAULT_REDSHIFT_CONNECTION_NAME)) {
      return Constants.DEFAULT_REDSHIFT_CONNECTION_NAME;
    } else if (connectionNameList.includes(Constants.DEFAULT_ATHENA_CONNECTION_NAME)) {
      return Constants.DEFAULT_ATHENA_CONNECTION_NAME;
    } else if (connectionNameList.includes(Constants.DEFAULT_GLUE_COMPATIBILITY_CONNECTION_NAME)) {
      return Constants.DEFAULT_GLUE_COMPATIBILITY_CONNECTION_NAME;
    } else if (connectionNameList.includes(Constants.DEFAULT_SPARK_GLUE_CONNECTION_NAME_DEPRECATED)) {
      return Constants.DEFAULT_SPARK_GLUE_CONNECTION_NAME_DEPRECATED;
    } else if (connectionNameList.includes(Constants.DEFAULT_GLUE_FINE_GRAINED_CONNECTION_NAME)) {
      return Constants.DEFAULT_GLUE_FINE_GRAINED_CONNECTION_NAME;
    } else if (connectionNameList.includes(Constants.DEFAULT_ATHENA_CONNECTION_NAME_EXPRESS)) {
      return Constants.DEFAULT_ATHENA_CONNECTION_NAME_EXPRESS;
    } else {
      return '';
    }
  } else if (
    interpreter === Constants.INTERPRETER_SCALA_SPARK_VALUE ||
    interpreter === Constants.INTERPRETER_PYSPARK_VALUE
  ) {
    if (connectionNameList.includes(Constants.DEFAULT_GLUE_COMPATIBILITY_CONNECTION_NAME)) {
      return Constants.DEFAULT_GLUE_COMPATIBILITY_CONNECTION_NAME;
    } else if (connectionNameList.includes(Constants.DEFAULT_SPARK_GLUE_CONNECTION_NAME_DEPRECATED)) {
      return Constants.DEFAULT_SPARK_GLUE_CONNECTION_NAME_DEPRECATED;
    } else if (connectionNameList.includes(Constants.DEFAULT_GLUE_FINE_GRAINED_CONNECTION_NAME)) {
      return Constants.DEFAULT_GLUE_FINE_GRAINED_CONNECTION_NAME;
    } else if (connectionNameList.includes(Constants.DEFAULT_SPARK_GLUE_CONNECTION_NAME_EXPRESS)) {
      return Constants.DEFAULT_SPARK_GLUE_CONNECTION_NAME_EXPRESS;
    } else {
      return '';
    }
  } else if (interpreter === Constants.INTERPRETER_LOCAL_PYTHON_VALUE) {
    if (connectionNameList.includes(Constants.DEFAULT_IAM_CONNECTION_NAME)) {
      return Constants.DEFAULT_IAM_CONNECTION_DISPLAYNAME;
    } else if (connectionNameList.includes(Constants.DEFAULT_IAM_CONNECTION_NAME_EXPRESS)) {
      return Constants.DEFAULT_IAM_CONNECTION_NAME_EXPRESS;
    } else {
      return '';
    }
  } else {
    return '';
  }
}

export function getCellConnectionTypeFromConnectionName(connectionName: string) {
  if (connectionName === Constants.DEFAULT_IAM_CONNECTION_DISPLAYNAME) {
    return Constants.CONNECTION_TYPE_IAM;
  }
  return connectionTypeMap[connectionName];
}

export function getCellInterpreterName(codeCell: CodeCell | Cell | undefined) {
  let cellInterpreterName = Constants.INTERPRETER_LOCAL_PYTHON_VALUE;
  if (codeCell === undefined) {
    return cellInterpreterName;
  }
  const cellLines = codeCell.model.sharedModel.source.trim().split('\n');
  if (cellLines.length > 0 && cellLines[0].startsWith(Constants.CONNECT_CELL_MAGIC)) {
    const language = getCellLanguageName(codeCell);
    const connection = getCellConnectionName(codeCell);
    if (language == Constants.LANGUAGE_SCALA) {
      cellInterpreterName = Constants.INTERPRETER_SCALA_SPARK_VALUE;
    } else if (language == Constants.LANGUAGE_SQL) {
      cellInterpreterName = Constants.INTERPRETER_SQL_VALUE;
    } else if (
      language == Constants.LANGUAGE_PYTHON &&
      connectionTypeMap[connection] == Constants.CONNECTION_TYPE_IAM
    ) {
      cellInterpreterName = Constants.INTERPRETER_LOCAL_PYTHON_VALUE;
    } else if (language == Constants.LANGUAGE_PYTHON) {
      cellInterpreterName = Constants.INTERPRETER_PYSPARK_VALUE;
    }
  } else if (cellLines.length > 0 && cellLines[0].startsWith(Constants.CONNECT_SCALA_SPARK_CELL_MAGIC_ALIAS)) {
    cellInterpreterName = Constants.INTERPRETER_SCALA_SPARK_VALUE;
  } else if (cellLines.length > 0 && cellLines[0].startsWith(Constants.CONNECT_SQL_CELL_MAGIC_ALIAS)) {
    cellInterpreterName = Constants.INTERPRETER_SQL_VALUE;
  } else if (cellLines.length > 0 && cellLines[0].startsWith(Constants.CONNECT_PYSPARK_MAGIC_ALIAS)) {
    cellInterpreterName = Constants.INTERPRETER_PYSPARK_VALUE;
  } else if (cellLines.length > 0 && cellLines[0].startsWith(Constants.CONNECT_SPARK_MAGIC_ALIAS)) {
    cellInterpreterName = Constants.INTERPRETER_PYSPARK_VALUE;
  }
  return cellInterpreterName;
}

export function getCellConnectionName(codeCell: CodeCell | Cell | undefined) {
  let cellConnectionName = Constants.DEFAULT_IAM_CONNECTION_DISPLAYNAME;
  if (codeCell === undefined) {
    return cellConnectionName;
  }
  const cellLines = codeCell.model.sharedModel.source.trim().split('\n');
  if (cellLines.length > 0 && cellLines[0].startsWith(Constants.CONNECT_CELL_MAGIC)) {
    const firstLine = cellLines[0];
    if (firstLine.includes(Constants.CONNECTION_NAME_KEY)) {
      cellConnectionName = firstLine.split(Constants.CONNECTION_NAME_KEY)[1].split(' ')[1];
    } else {
      cellConnectionName = '';
    }
  } else if (cellLines.length > 0 && isCellStartWithSupportedMagics(cellLines[0])) {
    const firstLineParts = cellLines[0].split(/\s+/);
    if (firstLineParts.length == 1) {
      cellConnectionName = '';
    } else {
      cellConnectionName = firstLineParts[firstLineParts.length - 1];
    }
    const cellInterpreterName = getCellInterpreterName(codeCell);
    if (cellConnectionName.length == 0) {
      cellConnectionName = getDefaultConnectionForInterpreter(cellInterpreterName, cellConnectionName, connectionList);
    }
  }

  return cellConnectionName;
}

export function getCellLanguageName(codeCell: CodeCell | Cell | undefined) {
  let cellLanguageName = Constants.LANGUAGE_PYTHON;
  if (codeCell === undefined) {
    return cellLanguageName;
  }
  const cellLines = codeCell.model.sharedModel.source.trim().split('\n');
  if (cellLines.length > 0 && cellLines[0].startsWith(Constants.CONNECT_CELL_MAGIC)) {
    const firstLine = cellLines[0];
    if (firstLine.includes(Constants.CONNECTION_LANGUAGE_KEY)) {
      cellLanguageName = firstLine.split(Constants.CONNECTION_LANGUAGE_KEY)[1].split(' ')[1];
    } else {
      cellLanguageName = '';
    }
  }
  if (cellLines.length > 0 && cellLines[0].startsWith(Constants.CONNECT_SCALA_SPARK_CELL_MAGIC_ALIAS)) {
    cellLanguageName = Constants.LANGUAGE_SCALA;
  }
  if (cellLines.length > 0 && cellLines[0].startsWith(Constants.CONNECT_SQL_CELL_MAGIC_ALIAS)) {
    cellLanguageName = Constants.LANGUAGE_SQL;
  }
  return cellLanguageName;
}

export function setSettingUserSelection(key: string, value: string | boolean): void {
  userSetting.set(key, value);
}

export function getDefaultConnection(): string {
  return userSetting.get(Constants.USER_SETTING_CONNECTION_KEY) as string;
}

export function getDefaultInterpreter(): string {
  return userSetting.get(Constants.USER_SETTING_INTERPRETER_KEY) as string;
}

export function getDefaultShowCellLevelConnectionSelection(): boolean {
  return userSetting.get(Constants.USER_SETTING_ALWAYS_SHOW_CELL_LEVEL_SELECTION) as boolean;
}

export function setCachedConnectionAndLanguage(activeCell: CodeCell | Cell | undefined | null): void {
  if (!activeCell) {
    cachedConnection = getDefaultConnection();
    cachedInterpreter = getDefaultInterpreter();
    return;
  }
  cachedInterpreter = getCellInterpreterName(activeCell);
  cachedConnection = getCellConnectionName(activeCell);
}

export function getCachedInterpreter(): string {
  return cachedInterpreter;
}

export function getCachedConnection(): string {
  return cachedConnection;
}

export function isNewSageMakerSupportedNotebook(kernelName: String | undefined, notebookPanel: NotebookPanel): boolean {
  return kernelName === Constants.SAGEMAKER_MAGIC_SUPPORTED_KERNEL_NAME && notebookPanel.model?.cells.length == 1;
}

export function isSageMakerConnectionSupportedForNotebook(notebookPanel: NotebookPanel) {
  return notebookPanel.sessionContext.session?.kernel?.name === Constants.SAGEMAKER_MAGIC_SUPPORTED_KERNEL_NAME;
}

export function createNewCellSourceForCell(interpreter: string, connection: string, source: string) {
  let lines = source.split('\n');
  if (!isCellStartWithSupportedMagics(lines[0])) {
    lines = [Constants.CONNECT_LOCAL_MAGIC_ALIAS, ...lines];
  }
  if (lines.length == 2
      && (lines[1] === Constants.AUTO_GENERATED_COMMENT_PYTHON_SYNTAX
          || lines[1] === Constants.AUTO_GENERATED_COMMENT_SCALA_SYNTAX
          || lines[1] === Constants.AUTO_GENERATED_COMMENT_SQL_SYNTAX)) {
    lines.pop();
  }

  const newFirstLine = getMagicLineFromInterpreterAndConnection(interpreter, connection);
  const newLines = [...lines];
  // override default.local to default.iam
  if (connection == Constants.DEFAULT_IAM_CONNECTION_DISPLAYNAME) {
    connection = Constants.DEFAULT_IAM_CONNECTION_NAME;
  }

  if (
    connection === Constants.DEFAULT_IAM_CONNECTION_NAME &&
    interpreter === Constants.INTERPRETER_LOCAL_PYTHON_VALUE
  ) {
    // if using default iam, skip the %magic line
    newLines[0] = '';
  } else if (
    connection == Constants.DEFAULT_IAM_CONNECTION_NAME_EXPRESS &&
    interpreter == Constants.INTERPRETER_LOCAL_PYTHON_VALUE
  ) {
    // if using default iam, skip the %magic line
    newLines[0] = '';
  } else {
    newLines[0] = newFirstLine.trim();
  }
  if (newLines.length == 1) {
    newLines[1] = '';
  }

  if (newLines.length == 2
      && newLines[0].startsWith(Constants.CONNECT_PYSPARK_MAGIC_ALIAS)
      && newLines[1] === "") {
    newLines[1] = Constants.AUTO_GENERATED_COMMENT_PYTHON_SYNTAX
  } else if (newLines.length == 2
      && newLines[0].startsWith(Constants.CONNECT_SCALA_SPARK_CELL_MAGIC_ALIAS)
      && newLines[1] === "") {
    newLines[1] = Constants.AUTO_GENERATED_COMMENT_SCALA_SYNTAX
  } else if (newLines.length == 2
      && newLines[0].startsWith(Constants.CONNECT_SQL_CELL_MAGIC_ALIAS)
      && newLines[1] === "") {
    newLines[1] = Constants.AUTO_GENERATED_COMMENT_SQL_SYNTAX
  }

  if (newLines[0] == '') {
    newLines.shift();
  }
  return newLines.join('\n');
}


export function getMagicLineFromInterpreterAndConnection(interpreter: string, connection: string) {
  if (interpreter == Constants.INTERPRETER_SCALA_SPARK_VALUE) {
    return `${Constants.CONNECT_SCALA_SPARK_CELL_MAGIC_ALIAS} ${connection}\n`;
  } else if (interpreter == Constants.INTERPRETER_SQL_VALUE) {
    return `${Constants.CONNECT_SQL_CELL_MAGIC_ALIAS} ${connection}\n`;
  } else if (interpreter == Constants.INTERPRETER_PYSPARK_VALUE) {
    return `${Constants.CONNECT_PYSPARK_MAGIC_ALIAS} ${connection}\n`;
  } else {
    return `${Constants.CONNECT_LOCAL_MAGIC_ALIAS} ${connection}\n`;
  }
}

export function isCellStartWithSupportedMagics(source: string) {
  return (
    source.startsWith(Constants.CONNECT_CELL_MAGIC) ||
    source.startsWith(Constants.CONNECT_PYSPARK_MAGIC_ALIAS) ||
    source.startsWith(Constants.CONNECT_SPARK_MAGIC_ALIAS) ||
    source.startsWith(Constants.CONNECT_SCALA_SPARK_CELL_MAGIC_ALIAS) ||
    source.startsWith(Constants.CONNECT_SQL_CELL_MAGIC_ALIAS) ||
    source.startsWith(Constants.CONNECT_LOCAL_MAGIC_ALIAS)
  );
}
