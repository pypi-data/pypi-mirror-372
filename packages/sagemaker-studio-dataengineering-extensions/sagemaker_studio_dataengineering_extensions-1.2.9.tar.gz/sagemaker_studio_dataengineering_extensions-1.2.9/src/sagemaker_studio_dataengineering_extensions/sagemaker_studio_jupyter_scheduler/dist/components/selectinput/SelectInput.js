import React from 'react';
import MuiAutocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
const SelectInput = ({ label, value, options, onChange, freeSolo, customListItemRender, renderInput, ...props }) => {
    var _a;
    const optionsMap = Object.fromEntries(options.map((option) => [option.value, option]));
    let normalizedValue = value;
    if (!freeSolo && typeof value === 'string' && value in optionsMap) {
        normalizedValue = optionsMap[value];
    }
    return (React.createElement(React.Fragment, null,
        React.createElement(MuiAutocomplete, { ...props, id: `${label}-selectinput`, renderOption: (props, options, state) => (React.createElement("li", { ...props }, customListItemRender ? customListItemRender(options, options.label, state.selected) : options.label)), componentsProps: {
                ...props.componentsProps,
                popupIndicator: {
                    ...(_a = props.componentsProps) === null || _a === void 0 ? void 0 : _a.popupIndicator,
                    size: 'small',
                },
            }, options: options, onChange: (_, value, reason) => {
                if ((value && !(typeof value === 'string')) || freeSolo) {
                    onChange && onChange(value || '');
                }
            }, value: normalizedValue, renderInput: renderInput || ((params) => React.createElement(TextField, { ...params, variant: "outlined", size: "small", margin: "dense" })) })));
};
export { SelectInput };
//# sourceMappingURL=SelectInput.js.map