import React from 'react';
import { Scheduler } from '@jupyterlab/scheduler';
import { ContentsManager, ServerConnection } from '@jupyterlab/services';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { IAutoDetectedConfig } from './JobEnvironment';
interface FormState {
    sm_lcc_init_script_arn: string;
    sm_init_script: string;
    role_arn: string;
    vpc_security_group_ids: string[];
    vpc_subnets: string[];
    sm_kernel: string;
    sm_image: string;
    s3_input: string;
    s3_input_account_id: string;
    s3_output: string;
    s3_output_account_id: string;
    sm_output_kms_key: string;
    sm_volume_kms_key: string;
    max_retry_attempts: number;
    max_run_time_in_seconds: number;
    enable_network_isolation: boolean;
}
export type CreateNotebookJobFormProps = Scheduler.IAdvancedOptionsProps & {
    requestClient: ServerConnection.ISettings;
    settingRegistry: ISettingRegistry;
    executionEnvironments: {
        environment_configs: IAutoDetectedConfig[] | null;
        auto_detected_config: IAutoDetectedConfig[];
    };
    contentsManager: ContentsManager;
};
declare const CreateNotebookJobForm: React.FunctionComponent<CreateNotebookJobFormProps>;
export { CreateNotebookJobForm, FormState, IAutoDetectedConfig };
//# sourceMappingURL=CreateNotebookJobform.d.ts.map