import React from 'react';
import { Scheduler } from '@jupyterlab/scheduler';
import { FormState } from '../..';
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
declare const VpcCheckbox: React.FunctionComponent<VpcProps>;
export { VpcCheckbox };
//# sourceMappingURL=VpcCheckbox.d.ts.map