/// <reference types="react" />
import { Scheduler } from '@jupyterlab/scheduler';
import { ContentsManager, ServerConnection } from '@jupyterlab/services';
import { FormState } from '../CreateNotebookJobform';
export interface IAutoDetectedConfig {
    name: string;
    label: string;
    description: string;
    value: any;
}
export type JobEnvironmentProps = Scheduler.IAdvancedOptionsProps & {
    isDisabled: boolean;
    executionEnvironments: {
        environment_configs: IAutoDetectedConfig[] | null;
        auto_detected_config: IAutoDetectedConfig[];
    };
    formState: FormState;
    formErrors: Scheduler.ErrorsType;
    setFormState: React.Dispatch<React.SetStateAction<FormState>>;
    setFormErrors: (errors: Scheduler.ErrorsType) => void;
    requestClient: ServerConnection.ISettings;
    contentsManager: ContentsManager;
};
export declare function fetchKernelAndImages(requestClient: ServerConnection.ISettings): Promise<any>;
//# sourceMappingURL=jobEnvironment.d.ts.map