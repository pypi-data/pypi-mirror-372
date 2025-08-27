from sagemaker_studio_jupyter_scheduler.model.runtime_environment_parameters import (
    RuntimeEnvironmentParameters,
)


def test_runtime_environment_parameters():
    # Given
    raw_parameters = {
        "sm_image": "mock-sm_image",
        "sm_kernel": "mock-sm_kernel",
        "sm_init_script": "mock-sm_init_script",
        "sm_lcc_init_script_arn": "mock-sm_lcc_init_script_arn",
        "s3_input": "mock-s3_input",
        "s3_output": "mock-s3_output",
        "role_arn": "mock-role_arn",
        "vpc_security_group_ids": "mock-vpc_security_group_ids",
        "vpc_subnets": "mock-vpc_subnets",
        "other_param": "mock-other_param",
        "x": 1,
        "yet_another_param": "mock-yet_another_param",
        "max_retry_attempts": "mock-max_retry_attempts",
        "max_run_time_in_seconds": "mock-max_run_time_in_seconds",
    }

    # When
    runtime_environment_parameters = RuntimeEnvironmentParameters(raw_parameters)

    # Then
    assert runtime_environment_parameters.sm_image == "mock-sm_image"
    assert runtime_environment_parameters.sm_kernel == "mock-sm_kernel"
    assert runtime_environment_parameters.sm_init_script == "mock-sm_init_script"
    assert (
        runtime_environment_parameters.sm_lcc_init_script_arn
        == "mock-sm_lcc_init_script_arn"
    )
    assert runtime_environment_parameters.s3_input == "mock-s3_input"
    assert runtime_environment_parameters.s3_output == "mock-s3_output"
    assert runtime_environment_parameters.role_arn == "mock-role_arn"
    assert (
        runtime_environment_parameters.security_group_ids
        == "mock-vpc_security_group_ids"
    )
    assert runtime_environment_parameters.subnets == "mock-vpc_subnets"
    assert runtime_environment_parameters.customer_environment_variables == {
        "other_param": "mock-other_param",
        "x": 1,
        "yet_another_param": "mock-yet_another_param",
    }
    assert (
        runtime_environment_parameters.max_retry_attempts == "mock-max_retry_attempts"
    )
    assert (
        runtime_environment_parameters.max_run_time_in_seconds
        == "mock-max_run_time_in_seconds"
    )
