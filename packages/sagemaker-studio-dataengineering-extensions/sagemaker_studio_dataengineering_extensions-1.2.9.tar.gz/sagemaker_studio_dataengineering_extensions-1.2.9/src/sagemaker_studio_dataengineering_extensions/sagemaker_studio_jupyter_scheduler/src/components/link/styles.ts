import { css } from '@emotion/css';

const LinkBase = () => css`
  cursor: pointer;
  text-decoration: none;
  color: var(--jp-brand-color1);

  &:hover {
    text-decoration: none;
    color: var(--jp-brand-color1);
  }
`;

export { LinkBase };
