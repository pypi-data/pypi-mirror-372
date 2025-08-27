import React from 'react';
import { TextFieldProps as MuiTextFieldProps } from '@mui/material';
import { TextInputSize } from './types';
import { InputProps } from '@mui/material/Input';
export interface TextInputProps extends Omit<MuiTextFieldProps, 'children' | 'color' | 'size' | 'InputProps'> {
    readonly size?: TextInputSize;
    readonly InputProps?: Partial<InputProps>;
}
declare const TextInput: React.FunctionComponent<TextInputProps>;
export { TextInput };
//# sourceMappingURL=TextInput.d.ts.map