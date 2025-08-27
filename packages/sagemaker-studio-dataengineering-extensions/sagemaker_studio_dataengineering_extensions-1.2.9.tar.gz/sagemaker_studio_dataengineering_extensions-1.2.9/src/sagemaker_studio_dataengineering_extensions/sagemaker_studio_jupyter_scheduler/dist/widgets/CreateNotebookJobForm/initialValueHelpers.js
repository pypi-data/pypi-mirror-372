import { JobsView } from '@jupyterlab/scheduler';
import { parseSpecName, strHasLength } from '../../utils';
export const NO_SCRIPT = 'No script';
const DEFAULT_ENV_VARIABLES_LIST = new Set([
    'sm_kernel',
    'sm_image',
    'sm_lcc_init_script_arn',
    'role_arn',
    'vpc_security_group_ids',
    'vpc_subnets',
    's3_input',
    's3_output',
    'sm_init_script',
    'sm_output_kms_key',
    'sm_volume_kms_key',
    'max_run_time_in_seconds',
    'max_retry_attempts',
    'enable_network_isolation',
    // DataZone environment variables that are automatically added for SMUS environments
    'DataZoneDomainId',
    'DataZoneProjectId',
    'DataZoneEndpoint',
    'DataZoneDomainRegion',
    'DataZoneStage',
    'DataZoneEnvironmentId',
    'ProjectS3Path'
]);
const SETTING_REGISTRY_PLUGIN = '@amzn/sagemaker-studio-jupyter-scheduler:advanced-options';
const SETTING_REGISTRY_ADVANCED_OPTIONS_KEY = 'advancedOptions';
export const getInitialSubnetOrSecurityGroupValues = (runtimeEnvironmentParameters, autoDetectedConfig, view, key) => {
    var _a;
    if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
        // these are comma separated values
        if (runtimeEnvironmentParameters) {
            if (!runtimeEnvironmentParameters[key]) {
                return [];
            }
            const asString = runtimeEnvironmentParameters[key];
            return asString.split(',');
        }
    }
    else if (view === JobsView.CreateForm) {
        return (_a = autoDetectedConfig === null || autoDetectedConfig === void 0 ? void 0 : autoDetectedConfig.find((c) => c.name === key)) === null || _a === void 0 ? void 0 : _a.value;
    }
    return [];
};
export const getInitialLCCValue = (runtimeEnvironmentParameters, view) => {
    if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
        if (runtimeEnvironmentParameters) {
            const val = runtimeEnvironmentParameters['sm_lcc_init_script_arn'];
            if (!val) {
                return NO_SCRIPT;
            }
            return val;
        }
        return NO_SCRIPT;
    }
    return NO_SCRIPT;
};
export const getInitialRoleArnValues = (runtimeEnvironmentParameters, autoDetectedConfig, view) => {
    var _a;
    if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
        if (runtimeEnvironmentParameters) {
            return runtimeEnvironmentParameters['role_arn'];
        }
    }
    else if (view === JobsView.CreateForm) {
        if (runtimeEnvironmentParameters && 'role_arn' in runtimeEnvironmentParameters) {
            return runtimeEnvironmentParameters['role_arn'];
        }
        const autoDetectedValue = (_a = autoDetectedConfig === null || autoDetectedConfig === void 0 ? void 0 : autoDetectedConfig.find((c) => c.name === 'role_arn')) === null || _a === void 0 ? void 0 : _a.value;
        if ((autoDetectedValue === null || autoDetectedValue === void 0 ? void 0 : autoDetectedValue.length) > 0) {
            return autoDetectedValue[0];
        }
    }
    return '';
};
export const getInitialImageValue = (runtimeEnvironmentParameters, autoDetectedConfig) => {
    var _a, _b;
    if (runtimeEnvironmentParameters) {
        const { sm_kernel, sm_image } = runtimeEnvironmentParameters;
        const KERNEL_IMAGE_KEY = `${sm_kernel}__SAGEMAKER_INTERNAL__${sm_image}`;
        return parseSpecName(KERNEL_IMAGE_KEY);
    }
    const autoDetectedImageValues = (_a = autoDetectedConfig === null || autoDetectedConfig === void 0 ? void 0 : autoDetectedConfig.find((c) => c.name === 'image')) === null || _a === void 0 ? void 0 : _a.value;
    const autoDetectedKernelValues = (_b = autoDetectedConfig === null || autoDetectedConfig === void 0 ? void 0 : autoDetectedConfig.find((c) => c.name === 'kernel')) === null || _b === void 0 ? void 0 : _b.value;
    if (strHasLength(autoDetectedImageValues) && strHasLength(autoDetectedKernelValues)) {
        return parseSpecName(`${autoDetectedKernelValues}__SAGEMAKER_INTERNAL__${autoDetectedImageValues}`);
    }
    return {
        kernel: null,
        arnEnvironment: null,
        version: null,
    };
};
export const getInitialInitScriptValue = (runtimeEnvironmentParameters, view) => {
    if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
        if (runtimeEnvironmentParameters) {
            return runtimeEnvironmentParameters['sm_init_script'];
        }
    }
    else if (view === JobsView.CreateForm) {
        if (runtimeEnvironmentParameters && 'sm_init_script' in runtimeEnvironmentParameters) {
            return runtimeEnvironmentParameters['sm_init_script'];
        }
    }
    return '';
};
export const getInitialS3Values = (runtimeEnvironmentParameters, autoDetectedConfig, view, key) => {
    var _a;
    if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
        if (runtimeEnvironmentParameters) {
            return runtimeEnvironmentParameters[key];
        }
    }
    else if (view === JobsView.CreateForm) {
        if (runtimeEnvironmentParameters && key in runtimeEnvironmentParameters) {
            return runtimeEnvironmentParameters[key];
        }
        return ((_a = autoDetectedConfig === null || autoDetectedConfig === void 0 ? void 0 : autoDetectedConfig.find((c) => c.name === key)) === null || _a === void 0 ? void 0 : _a.value) || '';
    }
    return '';
};
export const getInitialKeyValueAsBoolean = (runtimeEnvironmentParameters, view, key) => {
    if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
        if (runtimeEnvironmentParameters) {
            return Boolean(runtimeEnvironmentParameters[key]);
        }
    }
    else if (view === JobsView.CreateForm) {
        if (runtimeEnvironmentParameters && key in runtimeEnvironmentParameters) {
            return Boolean(runtimeEnvironmentParameters[key]);
        }
    }
    return false;
};
export const getInitialKeyValue = (runtimeEnvironmentParameters, view, defaultValue, key) => {
    if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
        if (runtimeEnvironmentParameters) {
            return runtimeEnvironmentParameters[key];
        }
    }
    else if (view === JobsView.CreateForm) {
        if (runtimeEnvironmentParameters && key in runtimeEnvironmentParameters) {
            return runtimeEnvironmentParameters[key];
        }
    }
    return defaultValue;
};
export const getInitialKMSKeys = (runtimeEnvironmentParameters, view, key) => {
    if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
        if (runtimeEnvironmentParameters) {
            return runtimeEnvironmentParameters[key];
        }
    }
    else if (view === JobsView.CreateForm) {
        if (runtimeEnvironmentParameters && key in runtimeEnvironmentParameters) {
            return runtimeEnvironmentParameters[key];
        }
    }
    return '';
};
export const getInitialEnvironmentVariables = (runtimeEnvironmentParameters) => {
    const initialEnvironmentVariables = [];
    // get all key/value pairs that are not part of default set => these are the env variables
    if (runtimeEnvironmentParameters) {
        for (const envVar in runtimeEnvironmentParameters) {
            if (!DEFAULT_ENV_VARIABLES_LIST.has(envVar)) {
                const entry = {
                    key: envVar,
                    value: runtimeEnvironmentParameters[envVar],
                };
                initialEnvironmentVariables.push(entry);
            }
        }
    }
    return initialEnvironmentVariables;
};
export const getNetworkAccessType = (autoDetectedConfig, view) => {
    var _a;
    if (view === JobsView.CreateForm) {
        return ((_a = autoDetectedConfig === null || autoDetectedConfig === void 0 ? void 0 : autoDetectedConfig.find((c) => c.name === 'app_network_access_type')) === null || _a === void 0 ? void 0 : _a.value) || '';
    }
    return '';
};
/**
 * Get the most recently cached value of the advanced options from the setting registry.
 * @returns Partial representation of advanced options
 */
export async function getAdvancedOptionsFromSettingRegistry(settingRegistry) {
    const state = await settingRegistry.get(SETTING_REGISTRY_PLUGIN, SETTING_REGISTRY_ADVANCED_OPTIONS_KEY);
    return state.composite;
}
//# sourceMappingURL=initialValueHelpers.js.map