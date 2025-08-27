import React from 'react';
import { Link, LinkTarget } from '../components/link';
const renderTextWithLinks = (text, links) => {
    const textBreakdowns = text.split('%');
    return (React.createElement(React.Fragment, null, textBreakdowns.map((textBreakdown) => {
        if (textBreakdown.startsWith('{')) {
            const [linkKey, ...splitedPartWithoutLink] = textBreakdown.replace('{', '').split('}');
            const linkDefinition = links[linkKey];
            const partWithoutLink = splitedPartWithoutLink.join('');
            return linkDefinition ? (React.createElement(React.Fragment, null,
                React.createElement(Link, { key: linkKey, href: linkDefinition.linkHref, target: LinkTarget.External }, linkDefinition.linkString),
                partWithoutLink)) : (React.createElement(React.Fragment, null, textBreakdown));
        }
        else {
            return React.createElement(React.Fragment, null, textBreakdown);
        }
    })));
};
export { renderTextWithLinks };
//# sourceMappingURL=rendering.js.map