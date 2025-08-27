from typing import Dict, List

from sagemaker_studio_jupyter_scheduler.model.models import (
    RuntimeEnvironmentParameterName,
    JobEnvironmentVariableName,
)


class RuntimeEnvironmentParameters:
    def __init__(self, parameters: Dict):
        self.parameters = parameters

    def _remove_dict_keys(self, original_dict: Dict, key_list: List[str]) -> Dict:
        new_dict = {**original_dict}
        for key in key_list:
            new_dict.pop(key, None)

        return new_dict

    @property
    def sm_image(self):
        return self.parameters.get(RuntimeEnvironmentParameterName.SM_IMAGE.value)

    @property
    def sm_kernel(self):
        return self.parameters.get(RuntimeEnvironmentParameterName.SM_KERNEL.value)

    @property
    def sm_init_script(self):
        return self.parameters.get(RuntimeEnvironmentParameterName.SM_INIT_SCRIPT.value)

    @property
    def sm_lcc_init_script_arn(self):
        return self.parameters.get(
            RuntimeEnvironmentParameterName.SM_LCC_INIT_SCRIPT_ARN.value
        )

    @property
    def s3_input(self):
        return self.parameters.get(RuntimeEnvironmentParameterName.S3_INPUT.value)

    @property
    def s3_input_account_id(self):
        return str(self.parameters.get(RuntimeEnvironmentParameterName.S3_INPUT_ACCOUNT_ID.value, ''))
    
    @property
    def s3_output(self):
        return self.parameters.get(RuntimeEnvironmentParameterName.S3_OUTPUT.value)

    @property
    def s3_output_account_id(self):
        return str(self.parameters.get(RuntimeEnvironmentParameterName.S3_OUTPUT_ACCOUNT_ID.value, ''))
    
    @property
    def max_run_time_in_seconds(self):
        return self.parameters.get(RuntimeEnvironmentParameterName.MAX_RUN_TIME_IN_SECONDS.value)
    
    @property
    def max_retry_attempts(self):
        return self.parameters.get(RuntimeEnvironmentParameterName.MAX_RETRY_ATTEMPTS.value)

    @property
    def role_arn(self):
        return self.parameters.get(RuntimeEnvironmentParameterName.ROLE_ARN.value)

    @property
    def security_group_ids(self):
        return self.parameters.get(
            RuntimeEnvironmentParameterName.VPC_SECURITY_GROUP_IDS.value
        )

    @property
    def subnets(self):
        return self.parameters.get(RuntimeEnvironmentParameterName.VPC_SUBNETS.value)

    @property
    def sm_output_kms_key(self):
        return self.parameters.get(
            RuntimeEnvironmentParameterName.SM_OUTPUT_KMS_KEY.value
        )

    @property
    def sm_volume_kms_key(self):
        return self.parameters.get(
            RuntimeEnvironmentParameterName.SM_VOLUME_KMS_KEY.value
        )
    
    @property
    def enable_network_isolation(self):
        return self.parameters.get(RuntimeEnvironmentParameterName.ENABLE_NETWORK_ISOLATION.value)

    @property
    def customer_environment_variables(self):
        return self._remove_dict_keys(
            self.parameters,
            [str(item) for item in RuntimeEnvironmentParameterName]
            + [str(item) for item in JobEnvironmentVariableName],
        )
    @property
    def max_retry_attempts(self):
        return self.parameters.get(
            RuntimeEnvironmentParameterName.MAX_RETRY_ATTEMPTS.value
        )

    @property
    def max_run_time_in_seconds(self):
        return self.parameters.get(
            RuntimeEnvironmentParameterName.MAX_RUN_TIME_IN_SECONDS.value
        )
    
    @property
    def sm_skip_efs_simulation(self):
        return self.parameters.get(
            RuntimeEnvironmentParameterName.SM_SKIP_EFS_SIMULATION.value, ""
        )
    