import React from 'react';
import MuiAutocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import { DropdownItem, SelectInputProps } from './types';

const SelectInput: React.FunctionComponent<SelectInputProps> = ({
  label,
  value,
  options,
  onChange,
  freeSolo,
  customListItemRender,
  renderInput,
  ...props
}: SelectInputProps) => {
  const optionsMap = Object.fromEntries(options.map((option) => [option.value, option]));
  let normalizedValue = value;
  if (!freeSolo && typeof value === 'string' && value in optionsMap) {
    normalizedValue = optionsMap[value];
  }
  return (
    <>
      <MuiAutocomplete<DropdownItem, false, boolean, boolean>
        {...props}
        id={`${label}-selectinput`}
        renderOption={(props, options, state) => (
          <li {...props}>{customListItemRender ? customListItemRender(options, options.label, state.selected) : options.label}</li>
        )}
        componentsProps={{
          ...props.componentsProps,
          popupIndicator: {
            ...props.componentsProps?.popupIndicator,
            size: 'small',
          },
        }}
        options={options}
        onChange={(_, value, reason) => {
          if ((value && !(typeof value === 'string')) || freeSolo) {
            onChange && onChange(value || '');
          }
        }}
        value={normalizedValue}
        renderInput={
          renderInput || ((params) => <TextField {...params} variant="outlined" size="small" margin="dense" />)
        }
      />
    </>
  );
};

export { SelectInput };
