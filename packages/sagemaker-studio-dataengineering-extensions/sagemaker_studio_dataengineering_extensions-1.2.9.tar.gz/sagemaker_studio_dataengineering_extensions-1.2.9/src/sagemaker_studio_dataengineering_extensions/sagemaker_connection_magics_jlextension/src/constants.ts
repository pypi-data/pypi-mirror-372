import { isLocalhost } from './utils';

export enum ConnectionType {
  IAM = 'iam',
  REDSHIFT = 'redshift',
  ATHENA = 'athena',
  SPARK_EMR_EC2 = 'spark_emr_ec2',
  SPARK_EMR_SERVERLESS = 'spark_emr_serverless',
  SPARK_GLUE = 'spark_glue',
}

export const ConnectionDescription: Map<ConnectionType, string> = new Map<ConnectionType, string>([
  [ConnectionType.IAM, 'JupyterLab environment provided by Amazon SageMaker'],
  [ConnectionType.SPARK_EMR_EC2, 'AWS EMR on EC2 - Spark compute platform provided by Amazon EMR'],
  [ConnectionType.SPARK_EMR_SERVERLESS, 'AWS EMR Serverless - Spark compute platform provided by Amazon EMR Serverless'],
  [ConnectionType.SPARK_GLUE, 'AWS Glue - Spark compute platform provided by AWS Glue'],
]);

export class Constants {
  public static readonly SAGEMAKER_JUPYTER_PLUGIN_SETTINGS_ID = '@amzn/sagemaker-connection-magics-jlextension:plugin';
  public static readonly CONNECTION_NAME_KEY = '--name';
  public static readonly CONNECTION_LANGUAGE_KEY = '--language';
  public static readonly CONNECTION_TYPE_EMR_EC2 = 'SPARK_EMR_EC2';
  public static readonly CONNECTION_TYPE_EMR_SERVERLESS = 'SPARK_EMR_SERVERLESS';
  public static readonly CONNECTION_TYPE_GLUE = 'SPARK_GLUE';
  public static readonly CONNECTION_TYPE_SPARK = 'SPARK';
  public static readonly CONNECTION_TYPE_REDSHIFT = 'REDSHIFT';
  public static readonly CONNECTION_TYPE_ATHENA = 'ATHENA';
  public static readonly CONNECTION_TYPE_IAM = 'IAM';
  public static readonly LANGUAGE_PYTHON = 'python';
  public static readonly LANGUAGE_PYTHON_DISPLAY_NAME = 'Python';
  public static readonly LANGUAGE_SQL = 'sql';
  public static readonly LANGUAGE_SQL_DISPLAY_NAME = 'SQL';
  public static readonly LANGUAGE_SCALA = 'scala';
  public static readonly LANGUAGE_SCALA_DISPLAY_NAME = 'Scala';
  public static readonly INTERPRETER_PYSPARK_DISPLAY_NAME = 'PySpark';
  public static readonly INTERPRETER_SCALA_SPARK_DISPLAY_NAME = 'ScalaSpark';
  public static readonly INTERPRETER_SQL_DISPLAY_NAME = 'SQL';
  public static readonly INTERPRETER_LOCAL_PYTHON_DISPLAY_NAME = 'Local Python';
  public static readonly INTERPRETER_PYSPARK_VALUE = 'pyspark';
  public static readonly INTERPRETER_SCALA_SPARK_VALUE = 'scalaspark';
  public static readonly INTERPRETER_SQL_VALUE = 'sql';
  public static readonly INTERPRETER_LOCAL_PYTHON_VALUE = 'local';
  public static readonly DEFAULT_IAM_CONNECTION_NAME = 'project.iam';
  public static readonly DEFAULT_IAM_CONNECTION_NAME_EXPRESS = 'default.iam';
  public static readonly DEFAULT_IAM_CONNECTION_DISPLAYNAME = 'project.python';
  public static readonly DEFAULT_SPARK_GLUE_CONNECTION_NAME_DEPRECATED = 'project.spark';
  public static readonly DEFAULT_GLUE_COMPATIBILITY_CONNECTION_NAME = 'project.spark.compatibility';
  public static readonly DEFAULT_GLUE_FINE_GRAINED_CONNECTION_NAME = 'project.spark.fineGrained';
  public static readonly DEFAULT_SPARK_GLUE_CONNECTION_NAME_EXPRESS = 'default.spark';
  public static readonly DEFAULT_REDSHIFT_CONNECTION_NAME = 'project.redshift';
  public static readonly DEFAULT_ATHENA_CONNECTION_NAME = 'project.athena';
  public static readonly DEFAULT_ATHENA_CONNECTION_NAME_EXPRESS = 'default.sql';
  public static readonly CONNECT_CELL_MAGIC = '%%connect';
  public static readonly CONNECT_PYSPARK_MAGIC_ALIAS = '%%pyspark';
  public static readonly CONNECT_SPARK_MAGIC_ALIAS = '%%spark';
  public static readonly CONNECT_LOCAL_MAGIC_ALIAS = '%%local';
  public static readonly CONNECT_SCALA_SPARK_CELL_MAGIC_ALIAS = '%%scalaspark';
  public static readonly CONNECT_SQL_CELL_MAGIC_ALIAS = '%%sql';
  public static readonly SAGEMAKER_MAGIC_SUPPORTED_KERNEL_NAME = 'python3';
  public static readonly USER_SETTING_CONNECTION_KEY = 'compute';
  public static readonly USER_SETTING_LANGUAGE_KEY = 'language';
  public static readonly USER_SETTING_INTERPRETER_KEY = 'connectionType';
  public static readonly USER_SETTING_ALWAYS_SHOW_CELL_LEVEL_SELECTION = 'alwaysShowCellLevelConnectionSelection';
  public static readonly USER_SETTING_ALWAYS_USE_S3_STORAGE_IN_VISUALIZATION = 'alwaysUseS3StorageInVisualization';
  public static readonly USER_SETTING_ENABLE_INTERACTIVE_DEBUGGING = 'enableInteractiveDebugging';
  public static readonly AUTO_GENERATED_COMMENT_PYTHON_SYNTAX = '# Enter your code at the start of this line to replace this comment';
  public static readonly AUTO_GENERATED_COMMENT_SCALA_SYNTAX = '// Enter your code at the start of this line to replace this comment';
  public static readonly AUTO_GENERATED_COMMENT_SQL_SYNTAX = '-- Enter your code at the start of this line to replace this comment';

  public static readonly CONNECTION_TYPE_INTERPRETER_MAP: Record<string, string[]> = {
    IAM: [Constants.INTERPRETER_LOCAL_PYTHON_VALUE],
    REDSHIFT: [Constants.INTERPRETER_SQL_VALUE],
    ATHENA: [Constants.INTERPRETER_SQL_VALUE],
    SPARK_GLUE: [Constants.INTERPRETER_PYSPARK_VALUE, Constants.INTERPRETER_SQL_VALUE, Constants.INTERPRETER_SCALA_SPARK_VALUE],
    SPARK_EMR_EC2: [Constants.INTERPRETER_PYSPARK_VALUE, Constants.INTERPRETER_SQL_VALUE, Constants.INTERPRETER_SCALA_SPARK_VALUE],
    SPARK_EMR_SERVERLESS: [Constants.INTERPRETER_PYSPARK_VALUE, Constants.INTERPRETER_SQL_VALUE, Constants.INTERPRETER_SCALA_SPARK_VALUE],
  };

  public static readonly INTERPRETER_CONNECTION_TYPE_MAP: Record<string, string[]> = {
    pyspark: ['SPARK_GLUE', 'SPARK_EMR_EC2', 'SPARK_EMR_SERVERLESS'],
    sql: ['REDSHIFT', 'ATHENA', 'SPARK_GLUE', 'SPARK_EMR_EC2', 'SPARK_EMR_SERVERLESS'],
    scalaspark: ['SPARK_GLUE', 'SPARK_EMR_EC2', 'SPARK_EMR_SERVERLESS'],
    local: ['IAM']
  };

  public static readonly SUPPORTED_INTERPRETER_LIST = [
    {label: Constants.INTERPRETER_PYSPARK_DISPLAY_NAME, value: Constants.LANGUAGE_PYTHON},
    {label: Constants.INTERPRETER_SCALA_SPARK_DISPLAY_NAME, value: Constants.LANGUAGE_SCALA},
    {label: Constants.INTERPRETER_SQL_DISPLAY_NAME, value: Constants.LANGUAGE_SQL},
    {label: Constants.INTERPRETER_LOCAL_PYTHON_DISPLAY_NAME, value: Constants.LANGUAGE_PYTHON},
  ];

  public static readonly endpointPrefix = isLocalhost() ? 'http://localhost:8888' : '';
}
