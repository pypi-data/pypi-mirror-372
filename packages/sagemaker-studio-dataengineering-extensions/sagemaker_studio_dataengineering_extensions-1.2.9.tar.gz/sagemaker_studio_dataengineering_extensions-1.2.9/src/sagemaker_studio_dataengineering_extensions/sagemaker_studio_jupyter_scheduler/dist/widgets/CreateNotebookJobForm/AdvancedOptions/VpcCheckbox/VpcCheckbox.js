import React from 'react';
import Checkbox from '@mui/material/Checkbox';
import InfoIcon from '@mui/icons-material/Info';
import { Tooltip } from '../../../../components/tooltip/Tooltip';
import { i18nStrings } from '../../../../constants/common';
import { Link, LinkTarget } from '../../../../components/link';
import * as Styles from '../../../styles';
const vpcErrorStrings = i18nStrings.ScheduleNoteBook.MainPanel.ErrorMessages.VPCErrors;
const labelStrings = i18nStrings.ScheduleNoteBook.MainPanel.AdvancedOptions;
const tooltipsStrings = i18nStrings.ScheduleNoteBook.MainPanel.Tooltips;
const toolTipLink = 'https://docs.aws.amazon.com/sagemaker/latest/dg/create-notebook-auto-execution-advanced.html';
const tooltipArea = (React.createElement("div", null,
    React.createElement("span", { className: Styles.TooltipTextContainer },
        " ",
        tooltipsStrings.VPCTooltip,
        " "),
    React.createElement(Link, { href: toolTipLink, target: LinkTarget.External },
        React.createElement("p", { className: Styles.TooltipLink }, i18nStrings.ScheduleNoteBook.MainPanel.Tooltips.LearnMore))));
const VpcCheckbox = ({ isChecked, formState, formErrors, initialSecurityGroups, initialSubnets, availableSubnets, setFormErrors, setChecked, setFormState, ...rest }) => {
    return (React.createElement("div", { className: Styles.TooltipCheckBoxContainer },
        React.createElement(Checkbox, { name: 'vpc-check-box', className: Styles.Checkbox, color: 'primary', checked: isChecked, onChange: e => {
                const checked = e.target.checked;
                setChecked(checked);
                if (checked) {
                    setFormState({
                        ...formState,
                        vpc_security_group_ids: initialSecurityGroups,
                        vpc_subnets: initialSubnets
                    });
                    if (initialSubnets.length === 0 && availableSubnets.length > 0) {
                        setFormErrors({
                            ...formErrors,
                            subnetError: `${vpcErrorStrings.RequiresPrivateSubnet} ${vpcErrorStrings.NoPrivateSubnetsInSageMakerDomain}. ${vpcErrorStrings.YouMayChooseOtherSubnets}`
                        });
                        return;
                    }
                    if (availableSubnets.length === 0) {
                        setFormErrors({
                            ...formErrors,
                            subnetError: `${vpcErrorStrings.RequiresPrivateSubnet} ${vpcErrorStrings.NoPrivateSubnetsInSageMakerDomain}`
                        });
                    }
                }
                else {
                    setFormState({
                        ...formState,
                        vpc_security_group_ids: [],
                        vpc_subnets: []
                    });
                    setFormErrors({
                        ...formErrors,
                        subnetError: '',
                        securityGroupError: ''
                    });
                }
            }, ...rest }),
        React.createElement("label", null, labelStrings.useVPC),
        React.createElement(Tooltip, { classes: {
                popperInteractive: Styles.PopperInteractive,
            }, title: tooltipArea },
            React.createElement(InfoIcon, { fontSize: "small" }))));
};
export { VpcCheckbox };
//# sourceMappingURL=VpcCheckbox.js.map