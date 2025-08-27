import React from 'react';
import { Tooltip } from '../../components/tooltip/Tooltip';
import { SelectInput, SelectInputProps } from '../../components/selectinput';

import InfoIcon from '@mui/icons-material/Info';
import * as Styles from './styles';
import * as WidgetStyles from '../styles';

interface SelectInputContainerProps extends SelectInputProps {
  required?: boolean;
  errorMessage?: string;
  toolTipText?: string;
  toolTipArea?: { descriptionText: string; toolTipComponent: React.ReactNode };
}

const SelectInputContainer: React.FunctionComponent<SelectInputContainerProps> = ({
  label,
  required = true,
  toolTipText,
  toolTipArea,
  errorMessage,
  ...inputProps
}) => {
  const toolTipAreaComponent = toolTipArea && (
    <div>
      <span className={WidgetStyles.TooltipTextContainer}>{toolTipArea.descriptionText}</span>
      {toolTipArea.toolTipComponent}
    </div>
  );
  return (
    <div className={Styles.SelectInputContainer}>
      <div className={Styles.tooltipsContainer}>
        <label className={Styles.InputLabel(required)}>{label}</label>
        {(toolTipText || toolTipArea) && !inputProps.readOnly && (
          <Tooltip
            title={toolTipAreaComponent || toolTipText || ''}
            className={Styles.tooltips}
            disableInteractive={toolTipArea === null}
          >
            <InfoIcon />
          </Tooltip>
        )}
      </div>
      <SelectInput label={label} disableClearable={true} {...inputProps} />
    </div>
  );
};

export { SelectInputContainer, SelectInputContainerProps };
