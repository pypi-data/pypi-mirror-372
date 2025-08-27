import { JobsView } from '@jupyterlab/scheduler';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { parseSpecName, strHasLength } from '../../utils';
import { FormState, IAutoDetectedConfig } from './CreateNotebookJobform';
import { IEnvironmentVariable } from './AdvancedOptions/EnvironmentVariables/EnvironmentVariable';

export const NO_SCRIPT = 'No script';

const DEFAULT_ENV_VARIABLES_LIST = new Set<string>([
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

export interface ISubnetSecurityGroupShape {
  name: string;
  is_selected: boolean;
}

export type ISubnetSecurityGroupValues = ISubnetSecurityGroupShape[];

export type RuntimeEnvParams =
  | {
    [key: string]: number | string | boolean;
  }
  | undefined;

export const getInitialSubnetOrSecurityGroupValues = (
  runtimeEnvironmentParameters: RuntimeEnvParams,
  autoDetectedConfig: IAutoDetectedConfig[],
  view: JobsView,
  key: 'vpc_security_group_ids' | 'vpc_subnets',
): string[] => {
  if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
    // these are comma separated values
    if (runtimeEnvironmentParameters) {
      if (!runtimeEnvironmentParameters[key]) {
        return [];
      }

      const asString = runtimeEnvironmentParameters[key] as string;
      return asString.split(',');
    }
  } else if (view === JobsView.CreateForm) {
    return autoDetectedConfig?.find((c) => c.name === key)?.value;
  }

  return [];
};

export const getInitialLCCValue = (
  runtimeEnvironmentParameters: RuntimeEnvParams,
  view: JobsView
): string => {
  if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
    if (runtimeEnvironmentParameters) {
      const val = runtimeEnvironmentParameters[
        'sm_lcc_init_script_arn'
      ] as string;

      if (!val) {
        return NO_SCRIPT;
      }

      return val;
    }

    return NO_SCRIPT;
  }

  return NO_SCRIPT;
};

export const getInitialRoleArnValues = (
  runtimeEnvironmentParameters: RuntimeEnvParams,
  autoDetectedConfig: IAutoDetectedConfig[],
  view: JobsView,
): string => {
  if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
    if (runtimeEnvironmentParameters) {
      return runtimeEnvironmentParameters['role_arn'] as string;
    }
  } else if (view === JobsView.CreateForm) {
    if (runtimeEnvironmentParameters && 'role_arn' in runtimeEnvironmentParameters) {
      return runtimeEnvironmentParameters['role_arn'] as string;
    }

    const autoDetectedValue = autoDetectedConfig?.find((c) => c.name === 'role_arn')?.value;

    if (autoDetectedValue?.length > 0) {
      return autoDetectedValue[0];
    }
  }

  return '';
};

export const getInitialImageValue = (
  runtimeEnvironmentParameters: RuntimeEnvParams,
  autoDetectedConfig: IAutoDetectedConfig[],
) => {
  if (runtimeEnvironmentParameters) {
    const { sm_kernel, sm_image } = runtimeEnvironmentParameters;
    const KERNEL_IMAGE_KEY = `${sm_kernel}__SAGEMAKER_INTERNAL__${sm_image}`;
    return parseSpecName(KERNEL_IMAGE_KEY);
  }

  const autoDetectedImageValues = autoDetectedConfig?.find((c) => c.name === 'image')?.value;
  const autoDetectedKernelValues = autoDetectedConfig?.find((c) => c.name === 'kernel')?.value;

  if (strHasLength(autoDetectedImageValues) && strHasLength(autoDetectedKernelValues)) {
    return parseSpecName(`${autoDetectedKernelValues}__SAGEMAKER_INTERNAL__${autoDetectedImageValues}`);
  }

  return {
    kernel: null,
    arnEnvironment: null,
    version: null,
  };
};

export const getInitialInitScriptValue = (runtimeEnvironmentParameters: RuntimeEnvParams, view: JobsView): string => {
  if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
    if (runtimeEnvironmentParameters) {
      return runtimeEnvironmentParameters['sm_init_script'] as string;
    }
  } else if (view === JobsView.CreateForm) {
    if (runtimeEnvironmentParameters && 'sm_init_script' in runtimeEnvironmentParameters) {
      return runtimeEnvironmentParameters['sm_init_script'] as string;
    }
  }

  return '';
};

export const getInitialS3Values = (
  runtimeEnvironmentParameters: RuntimeEnvParams,
  autoDetectedConfig: IAutoDetectedConfig[],
  view: JobsView,
  key: 's3_output' | 's3_input',
): string => {
  if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
    if (runtimeEnvironmentParameters) {
      return runtimeEnvironmentParameters[key] as string;
    }
  } else if (view === JobsView.CreateForm) {
    if (runtimeEnvironmentParameters && key in runtimeEnvironmentParameters) {
      return runtimeEnvironmentParameters[key] as string;
    }

    return autoDetectedConfig?.find((c) => c.name === key)?.value || '';
  }

  return '';
};

export const getInitialKeyValueAsBoolean = (
  runtimeEnvironmentParameters: RuntimeEnvParams,
  view: JobsView,
  key: 'enable_network_isolation',
): boolean => {
  if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
    if (runtimeEnvironmentParameters) {
      return Boolean(runtimeEnvironmentParameters[key]);
    }
  } else if (view === JobsView.CreateForm) {
    if (runtimeEnvironmentParameters && key in runtimeEnvironmentParameters) {
      return Boolean(runtimeEnvironmentParameters[key]);
    }
  }

  return false;
};

export const getInitialKeyValue = (
  runtimeEnvironmentParameters: RuntimeEnvParams,
  view: JobsView,
  defaultValue: number,
  key: 'max_retry_attempts' | 'max_run_time_in_seconds',
): number => {
  if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
    if (runtimeEnvironmentParameters) {
      return runtimeEnvironmentParameters[key] as number;
    }
  } else if (view === JobsView.CreateForm) {
    if (runtimeEnvironmentParameters && key in runtimeEnvironmentParameters) {
      return runtimeEnvironmentParameters[key] as number;
    }
  }

  return defaultValue;
};

export const getInitialKMSKeys = (
  runtimeEnvironmentParameters: RuntimeEnvParams,
  view: JobsView,
  key: 'sm_output_kms_key' | 'sm_volume_kms_key',
): string => {
  if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
    if (runtimeEnvironmentParameters) {
      return runtimeEnvironmentParameters[key] as string;
    }
  } else if (view === JobsView.CreateForm) {
    if (runtimeEnvironmentParameters && key in runtimeEnvironmentParameters) {
      return runtimeEnvironmentParameters[key] as string;
    }
  }

  return '';
};

export const getInitialEnvironmentVariables = (
  runtimeEnvironmentParameters: RuntimeEnvParams,
): IEnvironmentVariable[] => {
  const initialEnvironmentVariables: IEnvironmentVariable[] = [];

  // get all key/value pairs that are not part of default set => these are the env variables
  if (runtimeEnvironmentParameters) {
    for (const envVar in runtimeEnvironmentParameters) {
      if (!DEFAULT_ENV_VARIABLES_LIST.has(envVar)) {
        const entry = {
          key: envVar,
          value: runtimeEnvironmentParameters[envVar] as string,
        };

        initialEnvironmentVariables.push(entry);
      }
    }
  }

  return initialEnvironmentVariables;
};

export const getNetworkAccessType = (autoDetectedConfig: IAutoDetectedConfig[], view: JobsView): string => {
  if (view === JobsView.CreateForm) {
    return (autoDetectedConfig?.find((c) => c.name === 'app_network_access_type')?.value as string) || '';
  }

  return '';
};

/**
 * Get the most recently cached value of the advanced options from the setting registry.
 * @returns Partial representation of advanced options
 */
export async function getAdvancedOptionsFromSettingRegistry(settingRegistry: ISettingRegistry):
  Promise<Partial<FormState> | undefined> {
  const state = await settingRegistry.get(SETTING_REGISTRY_PLUGIN, SETTING_REGISTRY_ADVANCED_OPTIONS_KEY);
  return state.composite as Partial<FormState> | undefined;
}
