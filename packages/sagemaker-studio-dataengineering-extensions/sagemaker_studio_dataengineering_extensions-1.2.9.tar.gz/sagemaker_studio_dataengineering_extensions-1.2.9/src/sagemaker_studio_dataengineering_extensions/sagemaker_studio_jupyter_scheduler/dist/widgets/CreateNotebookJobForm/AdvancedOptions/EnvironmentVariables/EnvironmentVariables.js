import React from 'react';
import InfoIcon from '@mui/icons-material/Info';
import { Button } from '@mui/material';
import Alert from '@mui/material/Alert';
import { ErrorIconStyled } from '../../styles';
import { EnvironmentVariable } from './EnvironmentVariable';
import { TextInput } from '../../../../components/textinput';
import { Tooltip } from '../../../../components/tooltip/Tooltip';
import { i18nStrings } from '../../../../constants';
import * as Styles from './styles';
const widgetStrings = i18nStrings.ScheduleNoteBook.MainPanel.AdvancedOptions;
const tooltipsStrings = i18nStrings.ScheduleNoteBook.MainPanel.Tooltips;
const EnvironmentVariables = ({ allFieldsDisabled, isButtonDisabled, environmentVariables, setEnvironmentVariables, formErrors, ...rest }) => {
    const isError = !!formErrors.environmentVariablesError;
    const errorMessageWithIcon = (React.createElement("div", { className: ErrorIconStyled },
        React.createElement(Alert, { severity: "error" }, formErrors.environmentVariablesError)));
    return (React.createElement("div", { className: Styles.EnvironmentVariablesSection },
        React.createElement("div", { className: Styles.tooltipsContainer },
            React.createElement("label", { className: Styles.InputLabel }, widgetStrings.environmentVariables),
            !allFieldsDisabled ? (React.createElement(Tooltip, { title: tooltipsStrings.EnvironmentVariablesTooltip },
                React.createElement(InfoIcon, null))) : null),
        allFieldsDisabled && environmentVariables.length === 0 ? (React.createElement("div", { className: Styles.EnvironmentVariableContainer },
            React.createElement(TextInput, { InputProps: { readOnly: true }, placeholder: widgetStrings.Placeholders.NoneSelected }))) : (React.createElement(React.Fragment, null, environmentVariables.map((_, i) => (React.createElement(EnvironmentVariable, { isDisabled: allFieldsDisabled, key: i, environmentParameters: environmentVariables, setEnvironmentParameters: setEnvironmentVariables, index: i, formErrors: formErrors, ...rest }))))),
        isError && React.createElement("div", null, errorMessageWithIcon),
        !allFieldsDisabled && (React.createElement("div", null,
            React.createElement(Button, { disabled: isButtonDisabled, className: Styles.ConfigBtn, variant: 'contained', color: 'primary', size: 'small', onClick: () => {
                    setEnvironmentVariables([...environmentVariables, { key: '', value: '' }]);
                } }, widgetStrings.addEnvironmentvariable)))));
};
export { EnvironmentVariables };
//# sourceMappingURL=EnvironmentVariables.js.map