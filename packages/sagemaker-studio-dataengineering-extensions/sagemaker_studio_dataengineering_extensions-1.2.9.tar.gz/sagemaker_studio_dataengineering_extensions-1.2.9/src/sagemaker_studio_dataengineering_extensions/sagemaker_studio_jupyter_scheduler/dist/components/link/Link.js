import React from 'react';
import { Link as MuiLink } from '@mui/material';
import { cx } from '@emotion/css';
import { LinkTarget } from './types';
import { LinkBase } from './styles';
const Link = ({ className, disabled = false, children, onClick, target = LinkTarget.Content, ...materialLinkProps }) => {
    const external = target === LinkTarget.External;
    const props = {
        ...materialLinkProps,
        className: cx(LinkBase(), className),
        target,
        onClick: disabled ? undefined : onClick,
        rel: external ? 'noopener noreferrer' : undefined,
    };
    return React.createElement(MuiLink, { ...props, "data-testid": 'link' }, children);
};
export { Link };
//# sourceMappingURL=Link.js.map