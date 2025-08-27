import { i18nStrings } from '../../../constants/common';

const s3PathPattern = new RegExp('^(https|s3)://([^/]+)/?(.*)$');
const securityGroupAndSubnetPattern = new RegExp('[-0-9a-zA-Z]+');
const roleArnPattern = new RegExp('^arn:aws[a-z\\-]*:iam::\\d{12}:role/?[a-zA-Z_0-9+=,.@\\-_/]+$');
const keyArnPattern = new RegExp('^arn:aws:kms:\\w+(?:-\\w+)+:\\d{12}:key\\/[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+$');
const keyIDPattern = new RegExp('^[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}$');

const errorStrings = i18nStrings.ScheduleNoteBook.MainPanel.ErrorMessages;
const vpcErrorStrings = errorStrings.VPCErrors;
const maxRetryAttemptsMinValue = 0;
const maxRetryAttemptsMaxValue = 30;
const maxRunTimeMinValue = 0;

export const validateImage = (image: string): string => {
  return image.length <= 0 ? errorStrings.AdvancedOptions.ImageError : '';
}

export const validateKernel = (kernel: string): string => {
  return kernel.length <= 0 ? errorStrings.AdvancedOptions.KernelError : '';
}

export const validateRoleArn = (roleArn: string): string => {
  if (roleArn.length < 20 || roleArn.length > 2048) {
    return errorStrings.AdvancedOptions.RoleArnLengthError;
  }

  if (!roleArnPattern.test(roleArn)) {
    return errorStrings.AdvancedOptions.RoleArnFormatError;
  }

  return '';
};

// Reference: https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_DebugRuleConfiguration.html#sagemaker-Type-DebugRuleConfiguration-S3OutputPath
export const validateS3Url = (s3Path: string): string => {
  if (s3Path.trim().length === 0) {
    return errorStrings.AdvancedOptions.S3LengthError;
  }

  if (!s3PathPattern.test(s3Path)) {
    return errorStrings.AdvancedOptions.S3FormatError;
  }

  return '';
};

export const validateMaxRetryAttempts = (maxRetryAttemptsString: string): string => {
  const maxRetryAttempts = parseInt(maxRetryAttemptsString)
  if (isNaN(maxRetryAttempts) || maxRetryAttempts < maxRetryAttemptsMinValue || maxRetryAttempts > maxRetryAttemptsMaxValue){
    return errorStrings.AdvancedOptions.MaxRetryAttemptsError;
  }
  return '';
};

export const validateMaxRunTimeInSeconds = (maxRuntTimeInSecondsString: string): string => {
  const maxRuntTimeInSeconds = parseInt(maxRuntTimeInSecondsString)
  if (isNaN(maxRuntTimeInSeconds) || maxRuntTimeInSeconds < maxRunTimeMinValue){
    return errorStrings.AdvancedOptions.MaxRunTimeInSecondsError;
  }
  return '';
};

export const validateSubnetOptions = (subnetOptions: string[]): string => {
  if (subnetOptions) {
    if (subnetOptions.length === 0) {
      return `${vpcErrorStrings.RequiresPrivateSubnet} ${vpcErrorStrings.NoPrivateSubnetsInSageMakerDomain}`
    }
  }

  return '';
}

export const validateInitialSubnets = (initialSubnetValues: string[]): string => {
  if (initialSubnetValues) {
    if (initialSubnetValues.length === 0) {
      return `${vpcErrorStrings.RequiresPrivateSubnet} ${vpcErrorStrings.NoPrivateSubnetsInSageMakerDomain}. ${vpcErrorStrings.YouMayChooseOtherSubnets}`;
    }
  }
  return '';
}

// Reference: https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_VpcConfig.html#sagemaker-Type-VpcConfig-SecurityGroupIds
export const validateSecurityGroups = (securityGroups: string[], subnets: string[]): (string | undefined)[] => {
  if (securityGroups.length === 0) {
    if (subnets.length === 0) {
      return ['', ''];
    }
    return [errorStrings.AdvancedOptions.SecurityGroupMinError, undefined];
  }

  if (securityGroups.length > 0) {
    if (securityGroups.length > 5) {
      return [errorStrings.AdvancedOptions.SecurityGroupsMaxError, undefined];
    }

    for (const securityGroup of securityGroups) {
      if (!securityGroup.startsWith('sg-')) {
        return [errorStrings.AdvancedOptions.SecurityGroupSGError, undefined];
      }

      if (securityGroup.length > 32) {
        return [errorStrings.AdvancedOptions.SecurityGroupLengthError, undefined];
      }

      if (!securityGroupAndSubnetPattern.test(securityGroup)) {
        return [errorStrings.AdvancedOptions.SecurityGroupFormatError, undefined];
      }
    }

    if (subnets.length === 0) {
      return ['', errorStrings.AdvancedOptions.SubnetMinError];
    }
  }
  return ['', undefined];
};

// Reference: https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_VpcConfig.html#sagemaker-Type-VpcConfig-Subnets
export const validateSubnets = (subnets: string[], securityGroups: string[]): (string | undefined)[] => {
  if (subnets.length === 0) {
    if (securityGroups.length === 0) {
      return ['', ''];
    }
    return [errorStrings.AdvancedOptions.SubnetMinError, undefined];
  }

  if (subnets && subnets.length > 0) {
    if (subnets.length > 16) {
      return [errorStrings.AdvancedOptions.SubnetsMaxError, undefined];
    }

    for (const subnet of subnets) {
      if (subnet.length > 32) {
        return [errorStrings.AdvancedOptions.SubnetLengthError, undefined];
      }

      if (!securityGroupAndSubnetPattern.test(subnet)) {
        return [errorStrings.AdvancedOptions.SubnetsFormatError, undefined];
      }
    }

    if (securityGroups.length === 0) {
      return ['', errorStrings.AdvancedOptions.SecurityGroupMinError];
    }
  }
  return ['', undefined];
};

//Reference: https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_OutputDataConfig.html#sagemaker-Type-OutputDataConfig-KmsKeyId
export const validateKMS = (KMS: string): string => {
  if (KMS.length === 0) {
    return '';
  }
  if (!keyArnPattern.test(KMS) && !keyIDPattern.test(KMS)) {
    return errorStrings.AdvancedOptions.KMSKeyError;
  }
  return '';
};
