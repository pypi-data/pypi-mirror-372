import React from 'react';
import { Tooltip } from '../../components/tooltip/Tooltip';
import Alert from '@mui/material/Alert';
import InfoIcon from '@mui/icons-material/Info';
import Autocomplete, { createFilterOptions, } from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import * as Styles from './styles';
const filter = createFilterOptions();
const MultiSelectContainer = ({ label, required, errorMessage, disabled, renderInput, tooltip, disabledTooltip, freeSolo, options, ...rest }) => {
    var _a, _b;
    renderInput !== null && renderInput !== void 0 ? renderInput : (renderInput = (params) => (React.createElement(TextField, { ...params, variant: "outlined", size: "small", margin: "dense", placeholder: label })));
    // if disabled, display disabledTooltip (if present)
    //   otherwise, display tooltip (if present)
    const tooltipComponent = disabled ? (disabledTooltip ? (React.createElement(Tooltip, { title: disabledTooltip, className: Styles.tooltips },
        React.createElement(InfoIcon, null))) : (React.createElement(React.Fragment, null))) : tooltip ? (React.createElement(Tooltip, { title: tooltip, className: Styles.tooltips },
        React.createElement(InfoIcon, null))) : (React.createElement(React.Fragment, null));
    const errorComponent = errorMessage ? (React.createElement("div", { className: Styles.ErrorIconStyled },
        React.createElement(Alert, { severity: "error" }, errorMessage))) : (React.createElement(React.Fragment, null));
    return (React.createElement("div", { className: Styles.SelectInputContainer },
        React.createElement("div", { className: Styles.tooltipsContainer },
            React.createElement("label", { className: Styles.InputLabel(required) }, label),
            tooltipComponent),
        React.createElement(Autocomplete, { ...rest, multiple: true, renderInput: renderInput, freeSolo: freeSolo, readOnly: disabled, options: options, filterOptions: (options, params) => {
                const filtered = filter(options, params);
                // Suggest the creation of a new value
                if (params.inputValue !== '' && !options.includes(params.inputValue)) {
                    filtered.push(params.inputValue);
                }
                return filtered;
            }, renderOption: (props, option, state) => {
                if (!options.includes(option)) {
                    option = `Add "${option}"`;
                }
                return React.createElement("li", { ...props }, option);
            }, componentsProps: {
                ...rest.componentsProps,
                popupIndicator: {
                    ...(_a = rest.componentsProps) === null || _a === void 0 ? void 0 : _a.popupIndicator,
                    size: 'small',
                },
                clearIndicator: {
                    ...(_b = rest.componentsProps) === null || _b === void 0 ? void 0 : _b.clearIndicator,
                    size: 'small',
                },
            } }),
        errorComponent));
};
export { MultiSelectContainer };
//# sourceMappingURL=MultiSelectContainer.js.map