import React from 'react';

import { JobsView } from '@jupyterlab/scheduler';
import '@testing-library/jest-dom';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { i18nStrings } from '../constants';
import {
  CreateNotebookJobForm,
  CreateNotebookJobFormProps
} from '../widgets/CreateNotebookJobForm';
import { StudioImagesMapResponseMock } from '../widgets/CreateNotebookJobForm/Studio/studioMock';
import { PluginEnvironmentProvider, STUDIO_SAGEMAKER_UI_PLUGIN_ID } from '../utils/PluginEnvironmentProvider';
import { JupyterFrontEnd } from '@jupyterlab/application';

jest.mock('react', () => ({
  ...jest.requireActual('react'),
  useLayoutEffect: jest.requireActual('react').useEffect,
}));

jest.mock('../widgets/CreateNotebookJobForm/Studio/studioApi', () => {
  const module = jest.requireActual('../widgets/CreateNotebookJobForm/Studio/studioApi');
  return {
    ...module,
    fetchKernelAndImagesForStudio: () => new Promise((resolve) => resolve(StudioImagesMapResponseMock)),
  };
});

jest.mock('../widgets/CreateNotebookJobForm/initialValueHelpers', () => {
  const module = jest.requireActual('../widgets/CreateNotebookJobForm/initialValueHelpers');
  return {
    ...module,
    getAdvancedOptionsFromSettingRegistry: () => new Promise((resolve) => resolve({})),
  };
});

const widgetStrings = i18nStrings.ScheduleNoteBook.MainPanel.AdvancedOptions;
const errorStrings = i18nStrings.ScheduleNoteBook.MainPanel.ErrorMessages;

let mockApp: JupyterFrontEnd;

const mockExecutionEnvironments = {
  environment_configs: null,
  auto_detected_config: [
    {
      name: "s3_input",
      label: "Input S3",
      description: "S3 Location to store all notebook related files",
      value: "s3://sagemaker-notebook-execution-748478975813/",
    },
    {
      name: "s3_output",
      label: "Output S3",
      description: "S3 Location to store all Output artifacts",
      value: "s3://sagemaker-notebook-execution-748478975913/",
    },
    {
      name: "role_arn",
      label: "Execution Role ARN",
      description: "IAM Role to be used by the Notebook Execution Engine",
      value: [
        "arn:aws:iam::748478975813:role/service-role/AmazonSageMaker-ExecutionRole-20220409T160852",
      ],
    },
    {
      name: "image",
      label: "SageMaker Image",
      description: "SageMaker Image to execute the notebook in",
      value: "ecr-location",
    },
    {
      name: "kernel",
      label: "Python Kernel",
      description: "Python Kernel to execute the notebook in",
      value: "kernel name from notebook metadata",
    },
    {
      name: "lcc_arn",
      label: "LCC ARN",
      description: "LCC ARN to be executed before execution",
      value: [],
    },
    {
      name: "vpc_security_group_ids",
      label: "VPC Config Security Group IDs",
      description: "List of Security GroupIDs for the notebook to be executed",
      value: [
        {
          name: "sg-1",
          is_selected: true,
        },
        {
          name: "sg-2",
          is_selected: false,
        },
        {
          name: "sg-3",
          is_selected: false,
        },
      ],
    },
    {
      name: "vpc_subnets",
      label: "VPC Config Subnets",
      description: "List of Subnets for the notebook to be executed in",
      value: [
        {
          name: "subnet-1",
          is_selected: true,
        },
        {
          name: "subnet-2",
          is_selected: false,
        },
        {
          name: "subnet-3",
          is_selected: false,
        },
      ],
    },
    {
      name: "app_network_access_type",
      label: "App Network Access Type",
      description: "Access type for the network",
      value: "VpcOnly",
    },
  ],
};

describe('Create Notebook Job From tests', () => {
  beforeEach(() => {
    mockApp = {
      hasPlugin: (plugin: string) => plugin === STUDIO_SAGEMAKER_UI_PLUGIN_ID,
      listPlugins: () => new Set([STUDIO_SAGEMAKER_UI_PLUGIN_ID]),
    } as unknown as JupyterFrontEnd;
  });

  const defaultProps: CreateNotebookJobFormProps = {
    handleErrorsChange: jest.fn(),
    handleModelChange: jest.fn(),
    errors: {},
    model: {
      jobName: 'test-job',
      jobDefinitionId: 'job-id',
      inputFile: 'input-file',
      environment: '',
      createType: 'Job',
      runtimeEnvironmentParameters: {},
      scheduleInterval: '',
    },
    jobsView: JobsView.CreateForm,
    executionEnvironments: mockExecutionEnvironments,
  } as unknown as CreateNotebookJobFormProps;

  const setup = async (newProps: Partial<CreateNotebookJobFormProps>) => {
    const props: CreateNotebookJobFormProps = {
      ...defaultProps,
      ...newProps,
    } as unknown as CreateNotebookJobFormProps;
    render(
      <PluginEnvironmentProvider app={mockApp}>
        <CreateNotebookJobForm
          {...props}
        />
      </PluginEnvironmentProvider>
    );
  };

  describe('In Create Job View and Public-Internet domain', () => {
    it('does not render checkbox and VPC specific UI fields', async () => {
      const mockAutoDetectedConfig = mockExecutionEnvironments.auto_detected_config;
      mockAutoDetectedConfig[mockAutoDetectedConfig.length - 1] = {
        name: 'app_network_access_type',
        label: 'App Network Access Type',
        description: 'Access type for the network',
        value: 'PublicInternetOnly'
      };

      waitFor(async () => {
        await setup({
          jobsView: JobsView.CreateForm,
          executionEnvironments: {
            ...defaultProps.executionEnvironments,
            auto_detected_config: mockAutoDetectedConfig
          }
        });
      })


      const checkbox = await screen.queryByTestId('vpc-checkbox');
      expect(checkbox).not.toBeInTheDocument();

      const subnetsLabel = await screen.queryByText(widgetStrings.subnet);
      expect(subnetsLabel).not.toBeInTheDocument();

      const securityGroupsLabel = await screen.queryByText(
        widgetStrings.securityGroup
      );
      expect(securityGroupsLabel).not.toBeInTheDocument();
    });
  });
  
  describe('Custom image', () => {
    it('should initialize form state correctly when using custom image', async () => {
      if (defaultProps.model.runtimeEnvironmentParameters) {
        defaultProps.model.runtimeEnvironmentParameters.sm_image = 'arn:aws:sagemaker:us-west-2:236514542706:image/datascience-1.0/2';
        defaultProps.model.runtimeEnvironmentParameters.sm_kernel = 'python3';
      }

      setup({
        jobsView: JobsView.CreateForm,
      });

      const dropdown = await screen.findByTestId('sm_image_dropdown');
      const smImageDropdown = within(dropdown).getByRole('combobox') as HTMLInputElement;
      fireEvent.input(smImageDropdown, { target: { value: 'Data Science v2' } });
      expect(smImageDropdown.value).toEqual("Data Science v2");
    });

    it('should initialize form state correctly when using non custom image', async () => {
      if (defaultProps.model.runtimeEnvironmentParameters) {
        defaultProps.model.runtimeEnvironmentParameters.sm_image = 'arn:aws:sagemaker:us-west-2:236514542706:image/python-3.6';
        defaultProps.model.runtimeEnvironmentParameters.sm_kernel = 'python3';
      }

      setup({
        jobsView: JobsView.CreateForm,
      });

      const dropdown = await screen.findByTestId('sm_image_dropdown');
      const smImageDropdown = within(dropdown).getByRole('combobox') as HTMLInputElement;
      fireEvent.input(smImageDropdown, { target: { value: 'Base Python' } });
      expect(smImageDropdown.value).toEqual("Base Python");
    });
  });
});
