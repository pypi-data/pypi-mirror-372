import React from 'react';
import { Tooltip } from '../Tooltip';
import { render, fireEvent, screen, } from '@testing-library/react';

describe('<Tooltip />', () => {
  const title = 'This is a tooltip';
  const childTestId = 'child-test-id';
  const toolTipTestId = 'tool-tip-test-id';

  beforeEach(() => {
    render(<Tooltip data-testid={toolTipTestId} title={title}>
      <div>
        <span data-testid={childTestId}> Child Span</span>
      </div>
    </Tooltip>)
  });

  it('should render the tooltip with children', () => {
    expect(screen.getByTestId(childTestId)).toBeInTheDocument();
  });

  it('should show tooltip on hover', async () => {
    expect(screen.queryByText(title)).not.toBeInTheDocument();
    fireEvent.mouseOver(screen.getByTestId('toolTip'));
    expect(await screen.findByText(title)).toBeInTheDocument();
  });
});
