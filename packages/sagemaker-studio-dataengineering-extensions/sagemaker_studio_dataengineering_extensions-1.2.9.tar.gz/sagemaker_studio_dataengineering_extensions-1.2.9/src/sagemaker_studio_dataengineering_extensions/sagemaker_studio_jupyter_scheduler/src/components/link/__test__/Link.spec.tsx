import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import { Link, LinkProps } from '../Link';
import { LinkTarget, LinkUnderline } from '../types';

describe('<Link />', () => {
  const children = 'Test';
  const href = 'https://www.amazon.com';
  const defaultProps: LinkProps = {
    children,
    href,
    underline: LinkUnderline.Hover,
    target: LinkTarget.External,
    disabled: false,
  };

  it('renders correctly with default props', () => {
    const props = { ...defaultProps };
    const { getByTestId } = render(<Link {...props} />);
    expect(getByTestId('link')).toBeInTheDocument();
  });

  it('should handle onClick callback function properly', () => {
    const onClickHandler = jest.fn();
    const props = { ...defaultProps, onClick: onClickHandler };
    const { getByTestId } = render(<Link {...props} />);

    const link = getByTestId('link');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('href', 'https://www.amazon.com');
    fireEvent.click(link);
    expect(onClickHandler).toHaveBeenCalledTimes(1);
  });
});
