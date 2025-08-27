import React from 'react';
import { Scheduler } from '@jupyterlab/scheduler';
interface IEnvironmentVariable {
    key: string;
    value: string;
}
interface Props {
    isDisabled: boolean;
    index: number;
    environmentParameters: IEnvironmentVariable[];
    setEnvironmentParameters: (environmentParameters: IEnvironmentVariable[]) => void;
    formErrors: Scheduler.ErrorsType;
    setFormErrors: (errors: Scheduler.ErrorsType) => void;
}
declare const EnvironmentVariable: React.FunctionComponent<Props>;
export { EnvironmentVariable, IEnvironmentVariable };
//# sourceMappingURL=EnvironmentVariable.d.ts.map