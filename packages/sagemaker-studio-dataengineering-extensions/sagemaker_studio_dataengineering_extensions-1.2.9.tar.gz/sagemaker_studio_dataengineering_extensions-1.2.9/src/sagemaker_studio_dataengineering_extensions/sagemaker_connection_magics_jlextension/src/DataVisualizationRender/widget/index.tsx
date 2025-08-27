import React, { useEffect, useState } from 'react';
import {majorVersion, packageName} from "../utils/constants";
import {getPackageMetadata} from "../utils/getPackageMetadata";

export interface DataVisualizationWidgetExport {
  // eslint-disable-next-line
  renderToDom: (config: any) => () => void;
}

// eslint-disable-next-line react-refresh/only-export-components
export const importWidget = async (stage = 'prod', aliasName = ''): Promise<DataVisualizationWidgetExport> => {
  const packageNameSuffix = stage === 'prod' ? '' : `-${stage}`;

  const packageMetadataRequestConfig = {
    packageName: `${packageName}${packageNameSuffix}`,
    majorVersion: majorVersion.toString(),
    aliasName: aliasName,
  };
  /* eslint-disable */
  const packageMetadata = await getPackageMetadata(packageMetadataRequestConfig);
  return await import(
      /* @vite-ignore */
      /* webpackIgnore: true */ packageMetadata.basePath + packageMetadata.metadata.module?.path
      );
};

const DisplayWidget = (props: any): JSX.Element => {
  const [error, setError] = useState<Error | null>();

  let stage = props.stage;
  let aliasName = '';

  useEffect(() => {
    let unmount: () => void;
    importWidget(stage, aliasName)
      .then(widgetExport => {
        unmount = widgetExport.renderToDom({ ...props });
      })
      .catch(error => {
        console.error('Failed to import widget', error);
        setError(error);
      });
    return () => unmount?.();
  }, []);

  if (error) {
    return <div>Unable to load display widget.</div>;
  }

  return <div id={props.domId} style={{ display: 'contents' }}></div>;
};

export default DisplayWidget;
