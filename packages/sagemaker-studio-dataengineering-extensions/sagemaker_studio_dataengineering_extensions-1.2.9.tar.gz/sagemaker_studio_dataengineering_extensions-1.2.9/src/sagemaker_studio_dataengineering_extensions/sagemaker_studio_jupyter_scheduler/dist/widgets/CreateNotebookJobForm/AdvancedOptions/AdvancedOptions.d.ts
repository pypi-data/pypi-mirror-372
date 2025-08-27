import React from 'react';
import { Scheduler } from '@jupyterlab/scheduler';
import { FormState } from '..';
import { IEnvironmentVariable } from './EnvironmentVariables';
import { ServerConnection } from '@jupyterlab/services';
interface AdvancedOptionProps {
    isDisabled: boolean;
    formState: FormState;
    setFormState: (state: FormState) => void;
    formErrors: Scheduler.ErrorsType;
    lccOptions: string[];
    environmentVariables: IEnvironmentVariable[];
    setEnvironmentVariables: (environmentParameters: IEnvironmentVariable[]) => void;
    availableSecurityGroups: string[];
    availableSubnets: string[];
    initialSubnets: string[];
    requestClient: ServerConnection.ISettings;
    initialSecurityGroups: string[];
    userDefaultValues: FormState;
    setSubnets: (subnets: string[]) => void;
    setRoleArn: (roleArn: string) => void;
    setSecurityGroups: (securityGroups: string[]) => void;
    onSelectLCCScript: (event: string) => void;
    handleChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
    handleNumberValueChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
    setFormValidationErrors: (errors: Scheduler.ErrorsType) => void;
    isVPCDomain: boolean;
    enableVPCSetting: boolean;
    setEnableVPCSetting: (checkBoxState: boolean) => void;
}
declare const AdvancedOptions: React.FunctionComponent<AdvancedOptionProps>;
export default AdvancedOptions;
//# sourceMappingURL=AdvancedOptions.d.ts.map