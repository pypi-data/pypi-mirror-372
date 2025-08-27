import React from 'react';
import { Link, LinkTarget } from '../../../components/link';
import { i18nStrings } from '../../../constants';
import { imageDropdownDescContainer, imageDropdownOptionDesc, imageDropdownOptionLabel, imageDropdownOptionLink, imageDropdownOptionSpan, } from './studioStyles';
export const StudioImageSelectorOption = (option, label, selected) => {
    return (React.createElement("span", { className: imageDropdownOptionSpan },
        React.createElement("div", { className: imageDropdownOptionLabel, "data-selected": selected },
            React.createElement("p", null, label ? label : option.label)),
        renderLinkInDescription(option.optionMetadata && option.optionMetadata.description)));
};
const renderLinkInDescription = (description) => {
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
    return (React.createElement("div", { className: imageDropdownDescContainer },
        React.createElement("span", { className: imageDropdownOptionDesc }, trimmedDescription),
        links &&
            links.map((link) => (React.createElement(Link, { className: imageDropdownOptionLink, key: link, href: link, target: LinkTarget.External }, i18nStrings.KernelSelector.imageSelectorOption.linkText)))));
};
//# sourceMappingURL=StudioImageSelectorOption.js.map