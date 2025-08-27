import React from 'react';
import { TextField as MuiTextField, TextFieldProps as MuiTextFieldProps } from '@mui/material';
import { cx } from '@emotion/css';
import { TextInputBase, inputStyles, formHelperTextStyles } from './styles';
import { TextInputSize } from './types';
import { InputProps } from '@mui/material/Input';

export interface TextInputProps extends Omit<MuiTextFieldProps, 'children' | 'color' | 'size' | 'InputProps'> {
  readonly size?: TextInputSize;
  readonly InputProps?: Partial<InputProps>;
}

const TextInput: React.FunctionComponent<TextInputProps> = ({
  classes,
  className,
  InputProps,
  FormHelperTextProps,
  size = TextInputSize.Medium,
  variant,
  ...materialTextFieldProps
}) => {
  const classNames = cx(TextInputBase(), className, classes?.root);
  return (
    <MuiTextField
      data-testid={'inputField'}
      classes={{ root: classNames, ...classes }}
      variant={variant}
      role={'textField'}
      InputProps={{
        ...InputProps,
        classes: {
          root: cx(inputStyles(size), InputProps?.classes?.root),
          input: cx(inputStyles(size), InputProps?.classes?.input),
        },
      }}
      // InputLabelProps={{
      //   ...InputLabelProps,
      //   classes: { root: cx(inputLabelStyles().root, InputLabelProps?.classes?.root) },
      //   shrink: true,
      // }}
      FormHelperTextProps={{
        ...FormHelperTextProps,
        classes: { root: cx(formHelperTextStyles(), FormHelperTextProps?.classes?.root) },
      }}
      {...materialTextFieldProps}
    />
  );
};

export { TextInput };
