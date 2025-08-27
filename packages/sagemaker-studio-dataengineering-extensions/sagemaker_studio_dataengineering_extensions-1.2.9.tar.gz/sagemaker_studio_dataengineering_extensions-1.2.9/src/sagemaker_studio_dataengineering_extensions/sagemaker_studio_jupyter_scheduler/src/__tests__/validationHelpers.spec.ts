import {
  validateInitialSubnets,
  validateKMS,
  validateRoleArn,
  validateS3Url,
  validateSecurityGroups,
  validateSubnetOptions,
  validateSubnets
} from '../widgets/CreateNotebookJobForm/AdvancedOptions/validationHelpers';
import { i18nStrings } from '../constants';

const errorStrings = i18nStrings.ScheduleNoteBook.MainPanel.ErrorMessages;
const vpcErrorStrings = errorStrings.VPCErrors;

const createSubnetItem = (subnetName: string): string => {
  return subnetName;
};

const createSecurityGroupItem = (securityGroupName: string): string => {
  return securityGroupName;
}

describe('role arn tests', () => {
  it('returns length error when arn is too short', () => {
    const roleArn = 'erwqer';

    const result = validateRoleArn(roleArn);
    expect(result).toEqual(errorStrings.AdvancedOptions.RoleArnLengthError);
  });

  it('returns length error when arn is too long', () => {
    const roleArn = `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`;
    const result = validateRoleArn(roleArn)
    expect(result).toEqual(errorStrings.AdvancedOptions.RoleArnLengthError);
  });

  it('returns format error when role arn is is not correctly formatted', () => {
    const roleArn = `arn:aws:iam::748478975813/service-role/AmazonSageMaker-ExecutionRole-20220409T160852`;
    const result = validateRoleArn(roleArn);
    expect(result).toEqual(errorStrings.AdvancedOptions.RoleArnFormatError);
  });

  it('returns nothing when ARN is properly formatted', () => {
    const roleArn =
      'arn:aws:iam::748478975813:role/service-role/AmazonSageMaker-ExecutionRole-20220409T160852';
    const result = validateRoleArn(roleArn);
    expect(result).toEqual('');
  });
});

describe('S3 URL validation tests', () => {
  it('returns length error when string is empty', () => {
    let s3Url = '';
    expect(validateS3Url(s3Url)).toBe(errorStrings.AdvancedOptions.S3LengthError);

    s3Url = '    ';
    expect(validateS3Url(s3Url)).toBe(errorStrings.AdvancedOptions.S3LengthError);
  });

  it('returns format error when s3 url is not properly formatted', () => {
    const s3Url = 's3:--url-is-bad';
    expect(validateS3Url(s3Url)).toBe(errorStrings.AdvancedOptions.S3FormatError);
  });

  it('returns no error when url is properly formatted', () => {
    const s3Url = 's3://sagemaker-automated-execution-748478975813-us-west-2/';
    expect(validateS3Url(s3Url)).toBe('');
  });
});

describe('subnet list validation tests', () => {
  it('returns error if subnet options list is empty', () => {
    expect(validateSubnetOptions([])).toBe(
      `${vpcErrorStrings.RequiresPrivateSubnet} ${vpcErrorStrings.NoPrivateSubnetsInSageMakerDomain}`
    );
  });

  it('does not return an error if subnets has options', () => {
    const subnetOptions = ['subnet1', 'subnet2'];
    expect(validateSubnetOptions(subnetOptions)).toBe('');
  });

  it('returns no error if there are initial subents', () => {
    const initialSubnets = ['subnet1', 'subnet2'];
    expect(validateInitialSubnets(initialSubnets)).toBe('');
  });

  it('returns error if initial subnets list is empty', () => {
    expect(validateInitialSubnets([])).toBe(`${vpcErrorStrings.RequiresPrivateSubnet} ${vpcErrorStrings.NoPrivateSubnetsInSageMakerDomain}. ${vpcErrorStrings.YouMayChooseOtherSubnets}`);
  });
});

describe('KMS validation tests', () => {
  it('returns an error when KMS key is not properly formatted', () => {
    const KMS_KEY = 'wefwfwefwe';
    expect(validateKMS(KMS_KEY)).toBe(errorStrings.AdvancedOptions.KMSKeyError);
  });

  it('returns no error if KMS key is empty (because it is optional', () => {
    expect(validateKMS('')).toBe('');
  });

  it('returns no error when KMS Key arn is properly formatted', () => {
    const KMS_KEY_ARN =
      'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab';

    expect(validateKMS(KMS_KEY_ARN)).toBe('');

    const KMS_KEY_ID = '1234abcd-12ab-34cd-56ef-1234567890ab';
    expect(validateKMS(KMS_KEY_ID)).toBe('');
  });
});

describe('validate Subnets tests', () => {
  it('returns empty strings when both are empty', () => {
    const subnets: string[] = [];
    const securityGroups: string[] = [];

    expect(validateSubnets(subnets, securityGroups)).toStrictEqual(['', '']);
  });

  it('returns subnet min error when only subnets are empty', () => {
    const subnets: string[] = [];
    const securityGroups = ['sg-1'];

    expect(validateSubnets(subnets, securityGroups)).toStrictEqual([
      errorStrings.AdvancedOptions.SubnetMinError,
      undefined
    ]);
  });

  it('returns subnet length error when there are more than 16 subnets', () => {
    const subnets = [
      createSubnetItem('subnet'),
      createSubnetItem('subnet'),
      createSubnetItem('subnet'),
      createSubnetItem('subnet'),
      createSubnetItem('subnet'),
      createSubnetItem('subnet'),
      createSubnetItem('subnet'),
      createSubnetItem('subnet'),
      createSubnetItem('subnet'),
      createSubnetItem('subnet'),
      createSubnetItem('subnet'),
      createSubnetItem('subnet'),
      createSubnetItem('subnet'),
      createSubnetItem('subnet'),
      createSubnetItem('subnet'),
      createSubnetItem('subnet'),
      createSubnetItem('subnet')
    ];

    const securityGroups: string[] = [];

    expect(validateSubnets(subnets, securityGroups)).toStrictEqual([
      errorStrings.AdvancedOptions.SubnetsMaxError,
      undefined
    ]);
  });

  it('returns subnet length error when subnet is more than 32 characters', () => {
    const subnets = [
      createSubnetItem(
        'testingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtesting'
      )
    ];

    const securityGroups: string[] = [];

    expect(validateSubnets(subnets, securityGroups)).toStrictEqual([
      errorStrings.AdvancedOptions.SubnetLengthError,
      undefined
    ]);
  });

  it('returns subnet format error when subnet is improperly fomatted', () => {
    const subnets = [createSubnetItem('          ')];
    const securityGroups = ['sg-1'];

    const result = validateSubnets(subnets, securityGroups);

    expect(result[0]).toBe(errorStrings.AdvancedOptions.SubnetsFormatError);
    expect(result[1]).toEqual(undefined);
  });

  it('returns an error when there are subnets selected, but no security groups selected', () => {
    const subnets = [createSubnetItem('test-1')];
    const securityGroups: string[] = [];

    const result = validateSubnets(subnets, securityGroups);

    expect(result[0]).toBe('')
    expect(result[1]).toBe(errorStrings.AdvancedOptions.SecurityGroupMinError);
  });
});

describe('validate Security Groups tests', () => {
  it('returns empty strings when both are empty', () => {
    const subnets: string[] = [];
    const securityGroups: string[] = [];

    expect(validateSubnets(subnets, securityGroups)).toStrictEqual(['', '']);
  });

  it('returns sg min error when only subnets are empty', () => {
    const subnets: string[] = ['subnet-1'];
    const securityGroups: string[] = [];

    expect(validateSecurityGroups(securityGroups, subnets)).toStrictEqual([
      errorStrings.AdvancedOptions.SecurityGroupMinError,
      undefined
    ]);
  });

  it('returns sg length error when there are more than 5 sg', () => {
    const securityGroups = [
      createSecurityGroupItem('sg-1'),
      createSecurityGroupItem('sg-1'),
      createSecurityGroupItem('sg-1'),
      createSecurityGroupItem('sg-1'),
      createSecurityGroupItem('sg-1'),
      createSecurityGroupItem('sg-1'),
      createSecurityGroupItem('sg-1')
    ];

    const subnets: string[] = [];

    expect(validateSecurityGroups(securityGroups, subnets)).toStrictEqual([
      errorStrings.AdvancedOptions.SecurityGroupsMaxError,
      undefined
    ]);
  });

  it('returns sg length error when subnet is more than 32 characters', () => {
    const securityGroups = [
      createSecurityGroupItem(
        'sg-testingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtestingtesting'
      )
    ];

    const subnets: string[] = [];

    expect(validateSecurityGroups(securityGroups, subnets)).toStrictEqual([
      errorStrings.AdvancedOptions.SecurityGroupLengthError,
      undefined
    ]);
  });

  it('returns sg format error when `sg-` is not the starting of the string', () => {
    const securityGroups = [createSecurityGroupItem('rwerwqrq')];
    const subnets = ['subnet-1'];

    const result = validateSecurityGroups(securityGroups, subnets);

    expect(result[0]).toBe(errorStrings.AdvancedOptions.SecurityGroupSGError);
    expect(result[1]).toEqual(undefined);
  });

  it('returns an error when there are sg selected, but no subnets selected', () => {
    const securityGroups = [createSecurityGroupItem('sg-1')];
    const subnets: string[] = [];

    const result = validateSecurityGroups(securityGroups, subnets);

    expect(result[0]).toBe('');
    expect(result[1]).toBe(errorStrings.AdvancedOptions.SubnetMinError);
  });
});
