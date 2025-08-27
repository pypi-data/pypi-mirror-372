import React, {useEffect, useMemo, useState} from 'react';

import {NotebookPanel} from '@jupyterlab/notebook';

import DisplayWidget from "./index";
import {useKernelExecutor} from "../hooks/useKernelExecutor";
import {useNotebookUpdater} from "../hooks/useNotebookUpdater";
import {getCredentials, getRegion} from "../utils/getCredentials";
import {DisplayData} from "../utils/types";

export interface VisualizationWidgetProps {
  data: DisplayData;
  notebookPanel: NotebookPanel;
}

export const VisualizationWidget = ({data: initData, notebookPanel}: VisualizationWidgetProps): React.ReactNode => {
  const [data, setData] = useState<DisplayData>(initData);
  const [isS3Storage, setS3Storage] = useState<boolean>(data.type === "s3");
  const [isAsyncLoading, setAsyncLoading] = useState<boolean>(false);
  const kernelExecute = useKernelExecutor(notebookPanel, data.kernel_id)
  const updateCell = useNotebookUpdater(notebookPanel);

  const generateMetadata = useMemo(() => {
    if (kernelExecute) {
      return async () => {
        const value = await kernelExecute(`display(${data.interface_id}.generate_metadata_str())`);
        if (data.type === "cell") {
          await updateCell({...data, metadata_str: value});
        }
        return value
      }
    }
  }, [data, kernelExecute, updateCell]);

  const generateSummarySchema = useMemo(() => {
    if (kernelExecute) {
      return async () => {
        const value = await kernelExecute(`display(${data.interface_id}.generate_summary_schema_str())`);
        if (data.type === "cell") {
          await updateCell({...data, summary_schema_str: value});
        }
        return value
      }
    }
  }, [data, kernelExecute, updateCell]);

  const generateColumnSchema = useMemo(() => {
    if (kernelExecute) {
      return async (column: string) => {
        const value = await kernelExecute(`display(${data.interface_id}.generate_column_schema_str(column = "${column}"))`);
        if (data.type === "cell") {
          await updateCell({...data, column_schema_str_dict: {...data.column_schema_str_dict, [column]: value}});
        }
        return value
      }
    }
  }, [data, kernelExecute, updateCell]);

  const generatePlotData = useMemo(() => {
    if (kernelExecute) {
      return async (xAxis: string, yAxis: string, aggMethod: string) => {
        const value = await kernelExecute(`display(${data.interface_id}
                .generate_echart_data_str(x_axis = "${xAxis}", y_axis = "${yAxis}", agg_method = "${aggMethod}"))`);
        if (data.type === "cell") {
          await updateCell({
            ...data,
            echart_data_str_dict: {
              ...data.echart_data_str_dict,
              [xAxis]: {
                ...data.echart_data_str_dict?.[xAxis],
                [yAxis]: {...data.echart_data_str_dict?.[xAxis]?.[yAxis], [aggMethod]: value}
              }
            }
          });
        }
        return value
      }
    }
  }, [data, kernelExecute, updateCell]);

  const updateSample = useMemo(() => {
    if (kernelExecute) {
      return async (sampleMethod: string, sampleSize: string) =>
        await kernelExecute(`display(${data.interface_id}.set_sampling_method(sample_method="${sampleMethod}", sample_size=${sampleSize}))`);
    }
  }, [data, kernelExecute]);

  useEffect(() => {
    async function updateOutput(): Promise<DisplayData | undefined> {
      if (kernelExecute) {
        await kernelExecute(`${data.interface_id}.set_storage("${isS3Storage ? "s3" : "cell"}")`);
        if (isS3Storage) {
          if (data.type != "s3") {
            const s3Path = await kernelExecute(`display(${data.interface_id}.get_s3_path())`);
            const s3Size = parseInt(await kernelExecute(`display(${data.interface_id}.get_s3_df_size())`));
            await kernelExecute(`display(${data.interface_id}.generate_metadata_str())`);
            await kernelExecute(`display(${data.interface_id}.generate_summary_schema_str())`);
            await kernelExecute(`display(${data.interface_id}.upload_dataframe_to_s3())`, 1000000).then(() => {
              setAsyncLoading(false);
            });
            return {
              type: "s3",
              kernel_id: data.kernel_id,
              interface_id: data.interface_id,
              connection_name: data.connection_name,
              original_size: data.original_size,
              s3_path: s3Path,
              s3_size: s3Size,
            }
          }
        } else {
          if (data.type != "cell") {
            // Encode the data str using base64
            const data_str = await kernelExecute(`display(${data.interface_id}.generate_sample_dataframe_str())`);
            const metadata = await kernelExecute(`display(${data.interface_id}.generate_metadata_str())`);
            const summary_schema = await kernelExecute(`display(${data.interface_id}.generate_summary_schema_str())`);
            return {
              type: "cell",
              kernel_id: data.kernel_id,
              interface_id: data.interface_id,
              connection_name: data.connection_name,
              original_size: data.original_size,
              data_str: data_str,
              metadata_str: metadata,
              summary_schema_str: summary_schema,
              column_schema_str_dict: {},
              echart_data_str_dict: {}
            }
          }
        }
      }
      return undefined;
    }

    updateOutput().then(async displayData => {
      if (displayData) {
        setData(displayData);
        await updateCell(displayData);
      }
    }).catch(e => {
      console.error(e)
    })
  }, [isS3Storage, kernelExecute]);

  const props = useMemo(() => {
    const props: any = {}
    if (data.type === "s3") {
      props.visualizationProps = {
        type: "s3",
        visualizationDataProps: {
          originalSize: data.original_size,
          s3Path: data.s3_path,
          s3Size: data.s3_size,
          region: getRegion(),
          credentialProvider: getCredentials(data.connection_name),
          kernelOperations: kernelExecute ? {
            updateSample: updateSample,
            generateMetadata: generateMetadata,
            generateSummarySchema: generateSummarySchema,
            generateColumnSchema: generateColumnSchema,
            generatePlotData: generatePlotData,
            setS3Storage: setS3Storage,
          } : undefined
        }
      }
    } else if (data.type === "cell") {
      props.visualizationProps = {
        type: "cell",
        visualizationDataProps: {
          originalSize: data.original_size,
          dataId: data.interface_id,
          dataStr: data.data_str,
          metadataStr: data.metadata_str,
          summarySchemaStr: data.summary_schema_str,
          columnSchemaStrDict: data.column_schema_str_dict,
          plotDataStrDict: data.echart_data_str_dict,
          kernelOperations: kernelExecute ? {
            updateSample: updateSample,
            generateMetadata: generateMetadata,
            generateSummarySchema: generateSummarySchema,
            generateColumnSchema: generateColumnSchema,
            generatePlotData: generatePlotData,
            setS3Storage: setS3Storage,
          } : undefined
        },
      }
    }
    return props;
  }, [data, kernelExecute]);

  if (data.type === "default") {
    return (<div>Preparing your data for display...</div>);
  }

  return (
    <div>
      {isAsyncLoading && (<div>Uploading data to S3...</div>)}
      <DisplayWidget
        {...props}
        key={`${data.interface_id}-${data.type}${kernelExecute ? "-withKernel" : ""}`}
        domId={data.interface_id}
      />
    </div>
  );
};
