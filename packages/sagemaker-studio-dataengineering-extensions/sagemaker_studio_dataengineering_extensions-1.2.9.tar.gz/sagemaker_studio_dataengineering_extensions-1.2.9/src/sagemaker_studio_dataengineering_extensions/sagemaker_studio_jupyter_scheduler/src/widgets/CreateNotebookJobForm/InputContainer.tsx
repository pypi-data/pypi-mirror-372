import React from 'react';
import InfoIcon from '@mui/icons-material/Info';

import { TextInput, TextInputProps } from '../../components/textinput';
import { Tooltip } from '../../components/tooltip';

import * as Styles from './styles';
import { strHasLength } from '../../utils';

interface InputContainerProps extends TextInputProps {
  labelInfo: string;
  required?: boolean;
  errorMessage?: string;
  toolTipText?: string;
  readOnly?: boolean;
}

const InputContainer: React.FunctionComponent<InputContainerProps> = ({
  labelInfo,
  required,
  toolTipText,
  errorMessage,
  ...inputProps
}) => {
  return (
    <div className={Styles.InputContainer}>
      <div className={Styles.tooltipsContainer}>
        <label className={Styles.InputLabel(required)}> {labelInfo} </label>
        {toolTipText && !inputProps.readOnly && (
          <Tooltip title={toolTipText} className={Styles.tooltips}>
            <InfoIcon />
          </Tooltip>
        )}
      </div>
      <TextInput {...inputProps} error={strHasLength(errorMessage)} helperText={errorMessage}
        InputProps={{
          readOnly: inputProps.readOnly,
          ...inputProps.InputProps
        }} />
    </div>
  );
};

export { InputContainer };
