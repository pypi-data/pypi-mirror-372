import React from 'react';
import { Link, LinkTarget } from '../components/link';

const renderTextWithLinks = (text: string, links: { [linkKey: string]: { linkString: string; linkHref: string } }) => {
  const textBreakdowns = text.split('%');

  return (
    <>
      {textBreakdowns.map((textBreakdown) => {
        if (textBreakdown.startsWith('{')) {
          const [linkKey, ...splitedPartWithoutLink] = textBreakdown.replace('{', '').split('}');
          const linkDefinition = links[linkKey];
          const partWithoutLink = splitedPartWithoutLink.join('');
          return linkDefinition ? (
            <>
              <Link key={linkKey} href={linkDefinition.linkHref} target={LinkTarget.External}>
                {linkDefinition.linkString}
              </Link>
              {partWithoutLink}
            </>
          ) : (
            <>{textBreakdown}</>
          );
        } else {
          return <>{textBreakdown}</>;
        }
      })}
    </>
  );
};

export { renderTextWithLinks };
