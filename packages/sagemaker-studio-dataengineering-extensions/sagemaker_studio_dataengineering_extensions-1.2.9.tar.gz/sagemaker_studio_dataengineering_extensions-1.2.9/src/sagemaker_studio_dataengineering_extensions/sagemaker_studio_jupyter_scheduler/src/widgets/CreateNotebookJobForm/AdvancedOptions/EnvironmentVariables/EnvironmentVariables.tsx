import React from 'react';
import InfoIcon from '@mui/icons-material/Info';
import { Scheduler } from '@jupyterlab/scheduler';
import { Button } from '@mui/material';
import Alert from '@mui/material/Alert';

import { ErrorIconStyled } from '../../styles';
import { EnvironmentVariable } from './EnvironmentVariable';
import { TextInput } from '../../../../components/textinput';
import { Tooltip } from '../../../../components/tooltip/Tooltip';
import { i18nStrings } from '../../../../constants';

import * as Styles from './styles';

interface IEnvironmentVariable {
  key: string;
  value: string;
}

interface Props {
  isButtonDisabled: boolean;
  allFieldsDisabled: boolean;
  environmentVariables: IEnvironmentVariable[];
  setEnvironmentVariables: (environmentParameters: IEnvironmentVariable[]) => void;
  formErrors: Scheduler.ErrorsType;
  setFormErrors: (errors: Scheduler.ErrorsType) => void;
}

const widgetStrings = i18nStrings.ScheduleNoteBook.MainPanel.AdvancedOptions;
const tooltipsStrings = i18nStrings.ScheduleNoteBook.MainPanel.Tooltips;

const EnvironmentVariables: React.FunctionComponent<Props> = ({
  allFieldsDisabled,
  isButtonDisabled,
  environmentVariables,
  setEnvironmentVariables,
  formErrors,
  ...rest
}) => {
  const isError = !!formErrors.environmentVariablesError;

  const errorMessageWithIcon = (
    <div className={ErrorIconStyled}>
      <Alert severity="error">{formErrors.environmentVariablesError}</Alert>
    </div>
  );

  return (
    <div className={Styles.EnvironmentVariablesSection}>
      <div className={Styles.tooltipsContainer}>
        <label className={Styles.InputLabel}>{widgetStrings.environmentVariables}</label>
        {!allFieldsDisabled ? (
          <Tooltip title={tooltipsStrings.EnvironmentVariablesTooltip}>
            <InfoIcon />
          </Tooltip>
        ) : null}
      </div>

      {/* if in detail view and there are no env variables */}
      {allFieldsDisabled && environmentVariables.length === 0 ? (
        <div className={Styles.EnvironmentVariableContainer}>
          <TextInput
            InputProps={{ readOnly: true }}
            placeholder={widgetStrings.Placeholders.NoneSelected}
          />
        </div>
      ) : (
        <>
          {environmentVariables.map((_, i) => (
            <EnvironmentVariable
              isDisabled={allFieldsDisabled}
              key={i}
              environmentParameters={environmentVariables}
              setEnvironmentParameters={setEnvironmentVariables}
              index={i}
              formErrors={formErrors}
              {...rest}
            />
          ))}
        </>
      )}
      {isError && <div>{errorMessageWithIcon}</div>}
      {!allFieldsDisabled && (
        <div>
          <Button
            disabled={isButtonDisabled}
            className={Styles.ConfigBtn}
            variant={'contained'}
            color={'primary'}
            size={'small'}
            onClick={() => {
              setEnvironmentVariables([...environmentVariables, { key: '', value: '' }]);
            }}
          >
            {widgetStrings.addEnvironmentvariable}
          </Button>
        </div>
      )}
    </div>
  );
};

export { EnvironmentVariables };
