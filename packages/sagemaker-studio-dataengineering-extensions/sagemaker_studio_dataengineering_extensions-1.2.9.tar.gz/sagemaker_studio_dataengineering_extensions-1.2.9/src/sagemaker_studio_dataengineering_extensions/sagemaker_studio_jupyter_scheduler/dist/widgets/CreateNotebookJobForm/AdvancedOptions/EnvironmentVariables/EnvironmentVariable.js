import React from 'react';
import CloseIcon from '@mui/icons-material/Close';
import IconButton from '@mui/material/IconButton';
import { i18nStrings } from '../../../../constants/common';
import { InputContainer } from '../../InputContainer';
import * as Styles from './styles';
const KEY_REGEX = new RegExp('[a-zA-Z_][a-zA-Z0-9_]*');
const VALUE_REGEX = new RegExp('[\\S\\s]*');
const errorMessageStrings = i18nStrings.ScheduleNoteBook.MainPanel.ErrorMessages.AdvancedOptions;
const widgetStrings = i18nStrings.ScheduleNoteBook.MainPanel.AdvancedOptions;
const EnvironmentVariable = ({ isDisabled, environmentParameters, setEnvironmentParameters, index, formErrors, setFormErrors, }) => {
    const currentEnvironmentVariable = environmentParameters[index];
    const deleteKeyValue = (index) => {
        const newArray = [...environmentParameters];
        newArray.splice(index, 1);
        setEnvironmentParameters(newArray);
        setFormErrors({
            ...formErrors,
            environmentVariablesError: '',
        });
    };
    const handleChange = (e) => {
        const name = e.currentTarget.name;
        const value = e.target.value;
        const [field, i] = name.split('-');
        const updateItem = field === 'envKey'
            ? { key: value, value: environmentParameters[i].value }
            : { key: environmentParameters[i].key, value: value };
        const newArray = [...environmentParameters];
        newArray.splice(i, 1, updateItem);
        setEnvironmentParameters(newArray);
    };
    const handleBlur = () => {
        const { key, value } = currentEnvironmentVariable;
        if (key.length < 1 || value.length < 1) {
            setFormErrors({
                ...formErrors,
                environmentVariablesError: errorMessageStrings.EnvironmentVariableEmptyError,
            });
            return;
        }
        if (key.length > 512 || value.length > 512) {
            setFormErrors({
                ...formErrors,
                environmentVariablesError: errorMessageStrings.EnvironmentVariableLengthError,
            });
            return;
        }
        if (!KEY_REGEX.test(key) || !VALUE_REGEX.test(value)) {
            setFormErrors({
                ...formErrors,
                environmentVariablesError: errorMessageStrings.EnvironmentVariableFormatError,
            });
            return;
        }
        setFormErrors({
            ...formErrors,
            environmentVariablesError: '',
        });
    };
    return (React.createElement("div", { className: Styles.EnvironmentVariablesContainer },
        React.createElement(InputContainer, { className: Styles.EnvironmentVariablesInput, readOnly: isDisabled, name: `envKey-${index}`, labelInfo: widgetStrings.Key, value: environmentParameters[index].key, onChange: handleChange, onBlur: handleBlur }),
        React.createElement(InputContainer, { className: Styles.EnvironmentVariablesInput, readOnly: isDisabled, name: `envValue-${index}`, labelInfo: widgetStrings.Value, value: environmentParameters[index].value, onChange: handleChange, onBlur: handleBlur }),
        React.createElement("div", null, !isDisabled && (React.createElement(IconButton, { onClick: () => {
                deleteKeyValue(index);
                setFormErrors({
                    ...formErrors,
                    environmentVariablesError: '',
                });
            }, size: "large" },
            React.createElement(CloseIcon, null))))));
};
export { EnvironmentVariable };
//# sourceMappingURL=EnvironmentVariable.js.map