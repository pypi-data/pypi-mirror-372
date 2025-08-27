import React from 'react';
import { Link, LinkTarget } from '../../../components/link';
import { DropdownItem } from '../../../components/selectinput';
import { i18nStrings } from '../../../constants';
import {
  imageDropdownDescContainer,
  imageDropdownOptionDesc,
  imageDropdownOptionLabel,
  imageDropdownOptionLink,
  imageDropdownOptionSpan,
} from './studioStyles';

export const StudioImageSelectorOption = (option: DropdownItem, label?: string | JSX.Element, selected?: boolean) => {
  return (
    <span className={imageDropdownOptionSpan}>
      <div className={imageDropdownOptionLabel} data-selected={selected}>
        <p>{label ? label : option.label}</p>
      </div>
      {renderLinkInDescription(option.optionMetadata && option.optionMetadata.description)}
    </span>
  );
};

const renderLinkInDescription = (description: string): React.ReactElement | undefined => {
  if (!description) {
    return undefined;
  }
  const linkRegexExp = /(((https?:\/\/)|(www\.))[^\s]+)/g;
  const links = description.match(linkRegexExp);
  if (links) {
    console.log('links', links);
    for (const link of links) {
      description = description.replace(link, ' ');
    }
  }

  const trimmedDescription = description.trim();

  return (
    <div className={imageDropdownDescContainer}>
      <span className={imageDropdownOptionDesc}>{trimmedDescription}</span>
      {links &&
        links.map((link) => (
          <Link className={imageDropdownOptionLink} key={link} href={link} target={LinkTarget.External}>
            {i18nStrings.KernelSelector.imageSelectorOption.linkText}
          </Link>
        ))}
    </div>
  );
};
