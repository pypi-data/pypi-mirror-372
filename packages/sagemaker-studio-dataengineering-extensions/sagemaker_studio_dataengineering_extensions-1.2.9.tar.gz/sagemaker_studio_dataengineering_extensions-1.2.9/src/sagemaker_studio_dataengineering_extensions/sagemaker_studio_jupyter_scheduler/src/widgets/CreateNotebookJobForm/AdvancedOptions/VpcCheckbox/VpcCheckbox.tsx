import React from 'react';
import { Scheduler } from '@jupyterlab/scheduler';
import Checkbox from '@mui/material/Checkbox';
import InfoIcon from '@mui/icons-material/Info';

import { Tooltip } from '../../../../components/tooltip/Tooltip';
import { FormState } from '../..';
import { i18nStrings } from '../../../../constants/common';
import { Link, LinkTarget } from '../../../../components/link';

import * as Styles from '../../../styles';

const vpcErrorStrings = i18nStrings.ScheduleNoteBook.MainPanel.ErrorMessages.VPCErrors;
const labelStrings = i18nStrings.ScheduleNoteBook.MainPanel.AdvancedOptions;
const tooltipsStrings = i18nStrings.ScheduleNoteBook.MainPanel.Tooltips;

const toolTipLink = 'https://docs.aws.amazon.com/sagemaker/latest/dg/create-notebook-auto-execution-advanced.html';

export interface VpcProps {
  isChecked: boolean;
  formState: FormState;
  initialSecurityGroups: string[];
  initialSubnets: string[];
  availableSubnets: string[];
  formErrors: Scheduler.ErrorsType;
  setChecked: (checked: boolean) => void;
  setFormState: (formState: FormState) => void;
  setFormErrors: (formErrors: Scheduler.ErrorsType) => void;
  ['data-testid']?: string;
}

const tooltipArea = (
  <div>
    <span className={Styles.TooltipTextContainer}> {tooltipsStrings.VPCTooltip} </span>
    <Link href={toolTipLink} target={LinkTarget.External}>
      <p className={Styles.TooltipLink}>{i18nStrings.ScheduleNoteBook.MainPanel.Tooltips.LearnMore}</p>
    </Link>
  </div>
);

const VpcCheckbox: React.FunctionComponent<VpcProps> = ({
  isChecked,
  formState,
  formErrors,
  initialSecurityGroups,
  initialSubnets,
  availableSubnets,
  setFormErrors,
  setChecked,
  setFormState,
  ...rest
}) => {
  return (
    <div className={Styles.TooltipCheckBoxContainer}>
      <Checkbox
        name={'vpc-check-box'}
        className={Styles.Checkbox}
        color={'primary'}
        checked={isChecked}
        onChange={e => {
          const checked = (e.target as HTMLInputElement).checked;
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
          } else {
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
        }}
        {...rest}
      />
      <label>{labelStrings.useVPC}</label>
      <Tooltip
        classes={{
          popperInteractive: Styles.PopperInteractive,
        }}
        title={tooltipArea}
      >
        <InfoIcon fontSize="small" />
      </Tooltip>
    </div>
  );
};

export { VpcCheckbox };
