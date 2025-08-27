import React from 'react';
import { TextField as MuiTextField } from '@mui/material';
import { cx } from '@emotion/css';
import { TextInputBase, inputStyles, formHelperTextStyles } from './styles';
import { TextInputSize } from './types';
const TextInput = ({ classes, className, InputProps, FormHelperTextProps, size = TextInputSize.Medium, variant, ...materialTextFieldProps }) => {
    var _a, _b, _c;
    const classNames = cx(TextInputBase(), className, classes === null || classes === void 0 ? void 0 : classes.root);
    return (React.createElement(MuiTextField, { "data-testid": 'inputField', classes: { root: classNames, ...classes }, variant: variant, role: 'textField', InputProps: {
            ...InputProps,
            classes: {
                root: cx(inputStyles(size), (_a = InputProps === null || InputProps === void 0 ? void 0 : InputProps.classes) === null || _a === void 0 ? void 0 : _a.root),
                input: cx(inputStyles(size), (_b = InputProps === null || InputProps === void 0 ? void 0 : InputProps.classes) === null || _b === void 0 ? void 0 : _b.input),
            },
        }, 
        // InputLabelProps={{
        //   ...InputLabelProps,
        //   classes: { root: cx(inputLabelStyles().root, InputLabelProps?.classes?.root) },
        //   shrink: true,
        // }}
        FormHelperTextProps: {
            ...FormHelperTextProps,
            classes: { root: cx(formHelperTextStyles(), (_c = FormHelperTextProps === null || FormHelperTextProps === void 0 ? void 0 : FormHelperTextProps.classes) === null || _c === void 0 ? void 0 : _c.root) },
        }, ...materialTextFieldProps }));
};
export { TextInput };
//# sourceMappingURL=TextInput.js.map