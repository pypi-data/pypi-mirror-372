import React from 'react';
import Link from '@mui/material/Link';
import { cx } from '@emotion/css';
import { LinkBase } from './styles';
import { Link as RouterLinkInt } from 'react-router-dom';
const RouterLink = ({ className, children, to, ...materialLinkProps }) => {
    const props = {
        ...materialLinkProps,
        className: cx(LinkBase(), className),
        to,
        component: RouterLinkInt,
    };
    return React.createElement(Link, { "data-testid": 'link-to', ...props }, children);
};
export { RouterLink };
//# sourceMappingURL=RouterLink.js.map