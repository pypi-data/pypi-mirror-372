export interface Connection {
  configurations: Configurations[];
  connectionId: string;
  domainId: string;
  environmentId: string;
  name: string;
  physicalEndpoints: any;
  projectId: string;
  props: any;
  type: ConnectionType;
}

interface Configurations {
  classification?: string;
  properties?: Record<string, string>
}

export interface Credentials {
  access_key: string;
  secret_key: string;
  session_token: string;
}

export interface EnvResponse {
  domain_id: string;
  project_id: string;
  aws_region: string;
  environment_id: string;
  repository_name?: string;
  repository_user_email?: string;
  user_id: string;
  dz_endpoint: string;
  dz_region: string;
  dz_stage: string;
  enabled_features: string[];
}

export enum ConnectionType {
  SPARK = "SPARK",
  SPARK_GLUE = "SPARK_GLUE",
  SPARK_EMR_EC2 = "SPARK_EMR_EC2",
  SPARK_EMR_EKS = "SPARK_EMR_EKS",
  SPARK_EMR_SERVERLESS = "SPARK_EMR_SERVERLESS",
  IAM = "IAM",
  LAKEHOUSE = "LAKEHOUSE",
  S3 = "S3",
  GIT = "GIT",
  ATHENA = "ATHENA",
  HYPERPOD = "HYPERPOD",
  SNOWFLAKE = "SNOWFLAKE",
  BIGQUERY = "BIGQUERY",
  DOCUMENTDB = "DOCUMENTDB",
  DYNAMODB = "DYNAMODB",
  MYSQL = "MYSQL",
  OPENSEARCH = "OPENSEARCH",
  ORACLE = "ORACLE",
  POSTGRESQL = "POSTGRESQL",
  REDSHIFT = "REDSHIFT",
  SAPHANA = "SAPHANA",
  SQLSERVER = "SQLSERVER",
  TERADATA = "TERADATA",
  VERTICA = "VERTICA"
}

export enum NodeType {
  Connection = "connection",
  Environment = "environment",
  Catalog = "catalog",
  CatalogChild = "catalog-child",
  RedLakeCatalog = "redlake-catalog",
  RedLakeCatalogChild = "redlake-catalog-child",
  S3TablesCatalog = "s3-tables-catalog",
  S3TablesCatalogChild = "s3-tables-catalog-child",
  Database = "database",
  Table = "table",
  TableContainer = "table-container",
  Function = "function",
  Schema = "schema",
  Column = "column",
  StoredProcedure = "stored-procedure",
  View = "view",
  ViewContainer = "view-container",
  Bucket = "bucket",
  Folder = "folder",
  File = "file",
  LoadMore = "load-more",
  Loading = "loading",
  NoData = "no-data",
  NoSchema = "no-schema",
  Error = "error"
}

export interface NodePath {
  environment?: string;
  connection?: string;
  catalog?: string;
  catalogChild?: string;
  database?: string;
  schema?: string;
  table?: string;
  view?: string;
  column?: string;
  bucket?: string;
  key?: string;
  nextToken?: string;
  label?: string;
}

export interface NodeData {
  id: string;
  nodeType: NodeType;
  value?: any;
  parent?: NodeData;
  isContainer?: boolean;
  connectionType?: string;
  path?: NodePath;
  parents?: {
      parentId: string;
      parentType: string;
  }[];
}
