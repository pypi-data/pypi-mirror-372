import { css } from '@emotion/css';

export const WidgetContainer = css`
  box-sizing: border-box;
  width: 100%;
  padding: var(--jp-padding-large);
  flex-direction: column;
  display: flex;
  color: var(--jp-ui-font-color0);
`;

export const Header = css`
  width: 100%;
  display: flex;
  flex-flow: row nowrap;
  justify-content: space-between;
  padding-bottom: var(--jp-padding-20);
  color: var(--jp-ui-font-color0);
`;

export const HeaderDescription = css`
  max-width: 525px;
  color: var(--jp-ui-font-color2);
  margin-bottom: var(--jp-padding-medium);
`;

export const CategoryContainerDiv = css`
  display: block;
  margin-bottom: 0.5em;
  overflow-y: scroll;
`;

export const CategoryTitleDiv = css`
  align-items: center;
  display: inline-flex;
  margin-bottom: var(--jp-padding-16);
  margin-left: 1em;
  font-size: var(--jp-ui-font-size3);
  color: var(--jp-ui-font-color0);
`;

export const WidgetFieldsContainer = css`
  display: flex;
  flex-direction: column;
  font-size: 12px;
  color: var(--jp-ui-font-color0);
  padding: 10px;
  overflow-x: auto;
  overflow-y: hidden;
  gap: 20px;
`;
export const SecurityConfigContainer = css`
  display: flex;
  justify-content: space-between;
`;

export const EnvironmentVariablsContainer = css`
  display: flex;
  align-items: center;
`;

export const MarginBottom = css`
  margin-bottom: var(--jp-padding-medium);
`;
export const ConfigBtn = css`
  width: 50% !important;
  text-align: center;
  height: 30px;
  font-size: 12px !important;
`;
export const ActionBtnContainer = css`
  display: inline-flex;
  justify-content: right;
`;

export const ActionBtn = css`
  height: fit-content;
  width: 90px;
  text-align: center;
  margin-right: var(--jp-padding-medium);
`;
export const ActionBtnWrapper = css`
  position: absolute;
  right: 0%;
  bottom: 0%;
  margin-bottom: var(--jp-padding-large);
`;
export const SelectWidth = css`
  div:nth-child(2) {
    width: 98%;
  }
`;
export const SelectWidthInstanceType = css`
  div:nth-child(2) {
    width: 49%;
  }
`;

export const SelectWidthKernel = css`
  div:nth-child(2) {
    width: 150px;
  }
`;

export const CredentialsErrorDialogParagraph = css`
  width: 500px;
  margin-bottom: var(--jp-size-4);
`;

export const TooltipCheckBoxContainer = css`
  display: flex;
  align-items: center;
`;

export const TooltipTextContainer = css`
  display: flex;
  align-items: center;
`;

export const TooltipLink = css`
  color: var(--jp-brand-color3);
`;

export const Checkbox = css`
  padding: 4px;
`;

export const PopperInteractive = css`
  color: var(--jp-ui-font-color0);
`;

export const AdvancedOptionsSelectContainer = css`
  display: flex;
  flex-direction: column;
  gap: var(--jp-ui-font-size1);
`;

export const ErrorMessageBlock = css`
  color: var(--jp-error-color1);
  padding: 12px;
`;
