import React, { MouseEventHandler } from 'react';
import { LinkProps as MuiLinkProps } from '@mui/material';
import { LinkTarget, LinkUnderline } from './types';
export interface LinkProps extends MuiLinkProps {
    readonly disabled?: boolean;
    readonly target?: LinkTarget;
    readonly underline?: LinkUnderline;
    readonly onClick?: MouseEventHandler<HTMLAnchorElement>;
    readonly className?: string;
    readonly href?: string;
    readonly children?: string | React.ReactElement;
}
declare const Link: React.FunctionComponent<LinkProps>;
export { Link };
//# sourceMappingURL=Link.d.ts.map