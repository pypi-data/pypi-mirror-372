import { Cell, CodeCell } from '@jupyterlab/cells';
import { DEFAULT_IAM_CONNECTION_NAME, CONNECT_CELL_MAGIC, CONNECTION_NAME_KEY, SPARK_MAGIC, PYSPARK_MAGIC, SCALASPARK_MAGIC, SQL_MAGIC } from './constants'

let connectionTypeMap: Record<string, string> = {};

function isEmpty(obj: object): boolean {
    return Object.keys(obj).length === 0;
}


export async function getConnectionTypeMap(forceUpdate: boolean = false) {
    if (isEmpty(connectionTypeMap) || forceUpdate) {
        connectionTypeMap = {}
        const response = await fetch(`/jupyterlab/default/api/aws/datazone/connections`);
        const connectionsResponse = await response.json();
        const connections = connectionsResponse.items

        connections.forEach((connection: { type: string; name: string | number; props: { sparkEmrProperties: { computeArn: string | string[]; }; }; }) => {
            if (connection.type == 'IAM' || connection.type == 'REDSHIFT' || connection.type == 'ATHENA') {
                connectionTypeMap[connection.name] = connection.type;
            } else if (connection.type == 'SPARK') {
                if ('sparkGlueProperties' in connection.props) {
                    connectionTypeMap[connection.name] = 'SPARK_GLUE';
                } else if ('sparkEmrProperties' in connection.props && 'computeArn' in connection.props.sparkEmrProperties) {
                    if (connection.props.sparkEmrProperties.computeArn.includes('cluster')) {
                        connectionTypeMap[connection.name] = 'SPARK_EMR_EC2';
                    } else if (connection.props.sparkEmrProperties.computeArn.includes('applications')) {
                        connectionTypeMap[connection.name] = 'SPARK_EMR_SERVERLESS';
                    }
                }
            }
        });
    }

    return connectionTypeMap;
}

export function getCellConnectionName(codeCell: CodeCell | Cell) {
    if (codeCell === undefined) {
        return false;
    }

    const cellLines = codeCell.model.sharedModel.source.trim().split('\n');
    if (cellLines.length > 0) {
        let cellConnectionName = DEFAULT_IAM_CONNECTION_NAME;

        const firstLine = cellLines[0];
        if (firstLine.includes(CONNECTION_NAME_KEY)) {
            cellConnectionName = firstLine.split(CONNECTION_NAME_KEY)[1].split(' ')[1];
        }
        else if (firstLine.includes(PYSPARK_MAGIC) || firstLine.includes(SCALASPARK_MAGIC)) {
            cellConnectionName = firstLine.split(' ')[1];
        } 
        return cellConnectionName
    }
    return undefined
}

export function isSparkCell(codeCell: CodeCell | Cell) {
    if (codeCell === undefined) {
        return false;
    }

    const cellLines = codeCell.model.sharedModel.source.trim().split('\n');
    if (cellLines.length > 0) {
        let cellConnectionName = DEFAULT_IAM_CONNECTION_NAME;

        const firstLine = cellLines[0];
        if (firstLine.includes(CONNECT_CELL_MAGIC)) {
            cellConnectionName = firstLine.split(CONNECTION_NAME_KEY)[1].split(' ')[1];

            // one single line magic was not submitting any code, thus not a spark cell
            if (cellLines.length > 1) {
                const secondLine = cellLines[1];
                if (secondLine.startsWith('%')) {
                    return false
                }
            }

            return isSparkConnection(cellConnectionName)
        }
        else if (firstLine.includes(SPARK_MAGIC) || firstLine.includes(PYSPARK_MAGIC) || firstLine.includes(SCALASPARK_MAGIC)) {
            // one single line magic was not submitting any code, thus not a spark cell
            if (cellLines.length > 1) {
                const secondLine = cellLines[1];
                if (secondLine.startsWith('%')) {
                    return false
                }
            }
            return true;
        } else if (firstLine.includes(SQL_MAGIC)) {
            const cellConnectionName = firstLine.split(' ')[1];
            return isSparkConnection(cellConnectionName)
        }
    }

    return false
}

function isSparkConnection(cellConnectionName: string) {
    let connection_type = connectionTypeMap[cellConnectionName]
    // force Update connection list if not found
    if (!connection_type) {
        getConnectionTypeMap(true)
        connection_type = connectionTypeMap[cellConnectionName]
    }

    if (connection_type && connection_type.startsWith('SPARK')) {
        return true;
    }

    return false;
}
