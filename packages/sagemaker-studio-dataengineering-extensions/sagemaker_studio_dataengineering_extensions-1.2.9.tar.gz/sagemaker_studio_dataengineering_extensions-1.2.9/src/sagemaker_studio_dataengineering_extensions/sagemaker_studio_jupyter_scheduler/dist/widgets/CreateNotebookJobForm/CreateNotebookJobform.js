import React, { useState, useEffect, useMemo } from 'react';
import { JobsView } from '@jupyterlab/scheduler';
import { AppNetworkAccessType } from '../../types';
import AdvancedOptions from './AdvancedOptions/AdvancedOptions';
import { getAdditionalOptionsContainerStyles } from './styles';
import { getInitialEnvironmentVariables, getInitialInitScriptValue, getInitialLCCValue, getInitialRoleArnValues, getInitialS3Values, getInitialSubnetOrSecurityGroupValues, getNetworkAccessType, getInitialKMSKeys, getAdvancedOptionsFromSettingRegistry, NO_SCRIPT, getInitialKeyValue, getInitialKeyValueAsBoolean, } from './initialValueHelpers';
import * as validationHelpers from './AdvancedOptions/validationHelpers';
import { JobEnvironmentContainer } from './JobEnvironment/JobEnvironmentContainer';
const CreateNotebookJobForm = (props) => {
    const { executionEnvironments, settingRegistry, jobsView, requestClient, errors: formErrors, handleErrorsChange: setFormErrors, model, handleModelChange, } = props;
    const networkAccessType = useMemo(() => {
        return getNetworkAccessType(executionEnvironments === null || executionEnvironments === void 0 ? void 0 : executionEnvironments.auto_detected_config, jobsView);
    }, []);
    const areFieldsDisabled = jobsView === JobsView.JobDefinitionDetail || jobsView === JobsView.JobDetail;
    const initialLccValues = useMemo(() => {
        var _a, _b;
        const ALL_LCC_OPTIONS = [];
        const PRE_DEFINED_LCC_OPTIONS = ((_b = (_a = executionEnvironments.auto_detected_config) === null || _a === void 0 ? void 0 : _a.find(c => c.name === 'lcc_arn')) === null || _b === void 0 ? void 0 : _b.value) || [];
        ALL_LCC_OPTIONS.push(NO_SCRIPT);
        ALL_LCC_OPTIONS.push(...PRE_DEFINED_LCC_OPTIONS);
        const selectedLccValue = getInitialLCCValue(model.runtimeEnvironmentParameters, jobsView);
        if (model.runtimeEnvironmentParameters && selectedLccValue !== NO_SCRIPT) {
            ALL_LCC_OPTIONS.push(selectedLccValue);
        }
        return {
            allLCCOptions: ALL_LCC_OPTIONS,
            selectedLccValue
        };
    }, []);
    const initialRoleArnValue = useMemo(() => {
        return getInitialRoleArnValues(model.runtimeEnvironmentParameters, executionEnvironments.auto_detected_config, jobsView);
    }, []);
    const initialS3OutputValue = useMemo(() => {
        return getInitialS3Values(model.runtimeEnvironmentParameters, executionEnvironments.auto_detected_config, jobsView, 's3_output');
    }, []);
    const initialS3InputValue = useMemo(() => {
        return getInitialS3Values(model.runtimeEnvironmentParameters, executionEnvironments.auto_detected_config, jobsView, 's3_input');
    }, []);
    const initialMaxRetryAttemtpsValue = useMemo(() => {
        return getInitialKeyValue(model.runtimeEnvironmentParameters, jobsView, 1, 'max_retry_attempts');
    }, []);
    // get initial value from runtime environment
    const initialNetworkIsolationValue = useMemo(() => {
        return getInitialKeyValueAsBoolean(model.runtimeEnvironmentParameters, jobsView, 'enable_network_isolation');
    }, []);
    const initialMaxRunTimeInSecondsValue = useMemo(() => {
        return getInitialKeyValue(model.runtimeEnvironmentParameters, jobsView, 172800, 'max_run_time_in_seconds');
    }, []);
    const securityGroupOptions = useMemo(() => {
        var _a, _b;
        const ALL_SECURITY_GROUPS = ((_b = (_a = executionEnvironments.auto_detected_config) === null || _a === void 0 ? void 0 : _a.find((c) => c.name === 'vpc_security_group_ids')) === null || _b === void 0 ? void 0 : _b.value) || [];
        return ALL_SECURITY_GROUPS === null || ALL_SECURITY_GROUPS === void 0 ? void 0 : ALL_SECURITY_GROUPS.map((item) => item.name);
    }, []);
    const subnetOptions = useMemo(() => {
        var _a, _b;
        const ALL_SUBNETS = ((_b = (_a = executionEnvironments.auto_detected_config) === null || _a === void 0 ? void 0 : _a.find((c) => c.name === 'vpc_subnets')) === null || _b === void 0 ? void 0 : _b.value) || [];
        return ALL_SUBNETS === null || ALL_SUBNETS === void 0 ? void 0 : ALL_SUBNETS.map((item) => item.name);
    }, []);
    const initialSecurityGroupAndSubnetValues = useMemo(() => {
        if (networkAccessType === AppNetworkAccessType.PublicInternetOnly) {
            return {
                securityGroups: [],
                subnets: [],
            };
        }
        // if no private subnets then users can't create a job with a VPC, so switch to empty list for security groups
        const securityGroups = subnetOptions.length === 0 && jobsView === JobsView.CreateForm
            ? []
            : getInitialSubnetOrSecurityGroupValues(model.runtimeEnvironmentParameters, executionEnvironments.auto_detected_config, jobsView, 'vpc_security_group_ids');
        const subnets = getInitialSubnetOrSecurityGroupValues(model.runtimeEnvironmentParameters, executionEnvironments.auto_detected_config, jobsView, 'vpc_subnets');
        return { securityGroups, subnets };
    }, []);
    const initialInitScriptValue = useMemo(() => {
        return getInitialInitScriptValue(model.runtimeEnvironmentParameters, jobsView);
    }, []);
    const initialEnvironmentVariables = useMemo(() => {
        return getInitialEnvironmentVariables(model.runtimeEnvironmentParameters);
    }, []);
    const initialOutputKMSKey = useMemo(() => {
        return getInitialKMSKeys(model.runtimeEnvironmentParameters, jobsView, 'sm_output_kms_key');
    }, []);
    const initialVolumeKMSKey = useMemo(() => {
        return getInitialKMSKeys(model.runtimeEnvironmentParameters, jobsView, 'sm_volume_kms_key');
    }, []);
    const initialCheckedState = useMemo(() => {
        return false;
    }, []);
    // user default values object is the combination of the auto detected configs and the user default advanced options
    const [userDefaultValues, setUserDefaultValues] = useState({
        sm_lcc_init_script_arn: initialLccValues.selectedLccValue || '',
        role_arn: initialRoleArnValue || '',
        vpc_security_group_ids: initialSecurityGroupAndSubnetValues.securityGroups || [],
        vpc_subnets: initialSecurityGroupAndSubnetValues.subnets || [],
        s3_input: initialS3InputValue || '',
        s3_input_account_id: '',
        s3_output: initialS3OutputValue || '',
        s3_output_account_id: '',
        sm_kernel: '',
        sm_image: '',
        sm_init_script: initialInitScriptValue || '',
        sm_output_kms_key: initialOutputKMSKey || '',
        sm_volume_kms_key: initialVolumeKMSKey || '',
        max_retry_attempts: initialMaxRetryAttemtpsValue,
        max_run_time_in_seconds: initialMaxRunTimeInSecondsValue,
        enable_network_isolation: initialNetworkIsolationValue,
    });
    // initially output and volume kms keys should be empty even if we have the initial values coming from the user defaults,
    // because initially the kms encryption is disabled. When the kms encryption gets enabled the user default values will get picked up.
    const [formState, setFormState] = useState({
        ...userDefaultValues,
        sm_output_kms_key: '',
        sm_volume_kms_key: '',
    });
    // validate initial form values to be safe
    useEffect(() => {
        const initialSubnetOptionsError = validationHelpers.validateSubnetOptions(subnetOptions);
        const initialNoCompatibleSubnetsError = validationHelpers.validateInitialSubnets(initialSecurityGroupAndSubnetValues.subnets);
        const newFormErrors = {
            ...formErrors,
            roleError: validationHelpers.validateRoleArn(initialRoleArnValue),
            s3InputFolderError: validationHelpers.validateS3Url(initialS3InputValue),
            s3OutputFolderError: validationHelpers.validateS3Url(initialS3OutputValue),
            environmentsStillLoading: '',
            kernelsStillLoading: '',
            subnetError: initialCheckedState ? initialSubnetOptionsError || initialNoCompatibleSubnetsError || '' : '',
        };
        setFormErrors(newFormErrors);
    }, []);
    const [userDefaultAdvancedOptions, setUserDefaultAdvancedOptions] = useState();
    useEffect(() => {
        getAdvancedOptionsFromSettingRegistry(settingRegistry).then((advancedOptions) => {
            setUserDefaultAdvancedOptions(advancedOptions);
        });
    }, []);
    useEffect(() => {
        var _a, _b, _c, _d, _e, _f;
        let newFormState = {};
        let newFormErrors = {};
        let newUserDefaults = {};
        // we want to use the value from user settings always
        const enableNetworkIsolation = (_a = userDefaultAdvancedOptions === null || userDefaultAdvancedOptions === void 0 ? void 0 : userDefaultAdvancedOptions.enable_network_isolation) !== null && _a !== void 0 ? _a : false;
        newFormState = { ...newFormState, enable_network_isolation: enableNetworkIsolation };
        const roleArn = (_b = userDefaultAdvancedOptions === null || userDefaultAdvancedOptions === void 0 ? void 0 : userDefaultAdvancedOptions.role_arn) !== null && _b !== void 0 ? _b : '';
        if (roleArn && roleArn !== initialRoleArnValue) {
            newFormState = { ...newFormState, role_arn: roleArn };
            newFormErrors = {
                ...newFormErrors,
                roleError: validationHelpers.validateRoleArn(roleArn),
            };
        }
        const s3Input = (_c = userDefaultAdvancedOptions === null || userDefaultAdvancedOptions === void 0 ? void 0 : userDefaultAdvancedOptions.s3_input) !== null && _c !== void 0 ? _c : '';
        if (s3Input && s3Input !== initialS3InputValue) {
            newFormState = { ...newFormState, s3_input: s3Input };
            newFormErrors = {
                ...newFormErrors,
                s3InputFolderError: validationHelpers.validateS3Url(s3Input),
            };
        }
        const s3Output = (_d = userDefaultAdvancedOptions === null || userDefaultAdvancedOptions === void 0 ? void 0 : userDefaultAdvancedOptions.s3_output) !== null && _d !== void 0 ? _d : '';
        if (s3Output && s3Output !== initialS3OutputValue) {
            newFormState = { ...newFormState, s3_output: s3Output };
            newFormErrors = {
                ...newFormErrors,
                s3OutputFolderError: validationHelpers.validateS3Url(s3Output),
            };
        }
        const outputKMSKey = (_e = userDefaultAdvancedOptions === null || userDefaultAdvancedOptions === void 0 ? void 0 : userDefaultAdvancedOptions.sm_output_kms_key) !== null && _e !== void 0 ? _e : '';
        if (outputKMSKey && outputKMSKey !== initialOutputKMSKey) {
            // only update the user default values, the kms key value will get picked up
            // from the user default values object whenever the user enables the kms key encryption
            newUserDefaults = { ...newUserDefaults, sm_output_kms_key: outputKMSKey };
        }
        const volumeKMSKey = (_f = userDefaultAdvancedOptions === null || userDefaultAdvancedOptions === void 0 ? void 0 : userDefaultAdvancedOptions.sm_volume_kms_key) !== null && _f !== void 0 ? _f : '';
        if (volumeKMSKey && volumeKMSKey !== initialVolumeKMSKey) {
            // only update the user default values, the kms key value will get picked up
            // from the user default values object whenever the user enables the kms key encryption
            newUserDefaults = { ...newUserDefaults, sm_volume_kms_key: volumeKMSKey };
        }
        newUserDefaults = { ...newFormState, ...newUserDefaults };
        // we don't need the defaults if on the detail page
        if (Object.keys(newFormState).length > 0 && !areFieldsDisabled) {
            setFormState({ ...formState, ...newFormState });
        }
        if (Object.keys(newUserDefaults).length > 0) {
            // update the user default values object which contains the auto detected configs with
            // the values coming from the user default advanced options
            setUserDefaultValues({ ...userDefaultValues, ...newUserDefaults });
        }
        if (Object.keys(newFormErrors).length > 0) {
            setFormErrors({ ...formErrors, ...newFormErrors });
        }
    }, [userDefaultAdvancedOptions]);
    const [environmentVariables, setEnvironmentVariables] = useState(initialEnvironmentVariables);
    const [enableVPCSetting, setEnableVPCSetting] = useState(initialCheckedState);
    const environmentVariablesAsMap = useMemo(() => {
        const map = {};
        environmentVariables === null || environmentVariables === void 0 ? void 0 : environmentVariables.map((environmentVariable) => {
            const { key, value } = environmentVariable;
            // if key and value are empty, do not add to the map
            // TODO: modify this code to handle non string values as well
            if (key.trim().length !== 0 && value.trim().length !== 0) {
                map[key] = value;
            }
        });
        return map;
    }, [environmentVariables]);
    useEffect(() => {
        var _a, _b;
        const commaSeparatedVpcGroupIds = ((_a = formState.vpc_security_group_ids) === null || _a === void 0 ? void 0 : _a.join(',')) || '';
        const commaSeparatedVpcSubnets = ((_b = formState.vpc_subnets) === null || _b === void 0 ? void 0 : _b.join(',')) || '';
        handleModelChange({
            ...model,
            runtimeEnvironmentParameters: {
                ...formState,
                vpc_security_group_ids: commaSeparatedVpcGroupIds,
                vpc_subnets: commaSeparatedVpcSubnets,
                ...environmentVariablesAsMap,
            },
        });
    }, [formState, environmentVariablesAsMap]);
    const handleChange = (e) => {
        const name = e.target.name;
        const value = e.target.value;
        setFormState({ ...formState, [name]: value });
    };
    const handleNumberValueChange = (e) => {
        const name = e.target.name;
        const value = parseInt(e.target.value);
        setFormState({ ...formState, [name]: isNaN(value) ? '' : value });
    };
    const onSelectLCCScript = (startupScript) => {
        setFormState({
            ...formState,
            sm_lcc_init_script_arn: startupScript
        });
    };
    const setSecurityGroups = (securityGroups) => {
        setFormState({
            ...formState,
            vpc_security_group_ids: securityGroups,
        });
    };
    const setRoleArn = (roleArn) => {
        setFormState({ ...formState, role_arn: roleArn });
    };
    const setSubnets = (subnets) => {
        console.log('setSubnets called with:', subnets);
        setFormState({ ...formState, vpc_subnets: subnets });
    };
    return (React.createElement("div", { className: getAdditionalOptionsContainerStyles(areFieldsDisabled) },
        React.createElement(JobEnvironmentContainer, { isDisabled: areFieldsDisabled, formState: formState, setFormState: setFormState, formErrors: formErrors, setFormErrors: setFormErrors, ...props }),
        React.createElement(AdvancedOptions, { isDisabled: areFieldsDisabled, formState: formState, setFormState: setFormState, handleChange: handleChange, handleNumberValueChange: handleNumberValueChange, requestClient: requestClient, formErrors: formErrors, setFormValidationErrors: setFormErrors, environmentVariables: environmentVariables, userDefaultValues: userDefaultValues, setEnvironmentVariables: setEnvironmentVariables, lccOptions: initialLccValues.allLCCOptions, availableSecurityGroups: securityGroupOptions, availableSubnets: subnetOptions, initialSecurityGroups: initialSecurityGroupAndSubnetValues.securityGroups, initialSubnets: initialSecurityGroupAndSubnetValues.subnets, setSubnets: setSubnets, setRoleArn: setRoleArn, setSecurityGroups: setSecurityGroups, onSelectLCCScript: onSelectLCCScript, isVPCDomain: networkAccessType === AppNetworkAccessType.VpcOnly, enableVPCSetting: enableVPCSetting, setEnableVPCSetting: setEnableVPCSetting })));
};
export { CreateNotebookJobForm };
//# sourceMappingURL=CreateNotebookJobform.js.map