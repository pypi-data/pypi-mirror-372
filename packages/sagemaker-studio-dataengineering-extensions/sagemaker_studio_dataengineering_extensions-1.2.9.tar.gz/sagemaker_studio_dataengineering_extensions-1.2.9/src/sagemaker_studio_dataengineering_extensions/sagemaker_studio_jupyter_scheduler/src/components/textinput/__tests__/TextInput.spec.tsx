import React from 'react';
import { TextInput, TextInputProps } from '../TextInput';
import { render, fireEvent } from '@testing-library/react';

describe('<TextInput />', () => {
  it('should render with default props', () => {
    const { getByTestId } = render(<TextInput />);

    const inputField = getByTestId("inputField") as HTMLInputElement;
    expect(inputField.value).toBe(undefined);
    expect(inputField.disabled).toBe(undefined);
    expect(inputField.placeholder).toBe(undefined);
  });

  it('should render with custom props', () => {
    const props: TextInputProps = {
      disabled: true,
      placeholder: 'type...',
    };
    const { getByTestId } = render(<TextInput {...props} />);
    const inputField = getByTestId("inputField").querySelector('input');
    expect(inputField?.disabled).toBeTruthy();
    expect(inputField?.placeholder).toBe('type...');
  });

  it('should render with defaultValue if it is provided', () => {
    const defaultValue = 'default value';
    const { getByTestId } = render(<TextInput defaultValue={defaultValue} />);
    const inputField = getByTestId("inputField").querySelector('input');
    expect(inputField?.defaultValue).toBe(defaultValue);

  });

  it('should call onChange callback if it is provided', async () => {
    const mockOnChange = jest.fn();
    const defaultValue = 'default value';
    const props: TextInputProps = {
      disabled: true,
      placeholder: 'type...',
      onChange: mockOnChange,
      defaultValue: defaultValue,
      InputProps: {
        readOnly: false
      },
    };

    const { getByTestId } = render(<TextInput {...props} />);
    const inputField = getByTestId("inputField").querySelector('input');
    const mockChangeEvent = { target: { value: 'new value' } };
    fireEvent.focus(inputField as Element)
    fireEvent.input(inputField as Element, mockChangeEvent);
    expect(mockOnChange).toHaveBeenCalled();
  });
});
