import type { JupyterFrontEnd } from '@jupyterlab/application';
import { DocumentManager } from '@jupyterlab/docmanager';
import { NotebookActions, NotebookPanel, NotebookTracker } from '@jupyterlab/notebook';
import { AWS_DATA_CATALOG, DEFAULT_CONNECTION_NAME, OLD_DEFAULT_SPARK_CONNECTION_NAME, S3_NODE_TYPES } from "../constants";
import { ConnectionType, NodeType, type Connection, type NodeData } from "../types";

export function isLocalhost() {
  return ['localhost', '127.0.0.1'].some(condition => document.location.href.includes(condition));
}

export const endpointPrefix = isLocalhost() ? 'http://localhost:3000' : '';

export async function getOrCreateNotebook({
  app,
  docManager,
  notebookTracker
}: {
  app: JupyterFrontEnd,
  docManager: DocumentManager,
  notebookTracker: NotebookTracker
}) {
  // already an open notebook
  const notebook = notebookTracker.currentWidget;
  if (notebook) {
    // set as active tab
    await app.commands.execute('tabsmenu:activate-by-id', {
      id: notebook.id
    });
    return notebook;
  }
  // no notebook open, create a new untitled notebook
  const untitledNotebook = await docManager.newUntitled({ type: 'notebook' });
  await docManager.openOrReveal(untitledNotebook.path, 'default', { id: 'python3', name: 'python3' });
  // wait for new notebook to be added to the tracker
  const newNotebookPromise = new Promise<NotebookPanel>(resolve => {
    notebookTracker.widgetAdded.connect((_, widget) => {
      resolve(widget);
    });
  });
  const newNotebook = await newNotebookPromise;
  if (newNotebook) {
    return newNotebook;
  }
}

export async function onQueryWithJupyterLab({
  app,
  connections,
  connectionType,
  docManager,
  nodeData,
  notebookTracker
}: {
  app: JupyterFrontEnd,
  connections: Connection[],
  connectionType: ConnectionType,
  docManager: DocumentManager,
  nodeData: NodeData,
  notebookTracker: NotebookTracker
}) {
  const notebook = await getOrCreateNotebook({app, docManager, notebookTracker});
  if (notebook) {
    // insert new cell if active cell is not empty
    const isCellEmpty = notebook.content.activeCell?.model.sharedModel.source.trim() === "";
    if (!isCellEmpty) {
      NotebookActions.insertBelow(notebook.content);
    }
    const sqlQuery = getSQLQuery(connections, connectionType, nodeData);
    await notebook.revealed;
    notebook.content.activeCell?.model.sharedModel.setSource(sqlQuery);
  }
}

export function getJupyterLabMenuItems({
  app,
  connections,
  docManager,
  notebookTracker,
  nodeData
}: {
  app: JupyterFrontEnd,
  connections: Connection[],
  docManager: DocumentManager,
  notebookTracker: NotebookTracker,
  nodeData?: NodeData
}) {
  if (!nodeData) {
    return [];
  }
  const menuItems = [];
  const isContainer = nodeData.isContainer;
  const isS3Node = S3_NODE_TYPES.includes(nodeData.nodeType);
  const isTableNode = nodeData.nodeType === NodeType.Table && !!nodeData.path?.table;
  const isRedshiftNode = nodeData.connectionType === ConnectionType.REDSHIFT;
  if (isTableNode && !isContainer && !isS3Node) {
    const commonProps = {app, connections, docManager, nodeData, notebookTracker};
    if (isRedshiftNode) {
      menuItems.push({
        id: 'query-redshift',
        text: 'Preview data',
        onClickItem: () => onQueryWithJupyterLab({...commonProps, connectionType: ConnectionType.REDSHIFT})
      });
    } else {
      menuItems.push(
        ...[
          {
            id: 'query-athena',
            text: 'Preview data',
            onClickItem: () => onQueryWithJupyterLab({...commonProps, connectionType: ConnectionType.ATHENA})
          },
          {
            id: 'query-spark',
            text: 'Query with Spark',
            onClickItem: () => onQueryWithJupyterLab({...commonProps, connectionType: ConnectionType.SPARK})
          }
        ]
      );
    }
  }
  return menuItems;
}

function getDefaultConnectionName(connections: Connection[], connectionType: ConnectionType) {
  let defaultConnectionName;

  // check edge case for older projects that only have`project.spark`connection
  const oldDefaultSparkConnectionExists = 
    connections.find(connection => connection.name === OLD_DEFAULT_SPARK_CONNECTION_NAME);
  if (connectionType === ConnectionType.SPARK && oldDefaultSparkConnectionExists) {
    defaultConnectionName = OLD_DEFAULT_SPARK_CONNECTION_NAME;
  } else {
    defaultConnectionName = DEFAULT_CONNECTION_NAME[connectionType as string];
  }

  // validate default connection exists in connections list
  const defaultConnectionExists = connections.find(connection => connection.name === defaultConnectionName);
  if (defaultConnectionExists) {
    return defaultConnectionName;
  }

  // fallback to another connection with the same type
  return connections.find(connection => {
    if (connectionType === ConnectionType.SPARK) {
      // for spark, only return compatibility mode connection
      return isSparkGlueCompatibilityMode(connection);
    } else {
      return connection.type === connectionType
    }
  })?.name;
}

export function getSQLQuery(connections: Connection[], connectionType: ConnectionType, nodeData: NodeData) {
  const connectionName = getDefaultConnectionName(connections, connectionType);
  const isAwsDataCatalog = isAwsDataCatalogNode(nodeData);
  const isRedshiftDataCatalog = isRedshiftDataCatalogNode(nodeData);
  const isRedshiftNode = nodeData.connectionType === ConnectionType.REDSHIFT;
  const path = nodeData?.path;
  let notebookQuery = `%%sql ${connectionName}\n`;
  if (path) {
    const { catalog, catalogChild, database, schema, table } = path;
    
    // Redshift tables do not have 'catalog' in the node. For this case, 'catalog' would be 'database' and 'database' would be 'schema'.
    const catalogName = isRedshiftNode ? database : catalog;
    const databaseName = isRedshiftNode ? schema : database;

    switch (connectionType) {
      case ConnectionType.ATHENA:
        if (isAwsDataCatalog) {
          notebookQuery += `select * from "${catalogName}"."${databaseName}"."${table}" limit 10`;
        } else {
          notebookQuery += `select * from "${catalogName}/${catalogChild}"."${database}"."${table}" limit 10`;
        }
        break;
      case ConnectionType.REDSHIFT:
        if (isAwsDataCatalog || isRedshiftDataCatalog) {
          notebookQuery += `select * from "${catalogName}"."${databaseName}"."${table}" limit 10`;
        } else {
          const catalogChildName = !isRedshiftNode ? `${catalogChild}@` : '';
          notebookQuery += `select * from "${catalogChildName}${catalogName}"."${databaseName}"."${table}" limit 10`;
        }
        break;
      case ConnectionType.SPARK:
        if (isAwsDataCatalog) {
          notebookQuery += `select * from \`spark_catalog\`.\`${databaseName}\`.\`${table}\` limit 10`;
        } else {
          const catalogChildName = catalogChild ? `_${catalogChild}` : '';
          notebookQuery += `select * from \`${catalogName}${catalogChildName}\`.\`${databaseName}\`.\`${table}\` limit 10`;
        }
        break;
    }
  }
  return notebookQuery;
}

export function isAwsDataCatalogNode(nodeData: NodeData) {
  return nodeData.path?.catalog === AWS_DATA_CATALOG || nodeData.path?.database === AWS_DATA_CATALOG.toLowerCase();
}

export function isRedshiftDataCatalogNode(nodeData: NodeData) {
  return nodeData.connectionType === ConnectionType.REDSHIFT && nodeData.path?.database === "dev";
}

function isSparkGlueCompatibilityMode(connection: Connection) {
  if (connection.type !== ConnectionType.SPARK) {
    return false;
  }
  return connection.configurations?.find(config => {
    if (config?.classification === 'GlueDefaultArgument' && config?.properties) {
      return config.properties['--enable-lakeformation-fine-grained-access'] === "false";
    }
  });
}
