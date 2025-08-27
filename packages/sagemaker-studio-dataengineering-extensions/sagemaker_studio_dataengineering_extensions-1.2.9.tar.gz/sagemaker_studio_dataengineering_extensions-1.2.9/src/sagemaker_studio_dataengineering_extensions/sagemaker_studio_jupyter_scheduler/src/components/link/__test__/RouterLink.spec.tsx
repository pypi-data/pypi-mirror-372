import { render, fireEvent, screen, within } from '@testing-library/react';
import React from 'react';
import { RouterLink, RouterLinkProps } from '../RouterLink';
import { LinkUnderline } from '../types';
import { MemoryRouter } from 'react-router-dom';
import { Experimental_CssVarsProvider } from '@mui/material';

describe('<RouterLink />', () => {
  const to = '/user';
  const defaultProps: RouterLinkProps = {
    disabled: false,
    underline: LinkUnderline.Always,
    to: to,
  };

  it('renders correctly with default props', () => {
    const props = defaultProps;
    const label = 'label';
    // const test = render(<Router><RouterLink {...props}>{label}</RouterLink></Router>);
    const { getByTestId } = render(<MemoryRouter>
      <RouterLink {...props}>{label}</RouterLink>
    </MemoryRouter>)
    const { getByText } = within(screen.getByTestId('link-to'))

    expect(getByTestId('link-to')).toHaveAttribute('href', '/user');
    expect(getByText('label')).toBeInTheDocument()
  });
});
