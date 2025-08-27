import { css } from '@emotion/css';

export const EnvironmentVariablesContainer = css`
  display: flex;
  align-items: flex-end;
  padding-right: 1em;
  gap: 20px;
`;

export const EnvironmentVariableContainer = css`
  display: flex;
  flex-direction: column;
`;

export const EnvironmentVariablesInput = css`
  width: 170px;
`;

export const InputContainer = css`
  display: flex;
  flex-direction: column;
  margin-bottom: var(--jp-padding-large);
`;

export const EnvironmentVariablesSection = css`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

export const InputLabel = css`
  font-weight: 400;
  font-size: var(--jp-ui-font-size1);
  line-height: var(--jp-ui-font-size1);
`;

//Setting one off font-size to make it fit better inline in form.Re-visit to handle button better in future
export const ConfigBtn = css`
  background-color: var(--jp-brand-color1);
  font-size: var(--jp-ui-font-size1);
  text-transform: none;
`;

export const tooltipsContainer = css`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  svg {
    width: 0.75em;
    height: 0.75em;
  }
`;
