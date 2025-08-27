interface DisplayDataBase {
  kernel_id: string;
  interface_id: string;
  connection_name: string;
  original_size: number;
}

interface DefaultDisplayData extends DisplayDataBase {
  type: "default";
}

interface S3DisplayData extends DisplayDataBase {
  type: "s3";
  s3_path: string;
  s3_size: number;
}

interface CellDisplayData extends DisplayDataBase {
  type: "cell";
  data_str: string;
  metadata_str: string;
  summary_schema_str: string;
  column_schema_str_dict: Record<string, string>;
  echart_data_str_dict: Record<string, Record<string, Record<string, string>>>
}

export type DisplayData = S3DisplayData | CellDisplayData | DefaultDisplayData;
