import { JobsView } from '@jupyterlab/scheduler';
import * as initialValueHelpers from '../widgets/CreateNotebookJobForm/initialValueHelpers';
import { IAutoDetectedConfig } from '../widgets/CreateNotebookJobForm';
import { getInitialImageValueForStudio } from '../widgets/CreateNotebookJobForm/Studio/studioHelpers';

type RuntimeEnvParams = initialValueHelpers.RuntimeEnvParams;

const {
  getInitialLCCValue,
  getInitialRoleArnValues,
  getInitialInitScriptValue,
  getInitialS3Values,
  getInitialKMSKeys,
  getNetworkAccessType,
  getInitialSubnetOrSecurityGroupValues,
  getInitialEnvironmentVariables
} = initialValueHelpers;

describe('LCC tests', () => {
  it('correctly gets initial LCC value', () => {
    const mockRuntimeEnvParameters: RuntimeEnvParams = {
      sm_lcc_init_script_arn: 'testing-lcc-arn'
    };

    let result = getInitialLCCValue(
      mockRuntimeEnvParameters,
      JobsView.CreateForm
    );
    expect(result).toEqual('No script');

    result = getInitialLCCValue(mockRuntimeEnvParameters, JobsView.JobDetail);
    expect(result).toEqual('testing-lcc-arn');

    result = getInitialLCCValue(mockRuntimeEnvParameters, JobsView.JobDefinitionDetail);
    expect(result).toEqual('testing-lcc-arn');
  });
});

describe('Role Arn tests', () => {
  it('correctly gets initial Role Arn value', () => {
    const mockRuntimeEnvParameters: RuntimeEnvParams = {
      role_arn: 'testing-role-arn'
    };

    const mockAutoDetectedConfigValues: IAutoDetectedConfig[] = [
      {
        name: 'role_arn',
        value: ['testing-role-arn-auto'],
        label: 'Role Arn',
        description: 'Description'
      }
    ];

    let result = getInitialRoleArnValues(
      {},
      mockAutoDetectedConfigValues,
      JobsView.CreateForm
    );
    expect(result).toEqual('testing-role-arn-auto');

    result = getInitialRoleArnValues(
      mockRuntimeEnvParameters,
      mockAutoDetectedConfigValues,
      JobsView.JobDefinitionDetail
    );
    expect(result).toEqual('testing-role-arn');

    result = getInitialRoleArnValues(
      mockRuntimeEnvParameters,
      mockAutoDetectedConfigValues,
      JobsView.JobDetail
    );
    expect(result).toEqual('testing-role-arn');
  });
});

describe('Init scripts tests', () => {
  it('correctly gets initial initialization script value', () => {
    const mockRuntimeEnvParameters: RuntimeEnvParams = {
      sm_init_script: 'runtime-value'
    };

    let result = getInitialInitScriptValue(
      {},
      JobsView.CreateForm
    );
    expect(result).toEqual('');

    result = getInitialInitScriptValue(
      mockRuntimeEnvParameters,
      JobsView.CreateForm
    );
    expect(result).toEqual('runtime-value');

    result = getInitialInitScriptValue(
      mockRuntimeEnvParameters,
      JobsView.JobDefinitionDetail
    );
    expect(result).toEqual('runtime-value');

    result = getInitialInitScriptValue(
      mockRuntimeEnvParameters,
      JobsView.JobDetail
    );
    expect(result).toEqual('runtime-value');
  });
});

describe('S3 value tests', () => {
  it('correctly gets initial S3 input/output folder values', () => {
    const mockRuntimeEnvParameters: RuntimeEnvParams = {
      s3_output: 'output-value',
      s3_input: 'input-value'
    };

    const mockAutoDetectedConfigValues: IAutoDetectedConfig[] = [
      {
        name: 's3_output',
        value: 's3://sagemaker-notebook-execution-748478975913/',
        label: 'Role Arn',
        description: 'Description'
      },
      {
        name: 's3_input',
        value: 's3://sagemaker-notebook-execution-748478975914/',
        label: 'Role Arn',
        description: 'Description'
      }
    ];

    let result = getInitialS3Values({}, mockAutoDetectedConfigValues, JobsView.CreateForm, 's3_output');
    expect(result).toEqual('s3://sagemaker-notebook-execution-748478975913/');

    result = getInitialS3Values({}, mockAutoDetectedConfigValues, JobsView.CreateForm, 's3_input');
    expect(result).toEqual('s3://sagemaker-notebook-execution-748478975914/');

    result = getInitialS3Values(mockRuntimeEnvParameters, mockAutoDetectedConfigValues, JobsView.CreateForm, 's3_input');
    expect(result).toEqual('input-value');

    result = getInitialS3Values(mockRuntimeEnvParameters, mockAutoDetectedConfigValues, JobsView.CreateForm, 's3_output');
    expect(result).toEqual('output-value');

    result = getInitialS3Values(mockRuntimeEnvParameters, mockAutoDetectedConfigValues, JobsView.JobDetail, 's3_input');
    expect(result).toEqual('input-value');

    result = getInitialS3Values(mockRuntimeEnvParameters, mockAutoDetectedConfigValues, JobsView.JobDefinitionDetail, 's3_input');
    expect(result).toEqual('input-value');

    result = getInitialS3Values(mockRuntimeEnvParameters, mockAutoDetectedConfigValues, JobsView.JobDetail, 's3_output');
    expect(result).toEqual('output-value');

    result = getInitialS3Values(mockRuntimeEnvParameters, mockAutoDetectedConfigValues, JobsView.JobDefinitionDetail, 's3_output');
    expect(result).toEqual('output-value');
  });
});

describe('KMS key value tests', () => {
  it('correctly gets KMS key values', () => {
    const mockRuntimeEnvParameters: RuntimeEnvParams = {
      sm_output_kms_key: 'output-kms-key-value',
      sm_volume_kms_key: 'volume-kms-key-vale'
    };

    // Output KMS key values
    let result = getInitialKMSKeys(
      mockRuntimeEnvParameters,
      JobsView.CreateForm,
      'sm_output_kms_key'
    );
    expect(result).toEqual(mockRuntimeEnvParameters.sm_output_kms_key);

    result = getInitialKMSKeys({}, JobsView.CreateForm, 'sm_output_kms_key');
    expect(result).toEqual('');

    result = getInitialKMSKeys(
      mockRuntimeEnvParameters,
      JobsView.JobDefinitionDetail,
      'sm_output_kms_key'
    );
    expect(result).toEqual(mockRuntimeEnvParameters.sm_output_kms_key);

    result = getInitialKMSKeys(
      mockRuntimeEnvParameters,
      JobsView.JobDetail,
      'sm_output_kms_key'
    );
    expect(result).toEqual(mockRuntimeEnvParameters.sm_output_kms_key);


    // EBS Volume key values
    result = getInitialKMSKeys(
      mockRuntimeEnvParameters,
      JobsView.CreateForm,
      'sm_volume_kms_key'
    );
    expect(result).toEqual(mockRuntimeEnvParameters.sm_volume_kms_key);

    result = getInitialKMSKeys({}, JobsView.CreateForm, 'sm_volume_kms_key');
    expect(result).toEqual('');

    result = getInitialKMSKeys(
      mockRuntimeEnvParameters,
      JobsView.JobDefinitionDetail,
      'sm_volume_kms_key'
    );
    expect(result).toEqual(mockRuntimeEnvParameters.sm_volume_kms_key);

    result = getInitialKMSKeys(
      mockRuntimeEnvParameters,
      JobsView.JobDetail,
      'sm_volume_kms_key'
    );
    expect(result).toEqual(mockRuntimeEnvParameters.sm_volume_kms_key);
  });
});

describe('Network Access Type tests', () => {
  it('correctly gets the Network Access type initial value', () => {
    let mockAutoDetectedConfigValues: IAutoDetectedConfig[] = [
      {
        name: 'app_network_access_type',
        label: 'App Network Access Type',
        description: 'Access type for the network',
        value: 'VpcOnly'
      }
    ];

    const result = getNetworkAccessType(mockAutoDetectedConfigValues, JobsView.CreateForm);
    expect(result).toEqual('VpcOnly');

    mockAutoDetectedConfigValues = [
      {
        name: 'app_network_access_type',
        label: 'App Network Access Type',
        description: 'Access type for the network',
        value: 'PublicInternetOnly'
      }
    ];
  });
});

describe('Image value tests', () => {
  it('Create Form', () => {
    let runtimeEnvironmentParameters = {
      sm_image:
        'arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-1.15-cpu-py36',
      sm_kernel: 'python3'
    };

    const preSelectedImage =
      'arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0';
    const preSelectedKernel = 'python3';
    const mockPreSelectedKernelFromNotebook = `${preSelectedKernel}__SAGEMAKER_INTERNAL__${preSelectedImage}`;

    let result = getInitialImageValueForStudio(
      runtimeEnvironmentParameters,
      mockPreSelectedKernelFromNotebook,
      JobsView.CreateForm
    );

    expect(result.arnEnvironment).toEqual(runtimeEnvironmentParameters.sm_image);
    expect(result.kernel).toEqual(runtimeEnvironmentParameters.sm_kernel);

    const image_version_number = '2'

    runtimeEnvironmentParameters = {
      sm_image:
        'arn:aws:sagemaker:us-west-2:236514542706:image-version/my-custom-image/' + image_version_number,
      sm_kernel: 'python3'
    };

    result = getInitialImageValueForStudio(
      runtimeEnvironmentParameters,
      mockPreSelectedKernelFromNotebook,
      JobsView.CreateForm
    );

    expect(result.arnEnvironment).toEqual('arn:aws:sagemaker:us-west-2:236514542706:image-version/my-custom-image/' + image_version_number);
    expect(result.kernel).toEqual(runtimeEnvironmentParameters.sm_kernel);
    expect(result.version).toEqual(image_version_number);

    result = getInitialImageValueForStudio(
      {},
      mockPreSelectedKernelFromNotebook,
      JobsView.CreateForm
    );

    expect(result.arnEnvironment).toEqual(preSelectedImage);
    expect(result.kernel).toEqual(preSelectedKernel);
  });

  it('Job Detail view', () => {
    const runtimeEnvironmentParameters = {
      sm_image:
        'arn:aws:sagemaker:us-west-2:236514542706:image/tensorflow-1.15-cpu-py36',
      sm_kernel: 'python3'
    };

    const preSelectedImage =
      'arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0';
    const preSelectedKernel = 'python3';
    const mockPreSelectedKernelFromNotebook = `${preSelectedKernel}__SAGEMAKER_INTERNAL__${preSelectedImage}`;

    let result = getInitialImageValueForStudio(
      runtimeEnvironmentParameters,
      mockPreSelectedKernelFromNotebook,
      JobsView.JobDetail
    );

    expect(result.arnEnvironment).toEqual(
      runtimeEnvironmentParameters.sm_image
    );
    expect(result.kernel).toEqual(runtimeEnvironmentParameters.sm_kernel);

    result = getInitialImageValueForStudio(
      {},
      mockPreSelectedKernelFromNotebook,
      JobsView.JobDefinitionDetail
    );

    expect(result.arnEnvironment).toBe('undefined/undefined');
    expect(result.kernel).toBe('undefined');
  });
});

describe('Environment variables tests', () => {
  const mockRuntimeEnvParameters: RuntimeEnvParams = {
    role_arn: 'testing-role-arn',
    sm_kernel: 'test-kernel',
    env_var: 'env_value1',
    env_var2: 'env_value2',
  };

  const result = getInitialEnvironmentVariables(mockRuntimeEnvParameters);
  expect(result).toEqual([
    { key: 'env_var', value: 'env_value1' },
    { key: 'env_var2', value: 'env_value2' }
  ]);
});

