const pluginIds = {
    SchedulerPlugin: '@amzn/sagemaker-studio-scheduler:scheduler',
    TelemetryPlugin: '@amzn/sagemaker-studio-scheduler:schedulerTelemetry'
};
const featureNames = {
    scheduler: 'nbScheduler',
};
const i18nStrings = {
    ScheduleNoteBook: {
        MainPanel: {
            AdvancedOptions: {
                options: 'Advanced Options',
                environmentVariables: 'Environment variables',
                addEnvironmentvariable: 'Add Variable',
                Key: 'Key',
                Value: 'Value',
                RoleArn: 'Role ARN',
                Image: 'Image',
                Kernel: 'Kernel',
                securityGroup: 'Security Group(s)',
                subnet: 'Subnet(s)',
                s3InputFolder: 'Input Folder',
                inputInDifferentAccount: 'Input bucket is not in current account',
                inputInDifferentAccountLabel: "Enter input account ID",
                s3OutputFolder: 'Output Folder',
                outputInDifferentAccount: 'Output bucket is not in current account',
                outputInDifferentAccountLabel: "Enter output account ID",
                maxRetryAttempts: 'Max retry attempts',
                maxRunTimeInSeconds: 'Max run time (in seconds)',
                selectAdditionalDepency: 'Select additional dependencies',
                efsPlaceholder: 'Enter EFS file path',
                efsLabel: 'Initialization script location (optional)',
                startUpScript: 'Start-up script',
                executionEnv: 'Execution enviroment',
                useVPC: 'Use a Virtual Private Cloud (VPC) to run this job',
                enableNetworkIsolation: 'Enable Network Isolation',
                enableEncryption: 'Configure job encryption',
                enterKMSArnOrID: 'Enter KMS key ID or ARN',
                ebsKey: 'Job instance volume encryption KMS key',
                kmsKey: 'Output encryption KMS key',
                Placeholders: {
                    selectOrAdd: 'select or add',
                    No: 'No',
                    Add: 'Add',
                    NoneSelected: 'None selected',
                    SelectPrivateSubnets: 'Select private subnet(s)',
                    NoPrivateSubnets: 'No private subnet(s) available',
                    ImagePlaceHolder: `accountId.dkr.ecr.Region.amazonaws.com/repository[:tag] or [@digest]`,
                    KernelPlaceHolder: `kernel name`,
                    RolePlaceHolder: `arn:aws:iam::YourAccountID:role/YourRole`,
                    S3BucketPlaceHolder: `s3://bucket/path-to-your-data/`
                },
            },
            ErrorMessages: {
                JobEnvironment: {
                    KernelImageExistError: 'Image must be selected',
                },
                AdvancedOptions: {
                    ImageError: 'Image cannot be empty.',
                    KernelError: 'Kernel cannot be empty.',
                    EFSFilePathError: 'File path is not valid.',
                    RoleArnLengthError: 'Role ARN must have minimum length of 20 and maximum length of 2048.',
                    RoleArnFormatError: 'Role ARN is not properly formatted.',
                    S3LengthError: 'S3 Path must contain characters.',
                    S3FormatError: 'Invalid S3 Path format.',
                    SecurityGroupMinError: 'At least one Security Group must be selected when Subnet is selected.',
                    SecurityGroupsMaxError: 'Can only have a maximum of 5 Security Groups.',
                    SecurityGroupSGError: 'Security Group must start with sg-.',
                    SecurityGroupLengthError: 'Security Group must be less than 32 characters.',
                    SecurityGroupFormatError: 'Security Group has invalid format.',
                    SubnetMinError: 'At least one Subnet must be selected when Security Group is selected.',
                    SubnetsMaxError: 'Can only have maximum of 16 subnets.',
                    SubnetLengthError: 'Subnet must be less than 32 characters.',
                    SubnetsFormatError: 'One or more subnets has invalid format.',
                    EnvironmentVariableEmptyError: 'Key or Value cannot be empty.',
                    EnvironmentVariableLengthError: 'Key or Value cannot be more than 512 characters.',
                    EnvironmentVariableFormatError: 'Key or Value has invalid format.',
                    KMSKeyError: 'KMS key has invalid format.',
                    MaxRetryAttemptsError: 'Invalid max retry attempts must have a minimum value of 1 and a maximum value of 30.',
                    MaxRunTimeInSecondsError: 'Invalid max run time must have a minimum value of 1.',
                },
                VPCErrors: {
                    RequiresPrivateSubnet: 'Running notebook jobs in a VPC requires the virtual network to use a private subnet.',
                    NoPrivateSubnetsInSageMakerDomain: 'There are no private subnets associated with your SageMaker Studio domain',
                    YouMayChooseOtherSubnets: 'You may choose to run the job using other private subnets associated with this VPC',
                },
            },
            Tooltips: {
                ImageTooltipText: 'Enter the ECR registry path of the Docker image that contains the required Kernel & Libraries to execute the notebook. sagemaker-base-python-38 is selected by default',
                KernelTooltipText: 'Enter the display name of kernel to execute the given notebook. This kernel should be installed in the above image.',
                LCCScriptTooltipText: 'Select a lifecycle configuration script that will be run on image start-up.',
                VPCTooltip: 'Configure the virtual network to run this job in a Virtual Private Cloud (VPC).',
                KMSTooltip: 'Configure the cryptographic keys used to encrypt files in the job.',
                RoleArnTooltip: 'Enter the IAM Role ARN with appropriate permissions needed to execute the notebook. By default Role name with prefix SagemakerJupyterScheduler is selected',
                SecurityGroupsTooltip: 'Specify or add security group(s) of the desired VPC.',
                SubnetTooltip: 'Specify or add Private subnet(s) of the desired VPC.',
                InputFolderTooltip: 'Enter the S3 location to store the input artifacts like notebook and script.',
                OutputFolderTooltip: 'Enter the S3 location to store the output artifacts.',
                InitialScriptTooltip: 'Enter the file path of a local script to run before the notebook execution.',
                EnvironmentVariablesTooltip: 'Enter key-value pairs that will be accessible in your notebook.',
                networkIsolationTooltip: 'Enable network isolation.',
                kmsKeyTooltip: 'If you want Amazon SageMaker to encrypt the output of your notebook job using your own AWS KMS encryption key instead of the default S3 service key, provide its ID or ARN',
                ebsKeyTooltip: 'Encrypt data on the storage volume attached to the compute instance that runs the scheduled job.',
                LearnMore: 'Learn more',
                MaxRetryAttempts: 'Enter a minimum value of 1 and a maximum value of 30.',
                MaxRunTimeInSeconds: 'Enter a minimum value of 1.',
            },
            StudioTooltips: {
                ImageTooltipText: 'Select available SageMaker image.',
                KernelTooltipText: 'Select available SageMaker Kernel.',
                RoleArnTooltip: 'Specify a role with permission to create a notebook job.',
                SecurityGroupsTooltip: 'Specify or add security group(s) that have been created for the default VPC. For better security, we recommend that you use a private VPC.',
                SubnetTooltip: 'Specify or add subnet(s) that have been created for the default VPC. For better security, we recommend that you use a private VPC.',
                InputFolderTooltip: 'Enter the S3 location where the input folder it is located.',
                InputAccountIdTooltip: 'Enter the S3 location where the input folder it is located.',
                OutputFolderTooltip: 'Enter the S3 location where the output folder it is located.',
                OutputAccountIdTooltip: 'Enter the S3 location where the input folder it is located.',
                InitialScriptTooltip: 'Enter the EFS file path where a local script or a lifecycle configuration script is located.',
            },
        },
    },
    ImageSelector: {
        label: 'Image',
    },
    KernelSelector: {
        label: 'Kernel',
        imageSelectorOption: {
            linkText: 'More Info',
        },
    },
    Dialog: {
        awsCredentialsError: {
            title: 'You’re not authenticated to your AWS account.',
            body: {
                text: [
                    'You haven’t provided AWS security keys or they expired. Authenticate to your AWS account with valid security keys before creating a notebook job.',
                    'Note that you must have an AWS account configured with a proper role to create notebook jobs. See %{schedulerInformation} for instructions.',
                ],
                links: {
                    schedulerInformation: {
                        linkString: 'Notebook Scheduler information',
                        linkHref: 'https://docs.aws.amazon.com/sagemaker/latest/dg/notebook-auto-run.html',
                    },
                },
            },
            buttons: {
                goToIamConsole: 'Go to IAM console',
                enterKeysInTerminal: 'Run `aws configure` in Terminal',
            },
        },
    },
};
const errorCodes = {
    awsCredentials: {
        expiredToken: 'ExpiredToken',
        invalidClientTokenId: 'InvalidClientTokenId',
        noCredentials: 'NoCredentials',
    },
};
const JUPYTER_COMMAND_IDS = {
    terminal: {
        createNew: 'terminal:create-new',
    },
};
export { pluginIds, i18nStrings, errorCodes, featureNames, JUPYTER_COMMAND_IDS };
//# sourceMappingURL=common.js.map