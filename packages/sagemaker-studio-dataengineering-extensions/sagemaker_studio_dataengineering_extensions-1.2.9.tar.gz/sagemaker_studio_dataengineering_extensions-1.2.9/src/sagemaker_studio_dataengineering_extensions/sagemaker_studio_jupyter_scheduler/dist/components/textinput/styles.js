import { css } from '@emotion/css';
import { TextInputSize } from './types';
const lineHeights = {
    [TextInputSize.Large]: 'var(--jp-content-line-height-3)',
    [TextInputSize.Medium]: 'var(--jp-content-line-height-2)',
    [TextInputSize.Small]: 'var(--jp-content-line-height-1-25)',
};
const paddingSizes = {
    [TextInputSize.Large]: '1em',
    [TextInputSize.Medium]: '0.5em',
    [TextInputSize.Small]: '0.25em',
};
const inputStyles = (size) => css `
  root: {
    background: 'var(--jp-input-active-background)',
    borderTopLeftRadius: 'var(--jp-border-radius)',
    borderTopRightRadius: 'var(--jp-border-radius)',
    fontSize: 'var(--jp-ui-font-size2)',
    '&.Mui-focused': {
      background: 'var(--jp-input-active-background)',
    },
    '&.Mui-disabled': {
      borderRadius: 'var(--jp-border-radius)',
      color: 'var(--text-input-font-color-disabled)',
    },
    '&.MuiInput-underline.Mui-disabled:before': {
      borderBottom: 'none',
    },
  },
  underline: {
    borderBottom: 'none',
    '&:before': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&:after': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&:not(.Mui-disabled):hover:before': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&.Mui-error:hover:after': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&.Mui-error:after': {
      borderBottom: 'var(--jp-border-width) solid',
    },
  },
  input: {
    color: 'var(--jp-ui-font-color0)',
    lineHeight: ${lineHeights[size]},
    padding: ${paddingSizes[size]},
  },   
`;
const inputLabelStyles = css `
  root: {
    fontFamily: 'var(--jp-cell-prompt-font-family)',
    color: 'var(--jp-input-border-color)',
    marginBottom: 'var(--padding-small)',
    '&.Mui-error': {
      fontFamily: 'var(--jp-cell-prompt-font-family)',
      color: 'var(--jp-error-color1)',
    },
    '&.Mui-disabled': {
      fontFamily: 'var(--jp-cell-prompt-font-family)',
      color: 'var(--jp-error-color1)',
    },
  },
`;
const formHelperTextStyles = () => css `
    fontSize: 'var(--jp-ui-font-size0)',
    color: 'var(--text-input-helper-text)',
    '&.Mui-error': {
      color: 'var(--jp-error-color1)',
    },
    '&.Mui-disabled': {
      color: 'var(--jp-error-color1)',
    },
`;
const TextInputBase = () => css `
  .MuiFormHelperText-root.Mui-error::before {
    display: inline-block;
    vertical-align: middle;
    background-size: 1rem 1rem;
    height: var(--text-input-error-icon-height);
    width: var(--text-input-error-icon-width);
    background-image: var(--text-input-helper-text-alert-icon);
    background-repeat: no-repeat;
    content: ' ';
  }
`;
export { inputStyles, TextInputBase, inputLabelStyles, formHelperTextStyles, lineHeights, paddingSizes };
//# sourceMappingURL=styles.js.map