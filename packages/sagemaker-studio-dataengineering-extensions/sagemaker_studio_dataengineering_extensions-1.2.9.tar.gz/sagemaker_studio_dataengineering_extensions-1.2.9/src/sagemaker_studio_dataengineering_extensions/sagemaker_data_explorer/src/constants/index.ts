import { ConnectionType, NodeType } from "../types";

export const packageName = '@amzn/maxdome-data-explorer-widget';
export const majorVersion = 1;

export const AWS_DATA_CATALOG = 'AwsDataCatalog';
export const DEFAULT_CONNECTION_NAME: Record<string, string> = {
  [ConnectionType.ATHENA]: 'project.athena',
  [ConnectionType.SPARK]: 'project.spark.compatibility',
  [ConnectionType.REDSHIFT]: 'project.redshift'
}
export const OLD_DEFAULT_SPARK_CONNECTION_NAME = 'project.spark';
export const S3_NODE_TYPES = [NodeType.Bucket, NodeType.Folder, NodeType.File];
