import React, { MouseEventHandler } from 'react';
import { Link as MuiLink, LinkProps as MuiLinkProps } from '@mui/material';
import { cx } from '@emotion/css';
import { LinkTarget, LinkUnderline } from './types';
import { LinkBase } from './styles';

export interface LinkProps extends MuiLinkProps {
  readonly disabled?: boolean;
  readonly target?: LinkTarget;
  readonly underline?: LinkUnderline;
  readonly onClick?: MouseEventHandler<HTMLAnchorElement>;
  readonly className?: string;
  readonly href?: string;
  readonly children?: string | React.ReactElement;
}

const Link: React.FunctionComponent<LinkProps> = ({
  className,
  disabled = false,
  children,
  onClick,
  target = LinkTarget.Content,
  ...materialLinkProps
}) => {
  const external = target === LinkTarget.External;

  const props = {
    ...materialLinkProps,
    className: cx(LinkBase(), className),
    target,
    onClick: disabled ? undefined : onClick,
    rel: external ? 'noopener noreferrer' : undefined,
  };

  return <MuiLink {...props} data-testid={'link'} >{children}</MuiLink>;
};

export { Link };
