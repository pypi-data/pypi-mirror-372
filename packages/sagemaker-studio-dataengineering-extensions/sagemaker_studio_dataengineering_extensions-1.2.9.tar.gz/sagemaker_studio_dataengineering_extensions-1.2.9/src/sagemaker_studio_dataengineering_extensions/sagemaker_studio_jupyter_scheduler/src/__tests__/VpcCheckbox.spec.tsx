import React, { useState } from 'react';

import '@testing-library/jest-dom';
import { render, screen, fireEvent, within } from '@testing-library/react';

import { VpcCheckbox, VpcProps } from '../widgets/CreateNotebookJobForm/AdvancedOptions/VpcCheckbox';
import { i18nStrings } from '../constants';

const vpcErrorStrings =
  i18nStrings.ScheduleNoteBook.MainPanel.ErrorMessages.VPCErrors;
const labelStrings = i18nStrings.ScheduleNoteBook.MainPanel.AdvancedOptions;

const ControlledVPCCheckbox = (props: VpcProps) => {
  const [vpcProps, setVpcProps] = useState(props);

  const setChecked = () => {
    setVpcProps({
      ...vpcProps,
      isChecked: !vpcProps.isChecked
    });
  };

  return <VpcCheckbox {...vpcProps} setChecked={setChecked} data-testid="vpc-checkbox" />;
};

describe('VpcCheckbox tests', () => {
  const defaultProps: VpcProps = {
    isChecked: false,
    formState: {
      sm_lcc_init_script_arn: '',
      sm_init_script: '',
      role_arn: '',
      vpc_security_group_ids: [],
      vpc_subnets: [],
      sm_kernel: '',
      sm_image: '',
      s3_input: '',
      s3_output: '',
      sm_output_kms_key: '',
      sm_volume_kms_key: ''
    },
    formErrors: {},
    initialSecurityGroups: [],
    initialSubnets: [],
    availableSubnets: [],
    setChecked: jest.fn(),
    setFormState: jest.fn(),
    setFormErrors: jest.fn()
  };

  const setup = (newProps?: Partial<VpcProps>) => {
    const props = {
      ...defaultProps,
      ...newProps,
    }

    render(<ControlledVPCCheckbox {...props} />);
  }

  it('renders the checkbox', () => {
    setup();

    expect(screen.getByText(labelStrings.useVPC)).toBeInTheDocument();
    expect(screen.getByTestId('vpc-checkbox')).toBeInTheDocument();
  });

  it('renders the correct checked state when clicked', () => {
    setup();

    const checkBox = within(screen.getByTestId('vpc-checkbox')).getByRole('checkbox') as HTMLInputElement;
    expect(checkBox.checked).toBe(false);

    fireEvent.click(checkBox);
    expect(checkBox.checked).toBe(true);
  });

  it('when checked, calls setFormState method with correct params', () => {
    const mockInitialSubnets = ['subnet-1', 'subnet-2', 'subnet-3'];
    setup({
      initialSubnets: mockInitialSubnets
    });

    const checkBox = within(screen.getByTestId('vpc-checkbox')).getByRole('checkbox') as HTMLInputElement;
    fireEvent.click(checkBox);

    expect(defaultProps.setFormState).toHaveBeenCalledWith({
      ...defaultProps.formState,
      vpc_subnets: mockInitialSubnets,
    });
  });

  it('when checked, calls setFormState method with correct params', () => {
    setup();

    const checkBox = within(screen.getByTestId('vpc-checkbox')).getByRole('checkbox') as HTMLInputElement;
    fireEvent.click(checkBox);

    expect(defaultProps.setFormState).toHaveBeenCalledWith(defaultProps.formState);
    expect(defaultProps.setFormErrors).toHaveBeenCalledWith({
      subnetError: `${vpcErrorStrings.RequiresPrivateSubnet} ${vpcErrorStrings.NoPrivateSubnetsInSageMakerDomain}`
    });
  });

  it('when checked and has subnets, calls setFormErrors with', () => {
    const mockAvailableSubnets = ['subnet-1', 'subnet-2'];
    setup({ availableSubnets: mockAvailableSubnets });

    const checkBox = within(screen.getByTestId('vpc-checkbox')).getByRole('checkbox') as HTMLInputElement;
    fireEvent.click(checkBox);

    expect(checkBox.checked).toBe(true);
    expect(defaultProps.setFormState).toHaveBeenCalledWith(defaultProps.formState);
    expect(defaultProps.setFormErrors).toHaveBeenCalledWith({
      ...defaultProps.formErrors,
      subnetError: `${vpcErrorStrings.RequiresPrivateSubnet} ${vpcErrorStrings.NoPrivateSubnetsInSageMakerDomain}. ${vpcErrorStrings.YouMayChooseOtherSubnets}`
    });
  });

  it('when un-checked, resets form state security groups and subnets', () => {
    setup({ isChecked: true });

    const checkBox = within(screen.getByTestId('vpc-checkbox')).getByRole('checkbox') as HTMLInputElement;
    fireEvent.click(checkBox);
    expect(defaultProps.setFormState).toHaveBeenCalledWith({
      ...defaultProps.formState,
      vpc_security_group_ids: [],
      vpc_subnets: []
    });

    expect(defaultProps.setFormErrors).toHaveBeenCalledWith({
      ...defaultProps.formErrors,
      subnetError: '',
      securityGroupError: ''
    });
  });
});
