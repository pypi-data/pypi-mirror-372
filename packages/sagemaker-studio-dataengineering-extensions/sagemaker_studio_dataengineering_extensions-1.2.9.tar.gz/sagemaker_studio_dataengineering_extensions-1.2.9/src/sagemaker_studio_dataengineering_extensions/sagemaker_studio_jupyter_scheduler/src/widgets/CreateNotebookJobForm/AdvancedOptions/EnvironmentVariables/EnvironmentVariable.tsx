import React from 'react';
import { Scheduler } from '@jupyterlab/scheduler';
import CloseIcon from '@mui/icons-material/Close';
import IconButton from '@mui/material/IconButton';

import { i18nStrings } from '../../../../constants/common';
import { InputContainer } from '../../InputContainer';

import * as Styles from './styles';

const KEY_REGEX = new RegExp('[a-zA-Z_][a-zA-Z0-9_]*');
const VALUE_REGEX = new RegExp('[\\S\\s]*');

const errorMessageStrings = i18nStrings.ScheduleNoteBook.MainPanel.ErrorMessages.AdvancedOptions;
const widgetStrings = i18nStrings.ScheduleNoteBook.MainPanel.AdvancedOptions;

interface IEnvironmentVariable {
  key: string;
  value: string;
}

interface Props {
  isDisabled: boolean;
  index: number;
  environmentParameters: IEnvironmentVariable[];
  setEnvironmentParameters: (environmentParameters: IEnvironmentVariable[]) => void;
  formErrors: Scheduler.ErrorsType;
  setFormErrors: (errors: Scheduler.ErrorsType) => void;
}

const EnvironmentVariable: React.FunctionComponent<Props> = ({
  isDisabled,
  environmentParameters,
  setEnvironmentParameters,
  index,
  formErrors,
  setFormErrors,
}) => {
  const currentEnvironmentVariable = environmentParameters[index];

  const deleteKeyValue = (index: number) => {
    const newArray = [...environmentParameters];
    newArray.splice(index, 1);

    setEnvironmentParameters(newArray);
    setFormErrors({
      ...formErrors,
      environmentVariablesError: '',
    });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name = e.currentTarget.name;
    const value = e.target.value;
    const [field, i] = name.split('-') as [string, number];

    const updateItem =
      field === 'envKey'
        ? { key: value, value: environmentParameters[i].value }
        : { key: environmentParameters[i].key, value: value };

    const newArray = [...environmentParameters];
    newArray.splice(i, 1, updateItem);

    setEnvironmentParameters(newArray);
  };

  const handleBlur = () => {
    const { key, value } = currentEnvironmentVariable;

    if (key.length < 1 || value.length < 1) {
      setFormErrors({
        ...formErrors,
        environmentVariablesError: errorMessageStrings.EnvironmentVariableEmptyError,
      });
      return;
    }

    if (key.length > 512 || value.length > 512) {
      setFormErrors({
        ...formErrors,
        environmentVariablesError: errorMessageStrings.EnvironmentVariableLengthError,
      });
      return;
    }

    if (!KEY_REGEX.test(key) || !VALUE_REGEX.test(value)) {
      setFormErrors({
        ...formErrors,
        environmentVariablesError: errorMessageStrings.EnvironmentVariableFormatError,
      });
      return;
    }

    setFormErrors({
      ...formErrors,
      environmentVariablesError: '',
    });
  };

  return (
    <div className={Styles.EnvironmentVariablesContainer}>
      <InputContainer
        className={Styles.EnvironmentVariablesInput}
        readOnly={isDisabled}
        name={`envKey-${index}`}
        labelInfo={widgetStrings.Key}
        value={environmentParameters[index].key}
        onChange={handleChange}
        onBlur={handleBlur}
      />
      <InputContainer
        className={Styles.EnvironmentVariablesInput}
        readOnly={isDisabled}
        name={`envValue-${index}`}
        labelInfo={widgetStrings.Value}
        value={environmentParameters[index].value}
        onChange={handleChange}
        onBlur={handleBlur}
      />
      <div>
        {!isDisabled && (
          <IconButton
            onClick={() => {
              deleteKeyValue(index);
              setFormErrors({
                ...formErrors,
                environmentVariablesError: '',
              });
            }}
            size="large">
            <CloseIcon />
          </IconButton>
        )}
      </div>
    </div>
  );
};

export { EnvironmentVariable, IEnvironmentVariable };
