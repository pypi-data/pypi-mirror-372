import React from 'react';
import { Tooltip } from '../../components/tooltip/Tooltip';
import Alert from '@mui/material/Alert';

import InfoIcon from '@mui/icons-material/Info';
import Autocomplete, {
  AutocompleteProps,
  AutocompleteRenderInputParams,
  createFilterOptions,
} from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import * as Styles from './styles';

const filter = createFilterOptions<string>();

interface MultiSelectContainerProps extends Omit<AutocompleteProps<string, true, boolean, boolean>, 'renderInput'> {
  name: string;
  className?: string;
  label: string;
  errorMessage?: string;
  required?: boolean;
  renderInput?: (params: AutocompleteRenderInputParams) => React.ReactNode;
  tooltip?: string;
  disabledTooltip?: string;
}

const MultiSelectContainer: React.FunctionComponent<MultiSelectContainerProps> = ({
  label,
  required,
  errorMessage,
  disabled,
  renderInput,
  tooltip,
  disabledTooltip,
  freeSolo,
  options,
  ...rest
}) => {
  renderInput ??= (params: AutocompleteRenderInputParams) => (
    <TextField {...params} variant="outlined" size="small" margin="dense" placeholder={label} />
  );

  // if disabled, display disabledTooltip (if present)
  //   otherwise, display tooltip (if present)
  const tooltipComponent = disabled ? (
    disabledTooltip ? (
      <Tooltip title={disabledTooltip} className={Styles.tooltips}>
        <InfoIcon />
      </Tooltip>
    ) : (
      <></>
    )
  ) : tooltip ? (
    <Tooltip title={tooltip} className={Styles.tooltips}>
      <InfoIcon />
    </Tooltip>
  ) : (
    <></>
  );

  const errorComponent = errorMessage ? (
    <div className={Styles.ErrorIconStyled}>
      <Alert severity="error">{errorMessage}</Alert>
    </div>
  ) : (
    <></>
  );

  return (
    <div className={Styles.SelectInputContainer}>
      <div className={Styles.tooltipsContainer}>
        <label className={Styles.InputLabel(required)}>{label}</label>
        {tooltipComponent}
      </div>
      <Autocomplete
        {...rest}
        multiple
        renderInput={renderInput}
        freeSolo={freeSolo}
        readOnly={disabled}
        options={options}
        filterOptions={(options, params) => {
          const filtered = filter(options, params);

          // Suggest the creation of a new value
          if (params.inputValue !== '' && !options.includes(params.inputValue)) {
            filtered.push(params.inputValue);
          }

          return filtered;
        }}
        renderOption={(props, option, state) => {
          if (!options.includes(option)) {
            option = `Add "${option}"`;
          }

          return <li {...props}>{option}</li>;
        }}
        componentsProps={{
          ...rest.componentsProps,
          popupIndicator: {
            ...rest.componentsProps?.popupIndicator,
            size: 'small',
          },
          clearIndicator: {
            ...rest.componentsProps?.clearIndicator,
            size: 'small',
          },
        }}
      />
      {errorComponent}
    </div>
  );
};

export { MultiSelectContainer, MultiSelectContainerProps };
