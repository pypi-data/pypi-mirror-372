import React from 'react';
import { LinkProps as MuiLinkProps } from '@mui/material/Link';
import { LinkUnderline } from './types';
export interface RouterLinkProps extends MuiLinkProps {
    readonly disabled?: boolean;
    readonly underline?: LinkUnderline;
    readonly to?: string;
    readonly className?: string;
    readonly children?: any;
}
declare const RouterLink: React.FunctionComponent<RouterLinkProps>;
export { RouterLink };
//# sourceMappingURL=RouterLink.d.ts.map