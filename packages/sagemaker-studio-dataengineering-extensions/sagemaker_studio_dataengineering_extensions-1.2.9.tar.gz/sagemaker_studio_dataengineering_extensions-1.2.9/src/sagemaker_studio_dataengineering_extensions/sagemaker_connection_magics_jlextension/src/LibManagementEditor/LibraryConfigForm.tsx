import { nullTranslator } from '@jupyterlab/translation';
import { FormComponent } from '@jupyterlab/ui-components';
import { ReadonlyJSONObject } from '@lumino/coreutils';
import { IChangeEvent } from '@rjsf/core';
import validatorAjv8 from '@rjsf/validator-ajv8';
import { JSONSchema7, JSONSchema7Definition } from 'json-schema';
import React, { useEffect, useMemo, useRef, useState } from 'react';

import { ConnectionDescription } from '../constants';
import { CONFIGS } from './config';

export const LibraryConfigFormWidget: React.FC<LibraryConfigFormWidgetProps> = ({
  schema,
  config,
  onChange,
  hasError,
  selectedType,
  selectedSource,
}: LibraryConfigFormWidgetProps): JSX.Element => {
  const _onChange: (e: IChangeEvent<ReadonlyJSONObject>) => void = e => {
    hasError(e.errors.length !== 0);
    onChange(e.formData as ReadonlyJSONObject);
  };

  const getDescription: () => JSX.Element = () => {
    const configMetadata = CONFIGS[selectedType][selectedSource];
    return (
      <div className="jp-SettingsHeader-description">
        <div>Libraries in this configuration will be installed only for the following Computes:</div>
        <ul className="lsp-server-links-list jp-lib-mgmt-desc-divider">
          {configMetadata.supportedConnectionType.map(connectionType => (
            <li>{ConnectionDescription.get(connectionType)}</li>
          ))}
        </ul>
        {configMetadata.additionalDescription && configMetadata.additionalDescription.length > 0 && (
          <div>{configMetadata.additionalDescription}</div>
        )}
      </div>
    );
  };

  function createForm() {
    if (Array.isArray(schema.type) && schema.type.includes('object') && schema.properties) {
      return <MultiForm properties={schema.properties} config={config} onChange={onChange} hasError={hasError} />;
    } else {
      return (
        <FormComponent
          schema={schema}
          // @ts-ignore
          validator={validatorAjv8}
          formData={config}
          onChange={_onChange}
          liveValidate
          tagName="div"
          translator={nullTranslator}
          showErrorList={false}
        />
      );
    }
  }

  return (
    <>
      <div className="jp-SettingsHeader">
        <h2 className="jp-SettingsHeader-title">{CONFIGS[selectedType][selectedSource].title}</h2>
        {getDescription()}
      </div>
      {createForm()}
    </>
  );
};

const MultiForm: React.FC<MultiFormProps> = ({
  properties,
  config,
  onChange,
  hasError,
}: MultiFormProps): JSX.Element => {
  const [localConfig, setLocalConfig] = useState<ReadonlyJSONObject>(config ?? {});
  const [errors, setErrors] = useState<{ [key: string]: boolean }>({});
  const isMountingRef = useRef(false);

  useEffect(() => {
    isMountingRef.current = true;
  }, []);

  useEffect(() => {
    // Skip onChange call on page mount
    if (!isMountingRef.current) {
      onChange(localConfig);
    } else {
      isMountingRef.current = false;
    }
  }, [localConfig]);

  useEffect(() => {
    let error = false;
    Object.keys(errors).forEach(key => (error = error || errors[key]));
    hasError(error);
  }, [errors]);

  const formWidget = useMemo(() => {
    const forms: JSX.Element[] = [];
    Object.keys(properties).map(propertyKey => {
      const onPartialChange: (e: IChangeEvent<ReadonlyJSONObject>) => void = e => {
        setErrors(errors => {
          return {
            ...errors,
            [propertyKey]: e.errors.length !== 0,
          };
        });

        setLocalConfig(previousConfig => {
          const newConfig = JSON.parse(JSON.stringify(previousConfig));
          newConfig[propertyKey] = e.formData;
          return newConfig as ReadonlyJSONObject;
        });
      };
      forms.push(
        <FormComponent
          schema={properties[propertyKey] as JSONSchema7}
          // @ts-ignore
          validator={validatorAjv8}
          formData={config ? (config[propertyKey] as ReadonlyJSONObject) : {}}
          onChange={onPartialChange}
          liveValidate
          tagName="div"
          translator={nullTranslator}
          showErrorList={false}
        />
      );
    });
    return forms;
  }, []);

  return <>{formWidget}</>;
};

export interface LibraryConfigFormWidgetProps {
  schema: JSONSchema7;
  config: ReadonlyJSONObject;
  onChange: (config: ReadonlyJSONObject) => void;
  hasError: (error: boolean) => void;
  selectedType: string;
  selectedSource: string;
}

interface MultiFormProps {
  properties: {
    [key: string]: JSONSchema7Definition;
  };
  config: ReadonlyJSONObject;
  onChange: (config: ReadonlyJSONObject) => void;
  hasError: (error: boolean) => void;
}
