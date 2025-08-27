import React from 'react';
import Link, { LinkProps as MuiLinkProps } from '@mui/material/Link';
import { cx } from '@emotion/css';
import { LinkUnderline } from './types';
import { LinkBase } from './styles';
import { Link as RouterLinkInt } from 'react-router-dom';

export interface RouterLinkProps extends MuiLinkProps {
  readonly disabled?: boolean;
  readonly underline?: LinkUnderline;
  readonly to?: string;
  readonly className?: string;
  readonly children?: any;
}

const RouterLink: React.FunctionComponent<RouterLinkProps> = ({ className, children, to, ...materialLinkProps }) => {
  const props = {
    ...materialLinkProps,
    className: cx(LinkBase(), className),
    to,
    component: RouterLinkInt,
  };

  return <Link data-testid={'link-to'} {...props}>{children}</Link>;
};

export { RouterLink };
