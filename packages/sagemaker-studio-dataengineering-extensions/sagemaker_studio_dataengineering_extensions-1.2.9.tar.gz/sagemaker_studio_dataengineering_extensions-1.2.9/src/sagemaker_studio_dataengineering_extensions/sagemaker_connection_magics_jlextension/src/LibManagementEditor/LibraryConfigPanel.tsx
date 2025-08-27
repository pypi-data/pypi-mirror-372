import { ReadonlyJSONObject } from '@lumino/coreutils';
import { ISignal } from '@lumino/signaling';
import { JSONSchema7 } from 'json-schema';
import React, { useCallback, useEffect, useMemo, useState } from 'react';

import { LibraryConfigFormWidget } from './LibraryConfigForm';
import { LibraryConfigListWidget } from './LibraryConfigList';

export const LibraryConfigPanelWidget: React.FC<LibraryConfigPanelWidgetProps> = ({
  schema,
  configs,
  handleSelectTypeSignal,
  handleSelectSourceSignal,
  onConfigsChange,
  setError,
}: LibraryConfigPanelWidgetProps): JSX.Element => {
  const [selectType, setSelectType] = useState<string>('Jar');
  const [selectSource, setSelectSource] = useState<string>('MavenArtifacts');

  useEffect(() => {
    const onSelectTypeChange = (list: LibraryConfigListWidget, type: string) => {
      setSelectType(type);
    };
    handleSelectTypeSignal?.connect?.(onSelectTypeChange);
    const onSelectSourceChange = (list: LibraryConfigListWidget, source: string) => {
      setSelectSource(source);
    };
    handleSelectSourceSignal?.connect?.(onSelectSourceChange);

    return () => {
      handleSelectTypeSignal?.disconnect?.(onSelectTypeChange);
      handleSelectSourceSignal?.disconnect?.(onSelectSourceChange);
    };
  }, []);

  const selectSchema = useMemo(() => {
    if (selectType && selectSource) {
      return (schema.properties![selectType] as JSONSchema7).properties![selectSource] as JSONSchema7;
    } else {
      return {};
    }
  }, [selectType, selectSource, schema]);

  const selectConfig = useMemo(() => {
    if (selectType && selectSource) {
      return (configs[selectType] as ReadonlyJSONObject)[selectSource] as ReadonlyJSONObject;
    } else {
      return {} as ReadonlyJSONObject;
    }
  }, [selectType, selectSource, configs]);

  const onChange: (config: ReadonlyJSONObject) => void = config => {
    const newConfigs = JSON.parse(JSON.stringify(configs));
    newConfigs[selectType][selectSource] = config;
    onConfigsChange(newConfigs);
  };

  const hasError = useCallback(
    (hasError: boolean) => {
      setError(selectType, selectSource, hasError);
    },
    [setError, selectType, selectSource]
  );

  return (
    <div className="jp-SettingsPanel">
      <div className="jp-SettingsForm">
        <LibraryConfigFormWidget
          schema={selectSchema}
          config={selectConfig}
          onChange={onChange}
          hasError={hasError}
          selectedType={selectType}
          selectedSource={selectSource}
        />
      </div>
    </div>
  );
};

export interface LibraryConfigPanelWidgetProps {
  schema: JSONSchema7;
  configs: ReadonlyJSONObject;
  handleSelectTypeSignal: ISignal<LibraryConfigListWidget, string>;
  handleSelectSourceSignal: ISignal<LibraryConfigListWidget, string>;
  onConfigsChange: (configs: ReadonlyJSONObject) => void;
  setError: (type: string, source: string, error: boolean) => void;
}
