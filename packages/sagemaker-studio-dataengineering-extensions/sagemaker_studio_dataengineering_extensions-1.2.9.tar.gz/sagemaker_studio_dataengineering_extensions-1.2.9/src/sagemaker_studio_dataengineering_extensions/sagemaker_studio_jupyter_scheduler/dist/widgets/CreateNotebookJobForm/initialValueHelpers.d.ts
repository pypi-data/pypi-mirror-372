import { JobsView } from '@jupyterlab/scheduler';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { FormState, IAutoDetectedConfig } from './CreateNotebookJobform';
import { IEnvironmentVariable } from './AdvancedOptions/EnvironmentVariables/EnvironmentVariable';
export declare const NO_SCRIPT = "No script";
export interface ISubnetSecurityGroupShape {
    name: string;
    is_selected: boolean;
}
export type ISubnetSecurityGroupValues = ISubnetSecurityGroupShape[];
export type RuntimeEnvParams = {
    [key: string]: number | string | boolean;
} | undefined;
export declare const getInitialSubnetOrSecurityGroupValues: (runtimeEnvironmentParameters: RuntimeEnvParams, autoDetectedConfig: IAutoDetectedConfig[], view: JobsView, key: 'vpc_security_group_ids' | 'vpc_subnets') => string[];
export declare const getInitialLCCValue: (runtimeEnvironmentParameters: RuntimeEnvParams, view: JobsView) => string;
export declare const getInitialRoleArnValues: (runtimeEnvironmentParameters: RuntimeEnvParams, autoDetectedConfig: IAutoDetectedConfig[], view: JobsView) => string;
export declare const getInitialImageValue: (runtimeEnvironmentParameters: RuntimeEnvParams, autoDetectedConfig: IAutoDetectedConfig[]) => import("../../types/kernels").ParsedSpecName;
export declare const getInitialInitScriptValue: (runtimeEnvironmentParameters: RuntimeEnvParams, view: JobsView) => string;
export declare const getInitialS3Values: (runtimeEnvironmentParameters: RuntimeEnvParams, autoDetectedConfig: IAutoDetectedConfig[], view: JobsView, key: 's3_output' | 's3_input') => string;
export declare const getInitialKeyValueAsBoolean: (runtimeEnvironmentParameters: RuntimeEnvParams, view: JobsView, key: 'enable_network_isolation') => boolean;
export declare const getInitialKeyValue: (runtimeEnvironmentParameters: RuntimeEnvParams, view: JobsView, defaultValue: number, key: 'max_retry_attempts' | 'max_run_time_in_seconds') => number;
export declare const getInitialKMSKeys: (runtimeEnvironmentParameters: RuntimeEnvParams, view: JobsView, key: 'sm_output_kms_key' | 'sm_volume_kms_key') => string;
export declare const getInitialEnvironmentVariables: (runtimeEnvironmentParameters: RuntimeEnvParams) => IEnvironmentVariable[];
export declare const getNetworkAccessType: (autoDetectedConfig: IAutoDetectedConfig[], view: JobsView) => string;
/**
 * Get the most recently cached value of the advanced options from the setting registry.
 * @returns Partial representation of advanced options
 */
export declare function getAdvancedOptionsFromSettingRegistry(settingRegistry: ISettingRegistry): Promise<Partial<FormState> | undefined>;
//# sourceMappingURL=initialValueHelpers.d.ts.map