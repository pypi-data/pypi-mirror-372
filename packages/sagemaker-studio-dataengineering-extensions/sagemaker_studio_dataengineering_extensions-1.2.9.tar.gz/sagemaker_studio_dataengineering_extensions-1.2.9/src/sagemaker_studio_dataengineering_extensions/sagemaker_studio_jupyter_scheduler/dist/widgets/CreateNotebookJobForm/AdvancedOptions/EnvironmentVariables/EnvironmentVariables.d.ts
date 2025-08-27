import React from 'react';
import { Scheduler } from '@jupyterlab/scheduler';
interface IEnvironmentVariable {
    key: string;
    value: string;
}
interface Props {
    isButtonDisabled: boolean;
    allFieldsDisabled: boolean;
    environmentVariables: IEnvironmentVariable[];
    setEnvironmentVariables: (environmentParameters: IEnvironmentVariable[]) => void;
    formErrors: Scheduler.ErrorsType;
    setFormErrors: (errors: Scheduler.ErrorsType) => void;
}
declare const EnvironmentVariables: React.FunctionComponent<Props>;
export { EnvironmentVariables };
//# sourceMappingURL=EnvironmentVariables.d.ts.map