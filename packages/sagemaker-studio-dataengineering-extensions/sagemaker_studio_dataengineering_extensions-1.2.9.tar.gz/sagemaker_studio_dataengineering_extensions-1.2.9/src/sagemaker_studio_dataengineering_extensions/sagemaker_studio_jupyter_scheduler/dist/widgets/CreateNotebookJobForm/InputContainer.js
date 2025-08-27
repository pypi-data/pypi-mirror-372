import React from 'react';
import InfoIcon from '@mui/icons-material/Info';
import { TextInput } from '../../components/textinput';
import { Tooltip } from '../../components/tooltip';
import * as Styles from './styles';
import { strHasLength } from '../../utils';
const InputContainer = ({ labelInfo, required, toolTipText, errorMessage, ...inputProps }) => {
    return (React.createElement("div", { className: Styles.InputContainer },
        React.createElement("div", { className: Styles.tooltipsContainer },
            React.createElement("label", { className: Styles.InputLabel(required) },
                " ",
                labelInfo,
                " "),
            toolTipText && !inputProps.readOnly && (React.createElement(Tooltip, { title: toolTipText, className: Styles.tooltips },
                React.createElement(InfoIcon, null)))),
        React.createElement(TextInput, { ...inputProps, error: strHasLength(errorMessage), helperText: errorMessage, InputProps: {
                readOnly: inputProps.readOnly,
                ...inputProps.InputProps
            } })));
};
export { InputContainer };
//# sourceMappingURL=InputContainer.js.map