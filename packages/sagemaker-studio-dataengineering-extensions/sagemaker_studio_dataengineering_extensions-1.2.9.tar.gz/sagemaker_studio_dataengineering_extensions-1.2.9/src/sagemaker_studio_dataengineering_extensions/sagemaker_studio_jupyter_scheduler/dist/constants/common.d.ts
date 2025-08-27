declare const pluginIds: {
    SchedulerPlugin: string;
    TelemetryPlugin: string;
};
declare const featureNames: {
    scheduler: string;
};
declare const i18nStrings: {
    ScheduleNoteBook: {
        MainPanel: {
            AdvancedOptions: {
                options: string;
                environmentVariables: string;
                addEnvironmentvariable: string;
                Key: string;
                Value: string;
                RoleArn: string;
                Image: string;
                Kernel: string;
                securityGroup: string;
                subnet: string;
                s3InputFolder: string;
                inputInDifferentAccount: string;
                inputInDifferentAccountLabel: string;
                s3OutputFolder: string;
                outputInDifferentAccount: string;
                outputInDifferentAccountLabel: string;
                maxRetryAttempts: string;
                maxRunTimeInSeconds: string;
                selectAdditionalDepency: string;
                efsPlaceholder: string;
                efsLabel: string;
                startUpScript: string;
                executionEnv: string;
                useVPC: string;
                enableNetworkIsolation: string;
                enableEncryption: string;
                enterKMSArnOrID: string;
                ebsKey: string;
                kmsKey: string;
                Placeholders: {
                    selectOrAdd: string;
                    No: string;
                    Add: string;
                    NoneSelected: string;
                    SelectPrivateSubnets: string;
                    NoPrivateSubnets: string;
                    ImagePlaceHolder: string;
                    KernelPlaceHolder: string;
                    RolePlaceHolder: string;
                    S3BucketPlaceHolder: string;
                };
            };
            ErrorMessages: {
                JobEnvironment: {
                    KernelImageExistError: string;
                };
                AdvancedOptions: {
                    ImageError: string;
                    KernelError: string;
                    EFSFilePathError: string;
                    RoleArnLengthError: string;
                    RoleArnFormatError: string;
                    S3LengthError: string;
                    S3FormatError: string;
                    SecurityGroupMinError: string;
                    SecurityGroupsMaxError: string;
                    SecurityGroupSGError: string;
                    SecurityGroupLengthError: string;
                    SecurityGroupFormatError: string;
                    SubnetMinError: string;
                    SubnetsMaxError: string;
                    SubnetLengthError: string;
                    SubnetsFormatError: string;
                    EnvironmentVariableEmptyError: string;
                    EnvironmentVariableLengthError: string;
                    EnvironmentVariableFormatError: string;
                    KMSKeyError: string;
                    MaxRetryAttemptsError: string;
                    MaxRunTimeInSecondsError: string;
                };
                VPCErrors: {
                    RequiresPrivateSubnet: string;
                    NoPrivateSubnetsInSageMakerDomain: string;
                    YouMayChooseOtherSubnets: string;
                };
            };
            Tooltips: {
                ImageTooltipText: string;
                KernelTooltipText: string;
                LCCScriptTooltipText: string;
                VPCTooltip: string;
                KMSTooltip: string;
                RoleArnTooltip: string;
                SecurityGroupsTooltip: string;
                SubnetTooltip: string;
                InputFolderTooltip: string;
                OutputFolderTooltip: string;
                InitialScriptTooltip: string;
                EnvironmentVariablesTooltip: string;
                networkIsolationTooltip: string;
                kmsKeyTooltip: string;
                ebsKeyTooltip: string;
                LearnMore: string;
                MaxRetryAttempts: string;
                MaxRunTimeInSeconds: string;
            };
            StudioTooltips: {
                ImageTooltipText: string;
                KernelTooltipText: string;
                RoleArnTooltip: string;
                SecurityGroupsTooltip: string;
                SubnetTooltip: string;
                InputFolderTooltip: string;
                InputAccountIdTooltip: string;
                OutputFolderTooltip: string;
                OutputAccountIdTooltip: string;
                InitialScriptTooltip: string;
            };
        };
    };
    ImageSelector: {
        label: string;
    };
    KernelSelector: {
        label: string;
        imageSelectorOption: {
            linkText: string;
        };
    };
    Dialog: {
        awsCredentialsError: {
            title: string;
            body: {
                text: string[];
                links: {
                    schedulerInformation: {
                        linkString: string;
                        linkHref: string;
                    };
                };
            };
            buttons: {
                goToIamConsole: string;
                enterKeysInTerminal: string;
            };
        };
    };
};
declare const errorCodes: {
    awsCredentials: {
        expiredToken: string;
        invalidClientTokenId: string;
        noCredentials: string;
    };
};
declare const JUPYTER_COMMAND_IDS: {
    terminal: {
        createNew: string;
    };
};
export { pluginIds, i18nStrings, errorCodes, featureNames, JUPYTER_COMMAND_IDS };
//# sourceMappingURL=common.d.ts.map