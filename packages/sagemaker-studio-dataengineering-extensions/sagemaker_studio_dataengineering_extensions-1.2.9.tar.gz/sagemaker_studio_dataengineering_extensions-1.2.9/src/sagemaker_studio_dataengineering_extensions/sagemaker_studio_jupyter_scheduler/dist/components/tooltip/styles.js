import { css } from '@emotion/css';
const toolTipPopperStyles = () => css `
  popper: {
    '& .MuiTooltip-tooltip': {
      backgroundColor: 'var(--color-light)',
      boxShadow: 'var(--tooltip-shadow)',
      color: 'var(--tooltip-text-color',
      padding: 'var(--padding-16)',
      fontSize: 'var(--font-size-0)',
    },
  },
`;
const toolTipStyles = () => css `
  tooltip: {
    '& .MuiTooltip-arrow': {
      color: 'var(--tooltip-surface)',
      '&:before': {
        boxShadow: 'var(--tooltip-shadow)',
      },
    },
  },
`;
export { toolTipStyles, toolTipPopperStyles };
//# sourceMappingURL=styles.js.map