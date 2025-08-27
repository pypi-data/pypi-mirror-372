import React from 'react';
import { Tooltip } from '../../components/tooltip/Tooltip';
import { SelectInput } from '../../components/selectinput';
import InfoIcon from '@mui/icons-material/Info';
import * as Styles from './styles';
import * as WidgetStyles from '../styles';
const SelectInputContainer = ({ label, required = true, toolTipText, toolTipArea, errorMessage, ...inputProps }) => {
    const toolTipAreaComponent = toolTipArea && (React.createElement("div", null,
        React.createElement("span", { className: WidgetStyles.TooltipTextContainer }, toolTipArea.descriptionText),
        toolTipArea.toolTipComponent));
    return (React.createElement("div", { className: Styles.SelectInputContainer },
        React.createElement("div", { className: Styles.tooltipsContainer },
            React.createElement("label", { className: Styles.InputLabel(required) }, label),
            (toolTipText || toolTipArea) && !inputProps.readOnly && (React.createElement(Tooltip, { title: toolTipAreaComponent || toolTipText || '', className: Styles.tooltips, disableInteractive: toolTipArea === null },
                React.createElement(InfoIcon, null)))),
        React.createElement(SelectInput, { label: label, disableClearable: true, ...inputProps })));
};
export { SelectInputContainer };
//# sourceMappingURL=SelectInputContainer.js.map