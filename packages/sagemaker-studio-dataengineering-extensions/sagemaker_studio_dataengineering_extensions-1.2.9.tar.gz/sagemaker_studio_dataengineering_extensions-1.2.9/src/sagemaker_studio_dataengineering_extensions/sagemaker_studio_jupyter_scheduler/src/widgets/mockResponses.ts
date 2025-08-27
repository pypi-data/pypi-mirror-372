export const MOCK_ENVIRONMENT = {
  environment_configs: null,
  auto_detected_config: [
    {
      name: 's3_input',
      label: 'Input S3',
      description: 'S3 Location to store all notebook related files',
      value: 's3://sagemaker-notebook-execution-638670477360/',
    },
    {
      name: 'app_network_access_type',
      label: 'App Network Access Type',
      description: 'Access type for the network',
      value: 'VpcOnly',
    },
    {
      name: 's3_output',
      label: 'Output S3',
      description: 'S3 Location to store all Output artifacts',
      value: 's3://sagemaker-notebook-execution-638670477360/',
    },
    {
      name: 'role_arn',
      label: 'Execution Role ARN',
      description: 'IAM Role to be used by the Notebook Execution Engine',
      value: ['arn:aws:iam::638670477360:role/service-role/AmazonSageMaker-ExecutionRole-20210507T174789'],
    },
    {
      name: 'image',
      label: 'SageMaker Image',
      description: 'SageMaker Image to execute the notebook in',
      value: 'ecr-location',
    },
    {
      name: 'kernel',
      label: 'Python Kernel',
      description: 'Python Kernel to execute the notebook in',
      value: 'kernel name from notebook metadata',
    },
    {
      name: 'lcc_arn',
      label: 'LCC ARN',
      description: 'LCC ARN to be executed before execution',
      value: [],
    },
    {
      name: 'vpc_security_group_ids',
      label: 'VPC Config Security Group IDs',
      description: 'List of Security GroupIDs for the notebook to be executed',
      value: [
        {
          name: 'sg-1',
          is_selected: true,
        },
        {
          name: 'sg-2',
          is_selected: false,
        },
        {
          name: 'sg-3',
          is_selected: false,
        },
      ],
    },
    {
      name: 'vpc_subnets',
      label: 'VPC Config Subnets',
      description: 'List of Subnets for the notebook to be executed in',
      value: [
        {
          name: 'subnet-1',
          is_selected: true,
        },
        {
          name: 'sunet-2',
          is_selected: false,
        },
        {
          name: 'subnet-3',
          is_selected: false,
        },
      ],
    },
  ],
};
