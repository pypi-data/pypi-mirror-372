import { css } from '@emotion/css';

export const JobEnvironmentContainer = css`
  display: flex;
  flex-direction: column;
  padding: 10px;
`;

export const KernelImageSelectorContainer = css`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

export const ImageContainer = css`
  display: flex;
  flex-direction: column;
`;

export const flyoutCaret = css`
  transform: rotate(90deg);
`;

export const imageDropdownDescContainer = css`
  display: flex;
  flex-flow: row nowrap;
  justify-content: space-between;
  align-items: center;
  width: 100%;
`;

export const imageDropdownOptionLink = css`
  font-size: var(--jp-ui-font-size0);
  min-width: max-content;
`;

export const imageDropdownOptionDesc = css`
  font-size: var(--jp-ui-font-size0);
  color: var(--jp-inverse-layout-color4);
  padding-right: 5px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
`;

export const imageDropdownOptionSpan = css`
  width: 100%;
`;

export const imageDropdownOptionLabel = css`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  &[data-selected='true'] {
    background-image: var(--jp-check-icon);
    background-size: 15px;
    background-repeat: no-repeat;
    background-position: 100% center;
  }
  & > p {
    max-width: calc(100% - 10px);
  }
`;
