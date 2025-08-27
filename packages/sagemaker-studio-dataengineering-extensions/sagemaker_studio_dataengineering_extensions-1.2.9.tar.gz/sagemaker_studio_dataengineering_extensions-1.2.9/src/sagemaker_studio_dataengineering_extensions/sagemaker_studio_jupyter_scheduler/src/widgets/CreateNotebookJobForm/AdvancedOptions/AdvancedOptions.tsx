import React, { SyntheticEvent, useState } from 'react';
import { i18nStrings } from '../../../constants';
import { Scheduler } from '@jupyterlab/scheduler';
import { Checkbox } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import { InputContainer } from '../InputContainer';
import { VpcCheckbox } from './VpcCheckbox/VpcCheckbox';
import { FormState } from '..';
import { EnvironmentVariables, IEnvironmentVariable } from './EnvironmentVariables';
import { MultiSelectContainer } from '../MultiSelectContainer';
import { Link, LinkTarget } from '../../../components/link';
import { Tooltip } from '../../../components/tooltip/Tooltip';
import { ServerConnection } from '@jupyterlab/services';
import { URLExt } from '@jupyterlab/coreutils';

import {
  validateRoleArn,
  validateS3Url,
  validateSecurityGroups,
  validateSubnets,
  validateKMS,
  validateMaxRetryAttempts,
  validateMaxRunTimeInSeconds,
} from './validationHelpers';

import * as Styles from '../../styles';
import { usePluginEnvironment } from '../../../utils/PluginEnvironmentProvider';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import InputLabel from '@mui/material/InputLabel';

const widgetStrings = i18nStrings.ScheduleNoteBook.MainPanel.AdvancedOptions;
const tooltipsStrings = i18nStrings.ScheduleNoteBook.MainPanel.Tooltips;
const studioTooltipsStrings = i18nStrings.ScheduleNoteBook.MainPanel.StudioTooltips;
const errorStrings = i18nStrings.ScheduleNoteBook.MainPanel.ErrorMessages;

const KMSLink = 'https://docs.aws.amazon.com/sagemaker/latest/dg/create-notebook-auto-execution-advanced.html';
const StartupScriptLink = 'https://aws.amazon.com/blogs/machine-learning/customize-amazon-sagemaker-studio-using-lifecycle-configurations/';
const NetworkIsolationLink = 'https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html#sagemaker-CreateTrainingJob-request-EnableNetworkIsolation';

interface AdvancedOptionProps {
  isDisabled: boolean;
  formState: FormState;
  setFormState: (state: FormState) => void;
  formErrors: Scheduler.ErrorsType;
  lccOptions: string[];
  environmentVariables: IEnvironmentVariable[];
  setEnvironmentVariables: (environmentParameters: IEnvironmentVariable[]) => void;
  availableSecurityGroups: string[];
  availableSubnets: string[];
  initialSubnets: string[];
  requestClient: ServerConnection.ISettings;
  initialSecurityGroups: string[];
  userDefaultValues: FormState;
  setSubnets: (subnets: string[]) => void;
  setRoleArn: (roleArn: string) => void;
  setSecurityGroups: (securityGroups: string[]) => void;
  onSelectLCCScript: (event: string) => void;
  handleChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  handleNumberValueChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  setFormValidationErrors: (errors: Scheduler.ErrorsType) => void;
  isVPCDomain: boolean;
  enableVPCSetting: boolean;
  setEnableVPCSetting: (checkBoxState: boolean) => void;
}

const networkIsolationTooltipArea = (
  <div>
    <span className={Styles.TooltipTextContainer}>{tooltipsStrings.networkIsolationTooltip}</span>
    <Link href={NetworkIsolationLink} target={LinkTarget.External}>
      <p className={Styles.TooltipLink}>{tooltipsStrings.LearnMore}</p>
    </Link>
  </div>
);

const kmsTooltipArea = (
  <div>
    <span className={Styles.TooltipTextContainer}>{tooltipsStrings.kmsKeyTooltip}</span>
    <Link href={KMSLink} target={LinkTarget.External}>
      <p className={Styles.TooltipLink}>{tooltipsStrings.LearnMore}</p>
    </Link>
  </div>
);

const startupScriptTooltipContent = (
  <div>
    <span className={Styles.TooltipTextContainer}>{tooltipsStrings.LCCScriptTooltipText}</span>
    <Link href={StartupScriptLink} target={LinkTarget.External}>
      <p className={Styles.TooltipLink}>{tooltipsStrings.LearnMore}</p>
    </Link>
  </div>
);

const AdvancedOptions: React.FunctionComponent<AdvancedOptionProps> = ({
  isDisabled,
  formState,
  formErrors,
  environmentVariables,
  setEnvironmentVariables,
  lccOptions,
  availableSecurityGroups,
  availableSubnets,
  initialSubnets,
  initialSecurityGroups,
  isVPCDomain,
  requestClient,
  enableVPCSetting,
  userDefaultValues,
  setFormState,
  handleChange,
  handleNumberValueChange,
  setSubnets,
  setSecurityGroups,
  onSelectLCCScript,
  setFormValidationErrors,
  setEnableVPCSetting,
  setRoleArn,
}) => {
  const { pluginEnvironment } = usePluginEnvironment();
  const [enableJobEncryption, setEnableJobEncryption] = useState(false);
  const [useCrossAccountInput, setUseCrossAccountInput] = useState(false);
  const [useCrossAccountOutput, setUseCrossAccountOutput] = useState(false);
  const [loading, setLoading] = useState(false);

  const validateVolumeFilePath = async (filePath: string) => {
    const url = URLExt.join(requestClient.baseUrl, '/sagemaker_studio_jupyter_scheduler/validate_volume_path');
    setLoading(true);
    const response = await ServerConnection.makeRequest(
      url,
      { method: 'POST', body: JSON.stringify({ file_path: filePath }) },
      requestClient,
    );
    setLoading(false);

    if (response.status === 200) {
      const responseBody = await response.json();
      if (responseBody.file_path_exist !== true) {
        setFormValidationErrors({
          ...formErrors,
          efsFilePathError: errorStrings.AdvancedOptions.EFSFilePathError,
        });
        return;
      }
    }

    setFormValidationErrors({
      ...formErrors,
      efsFilePathError: '',
    });
  };

  const disableAddEnvironmentVariablesButton = () =>
    isDisabled || environmentVariables.length >= 48 || !!formErrors.environmentVariablesError;

  const validateInitScript = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const filePath = e.target.value;
    const isAllWhiteSpace = filePath.trim().length === 0;

    if (!isAllWhiteSpace) {
      validateVolumeFilePath(filePath);
    } else {
      setFormValidationErrors({
        ...formErrors,
        efsFilePathError: '',
      });
    }
  };

  const handleS3InputFieldOnBlur = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const name = e.target.name;
    const errorMessage = validateS3Url(e.target.value);

    setFormValidationErrors({
      ...formErrors,
      [name === 's3_input' ? 's3InputFolderError' : 's3OutputFolderError']: errorMessage,
    });
  };

  const handleMaxRetryAttemptsFieldOnBlur = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {

    const errorMessage = validateMaxRetryAttempts(e.target.value);

    setFormValidationErrors({
      ...formErrors,
      maxRetryAttemptsError: errorMessage,
    });
  };

  const handleMaxRunTimeInSecondsFieldOnBlur = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {

    const errorMessage = validateMaxRunTimeInSeconds(e.target.value);

    setFormValidationErrors({
      ...formErrors,
      maxRunTimeInSecondsError: errorMessage,
    });
  };

  const handleKMSOnBlur = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const name = e.target.name;
    const errorMessage = validateKMS(e.target.value);
    setFormValidationErrors({
      ...formErrors,
      [name === 'sm_output_kms_key' ? 'outputKMSError' : 'ebsKMSError']: errorMessage,
    });
  };

  const handleRoleArnOnBlur = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { value } = e.target;
    const errorMessage = validateRoleArn(value);
    setRoleArn(value);

    setFormValidationErrors({
      ...formErrors,
      roleError: errorMessage,
    });
  };

  const handleChangeSecurityGroups = (event: SyntheticEvent, values: string[]) => {
    const [errorMessageSecurityGroup, errorMessageSubnet] = validateSecurityGroups(values, formState.vpc_subnets);

    setSecurityGroups(values);

    setFormValidationErrors({
      ...formErrors,
      securityGroupError: errorMessageSecurityGroup ?? '',
      subnetError: errorMessageSubnet ?? formErrors.subnetError,
    });
  };

  const handleChangeSubnets = (event: SyntheticEvent, values: string[]) => {
    const [errorMessageSubnet, errorMessageSecurityGroup] = validateSubnets(values, formState.vpc_security_group_ids);

    setSubnets(values);

    setFormValidationErrors({
      ...formErrors,
      securityGroupError: errorMessageSecurityGroup ?? formErrors.securityGroupError,
      subnetError: errorMessageSubnet ?? '',
    });
  };

  // for sagemaker unified studio TODO: find a way to detect if it's SMUS
  const isSMUS = true;

  return (
    <div className={Styles.WidgetFieldsContainer}>
      {!isSMUS && (
        <InputContainer
          aria-label={'role_arn'}
          name={'role_arn'}
          disabled={loading}
          readOnly={isDisabled}
          required
          labelInfo={widgetStrings.RoleArn}
          errorMessage={formErrors.roleError}
          placeholder={widgetStrings.Placeholders.RolePlaceHolder}
          onChange={handleChange}
          value={formState.role_arn}
          onBlur={handleRoleArnOnBlur}
          toolTipText={pluginEnvironment.isStudioOrJupyterLab ? studioTooltipsStrings.RoleArnTooltip : tooltipsStrings.RoleArnTooltip}
        />
      )}

      {!isSMUS && (
        <InputContainer
          name={'s3_input'}
          onChange={handleChange}
          required
          disabled={loading}
          readOnly={isDisabled}
          value={formState.s3_input}
          placeholder={widgetStrings.Placeholders.S3BucketPlaceHolder}
          labelInfo={widgetStrings.s3InputFolder}
          errorMessage={formErrors.s3InputFolderError}
          onBlur={handleS3InputFieldOnBlur}
          toolTipText={pluginEnvironment.isStudioOrJupyterLab ? studioTooltipsStrings.InputFolderTooltip : tooltipsStrings.InputFolderTooltip}
        />
      )}
      {!isDisabled && !isSMUS && (
        <div className={Styles.TooltipCheckBoxContainer}>
          <Checkbox
            data-testid={'input_cross_account_id'}
            name={'input_cross_account_id'}
            className={Styles.Checkbox}
            color={'primary'}
            checked={useCrossAccountInput}
            onChange={(e) => {
              const checkedState = e.target.checked;
              setUseCrossAccountInput(checkedState);
              
              // every time the box is set, account Id resets
              !isSMUS && setFormState({
                ...formState,
                s3_input_account_id: '',
              });
            }}
          />
          <label>{widgetStrings.inputInDifferentAccount}</label>
        </div>
      )}

      {(isDisabled || useCrossAccountInput) && !isSMUS && (
        <>
          <InputContainer
            name={'s3_input_account_id'}
            onChange={handleChange}
            required={false}
            readOnly={isDisabled}
            disabled={loading}
            value={formState.s3_input_account_id}
            labelInfo={widgetStrings.inputInDifferentAccountLabel}
            onBlur={(event) => {
              setFormState({
                ...formState,
                s3_input_account_id: event.target.value,
              });
            }}
          />
        </>
      )}

      {!isSMUS && (
        <InputContainer
          name={'s3_output'}
          onChange={handleChange}
          required
          disabled={loading}
          readOnly={isDisabled}
          value={formState.s3_output}
          placeholder={widgetStrings.Placeholders.S3BucketPlaceHolder}
          labelInfo={widgetStrings.s3OutputFolder}
          errorMessage={formErrors.s3OutputFolderError}
          onBlur={handleS3InputFieldOnBlur}
          toolTipText={pluginEnvironment.isStudioOrJupyterLab ? studioTooltipsStrings.OutputFolderTooltip : tooltipsStrings.OutputFolderTooltip}
        />
      )}

      {!isDisabled && !isSMUS && (
        <div className={Styles.TooltipCheckBoxContainer}>
          <Checkbox
            data-testid={'output_cross_account_id'}
            name={'output_cross_account_id'}
            className={Styles.Checkbox}
            color={'primary'}
            checked={useCrossAccountOutput}
            onChange={(e) => {
              const checkedState = e.target.checked;
              setUseCrossAccountOutput(checkedState);
              
              // every time the box is set, account Id resets
              !isSMUS && setFormState({
                ...formState,
                s3_output_account_id: '',
              });
            }}
          />
          <label>{widgetStrings.outputInDifferentAccount}</label>
        </div>
      )}

      {(isDisabled || useCrossAccountOutput) && !isSMUS && (
        <>
          <InputContainer
            name={'s3_output_account_id'}
            onChange={handleChange}
            required={false}
            readOnly={isDisabled}
            disabled={loading}
            value={formState.s3_output_account_id}
            labelInfo={widgetStrings.outputInDifferentAccountLabel}
            onBlur={(event) => {
              setFormState({
                ...formState,
                s3_output_account_id: event.target.value,
              });
            }}
          />
        </>
      )}

      {!isSMUS && (
        <div className={Styles.TooltipCheckBoxContainer}>
          <Checkbox
            data-testid={'enable_network_isolation_checkbox'}
            name={'enable_network_isolation_checkbox'}
            className={Styles.Checkbox}
            color={'primary'}
            disabled={isDisabled}
            checked={formState.enable_network_isolation}
            onChange={(event) => {
              setFormState({
                ...formState,
                enable_network_isolation: event.target.checked
              });
            }}
          />
          <label>{widgetStrings.enableNetworkIsolation}</label>
          <Tooltip
            classes={{
              popperInteractive: Styles.PopperInteractive,
            }}
            title={networkIsolationTooltipArea}
          >
            <InfoIcon fontSize="small" />
          </Tooltip>
        </div>
      )}

      {!isDisabled && !isSMUS && (
        <div className={Styles.TooltipCheckBoxContainer}>
          <Checkbox
            data-testid={'kms_checkbox'}
            name={'kms_checkbox'}
            className={Styles.Checkbox}
            color={'primary'}
            checked={enableJobEncryption}
            onChange={(e) => {
              const checkedState = e.target.checked;
              setEnableJobEncryption(checkedState);
              // when checkbox gets checked, the user wants to enable the kms encryption, so
              // we should pick the kms key from the user default values object and check it for validity.
              // if they disable the kms encryption we should clear out the kms key and the respective form errors.
              const outputKMSKey = checkedState ? userDefaultValues.sm_output_kms_key : '';
              const volumeKMSKey = checkedState ? userDefaultValues.sm_volume_kms_key : '';
              setFormState({
                ...formState,
                sm_output_kms_key: outputKMSKey,
                sm_volume_kms_key: volumeKMSKey,
              });
              setFormValidationErrors({
                ...formErrors,
                outputKMSError: validateKMS(outputKMSKey),
                ebsKMSError: validateKMS(volumeKMSKey),
              });
            }}
          />
          <label>{widgetStrings.enableEncryption}</label>
          <Tooltip
            classes={{
              popperInteractive: Styles.PopperInteractive,
            }}
            title={kmsTooltipArea}
          >
            <InfoIcon fontSize="small" />
          </Tooltip>
        </div>
      )}

      {(isDisabled || enableJobEncryption) && !isSMUS && (
        <>
          <InputContainer
            name={'sm_output_kms_key'}
            onChange={handleChange}
            required={false}
            readOnly={isDisabled}
            disabled={loading}
            value={formState.sm_output_kms_key}
            placeholder={isDisabled ? widgetStrings.Placeholders.NoneSelected : widgetStrings.enterKMSArnOrID}
            labelInfo={widgetStrings.kmsKey}
            errorMessage={formErrors.outputKMSError}
            onBlur={handleKMSOnBlur}
            toolTipText={!isDisabled ? tooltipsStrings.kmsKeyTooltip : undefined}
          />
          <InputContainer
            name={'sm_volume_kms_key'}
            onChange={handleChange}
            required={false}
            readOnly={isDisabled}
            disabled={loading}
            value={formState.sm_volume_kms_key}
            placeholder={isDisabled ? widgetStrings.Placeholders.NoneSelected : widgetStrings.enterKMSArnOrID}
            labelInfo={widgetStrings.ebsKey}
            errorMessage={formErrors.ebsKMSError}
            onBlur={handleKMSOnBlur}
            toolTipText={!isDisabled ? tooltipsStrings.ebsKeyTooltip : undefined}
          />
        </>
      )}

      {isVPCDomain && !isDisabled && !isSMUS && (
        <VpcCheckbox
          isChecked={enableVPCSetting}
          setChecked={setEnableVPCSetting}
          initialSecurityGroups={initialSecurityGroups}
          initialSubnets={initialSubnets}
          availableSubnets={availableSubnets}
          formState={formState}
          formErrors={formErrors}
          setFormErrors={setFormValidationErrors}
          setFormState={setFormState}
          data-testid={'vpc-checkbox'}
        />
      )}

      {((isVPCDomain && enableVPCSetting) || isDisabled) && !isSMUS && (
        <>
          <MultiSelectContainer
            required
            name={'vpc_subnets'}
            disabled={isDisabled || (pluginEnvironment.isStudioOrJupyterLab && availableSubnets.length === 0)}
            label={widgetStrings.subnet}
            options={availableSubnets}
            value={formState.vpc_subnets}
            onChange={handleChangeSubnets}
            errorMessage={formErrors.subnetError}
            placeholder={`${widgetStrings.Placeholders.SelectPrivateSubnets}`}
            tooltip={pluginEnvironment.isStudio ? studioTooltipsStrings.SubnetTooltip : tooltipsStrings.SubnetTooltip}
            disabledTooltip={`${widgetStrings.Placeholders.NoPrivateSubnets}`}
            freeSolo
          />

          <MultiSelectContainer
            required
            className={'securityGroupSelector'}
            name={'vpc_security_group_ids'}
            disabled={isDisabled || (pluginEnvironment.isStudioOrJupyterLab && availableSecurityGroups.length === 0)}
            label={widgetStrings.securityGroup}
            options={availableSecurityGroups}
            value={formState.vpc_security_group_ids}
            onChange={handleChangeSecurityGroups}
            errorMessage={formErrors.securityGroupError}
            placeholder={`${widgetStrings.Placeholders.selectOrAdd} ${widgetStrings.securityGroup}`}
            tooltip={pluginEnvironment.isStudio ? studioTooltipsStrings.SecurityGroupsTooltip : tooltipsStrings.SecurityGroupsTooltip}
            disabledTooltip={`${widgetStrings.Placeholders.No} ${widgetStrings.securityGroup}`}
            freeSolo
          />
        </>
      )}

      {pluginEnvironment.isStudioOrJupyterLab && !isSMUS &&
        <div className={Styles.AdvancedOptionsSelectContainer}>
        <InputLabel id="startup-script-select-label">
          {widgetStrings.startUpScript}
          <Tooltip
            title={startupScriptTooltipContent}
          >
            <InfoIcon fontSize="small" />
          </Tooltip>
        </InputLabel>
        <Select
          labelId="startup-script-select-label"
          id="startup-script-select"
          disabled={loading}
          readOnly={isDisabled}
          value={formState.sm_lcc_init_script_arn}
          onChange={(event) => onSelectLCCScript(event.target.value)}
        >
          {lccOptions && lccOptions.map((lccOption) => (
            <MenuItem key={lccOption} value={lccOption}>{lccOption}</MenuItem>
          ))}
        </Select>
      </div>}

      <EnvironmentVariables
        isButtonDisabled={disableAddEnvironmentVariablesButton()}
        allFieldsDisabled={isDisabled}
        environmentVariables={environmentVariables}
        setEnvironmentVariables={setEnvironmentVariables}
        formErrors={formErrors}
        setFormErrors={setFormValidationErrors}
      />

      {!isSMUS && (
        <div>
          <InputContainer
            placeholder={isDisabled ? widgetStrings.Placeholders.NoneSelected : widgetStrings.efsPlaceholder}
            labelInfo={widgetStrings.efsLabel}
            required={false}
            value={formState.sm_init_script}
            name={'sm_init_script'}
            readOnly={isDisabled}
            disabled={loading}
            errorMessage={formErrors.efsFilePathError}
            onChange={handleChange}
            onBlur={validateInitScript}
            toolTipText={!isDisabled ? (pluginEnvironment.isStudio ? studioTooltipsStrings.InitialScriptTooltip : tooltipsStrings.InitialScriptTooltip) : undefined}
          />
          {/* {loading && <ActivityIndicator />} */}
        </div>
      )}

      <InputContainer
        name={'max_retry_attempts'}
        type="number"
        onChange={handleNumberValueChange}
        required
        disabled={loading}
        readOnly={isDisabled}
        value={formState.max_retry_attempts}
        placeholder={widgetStrings.maxRetryAttempts}
        labelInfo={widgetStrings.maxRetryAttempts}
        errorMessage={formErrors.maxRetryAttemptsError}
        onBlur={handleMaxRetryAttemptsFieldOnBlur}
        toolTipText={tooltipsStrings.MaxRetryAttempts}
      />

      <InputContainer
        name={'max_run_time_in_seconds'}
        type="number"
        onChange={handleNumberValueChange}
        required
        disabled={loading}
        readOnly={isDisabled}
        value={formState.max_run_time_in_seconds}
        placeholder={widgetStrings.maxRunTimeInSeconds}
        labelInfo={widgetStrings.maxRunTimeInSeconds}
        errorMessage={formErrors.maxRunTimeInSecondsError}
        onBlur={handleMaxRunTimeInSecondsFieldOnBlur}
        toolTipText={tooltipsStrings.MaxRunTimeInSeconds}
      />

    </div>
  );
};

export default AdvancedOptions;
