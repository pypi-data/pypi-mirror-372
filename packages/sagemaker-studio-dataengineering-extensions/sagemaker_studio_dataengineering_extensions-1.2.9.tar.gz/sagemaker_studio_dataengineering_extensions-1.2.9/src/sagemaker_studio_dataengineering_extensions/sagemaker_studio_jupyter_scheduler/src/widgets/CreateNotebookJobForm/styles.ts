import { css } from '@emotion/css';

export const SelectInputContainer = css`
  display: flex;
  flex-direction: column;
`;

export const InputContainer = css`
  display: flex;
  flex-direction: column;
`;

export const tooltipsContainer = css`
  display: inline-flex;
  svg {
    width: 0.75em;
    height: 0.75em;
    transform: translateY(-2px);
  }
`;

export const tooltips = css`
  svg {
    width: 0.75em;
    height: 0.75em;
    transform: translateY(1px);
  }
`;

export const getAdditionalOptionsContainerStyles = (isDetailsView = false) => css`
  display: flex;
  flex-direction: column;
  ${!isDetailsView ? `max-width : 500px;` : ``}
  .MuiCheckbox-colorPrimary.Mui-checked {
    color: var(--jp-brand-color1);
  }
  .MuiButton-containedPrimary:hover {
    background-color: var(--jp-brand-color1);
  }
`;

export const ValidationMessageStyled = css`
  font-size: var(--jp-content-font-size1);
`;

export const ErrorIconStyled = css`
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 0.5rem;
  svg {
    width: var(--jp-ui-font-size1);
    height: var(--jp-ui-font-size1);
    path {
      fill: var(--jp-error-color1);
    }
  }
`;

export const requiredInput = (required: boolean | undefined) => {
  if (required) {
    return css`
      &:after {
        content: '*';
        color: var(--jp-error-color1);
      }
    `;
  }
  return '';
};

export const InputLabel = (required = false) => css`
  color: var(--jp-color-root-light-800);
  font-weight: 400;
  font-size: var(--jp-ui-font-size1);
  line-height: var(--jp-ui-font-size1);
  margin-bottom: var(--jp-ui-font-size1);
  ${required &&
  `
    &:after {
      content: '*';
      color: var(--jp-error-color1);
    }
  `}
`;
