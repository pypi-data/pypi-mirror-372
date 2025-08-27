import React from 'react';
import { toolTipStyles, toolTipPopperStyles } from './styles';
import MuiTooltip, { TooltipClassKey, TooltipProps as MuiTooltipProps } from '@mui/material/Tooltip';
import { ClassNameMap } from '@mui/material';
import { cx } from '@emotion/css';

enum TooltipPlacements {
  TopStart = 'top-start',
  Top = 'top',
  TopEnd = 'top-end',
  RightStart = 'right-start',
  Right = 'right',
  RightEnd = 'right-end',
  BottomStart = 'bottom-start',
  Bottom = 'bottom',
  BottomEnd = 'bottom-end',
  LeftStart = 'left-start',
  Left = 'left',
  LeftEnd = 'left-end',
}

export interface TooltipProps extends Omit<MuiTooltipProps, 'className' | 'classes' | 'arrow' | 'placement'> {
  readonly className?: string;
  readonly classes?: Partial<ClassNameMap<TooltipClassKey>>;
  readonly placement?: TooltipPlacements;
}

const Tooltip: React.FunctionComponent<TooltipProps> = ({
  children,
  classes,
  className,
  placement = TooltipPlacements.Right,
  ...materialTooltipProps
}) => {
  const classNames = cx(className, toolTipPopperStyles(), classes?.popper);
  return (
    <MuiTooltip
      {...materialTooltipProps}
      arrow
      classes={{ popper: classNames, tooltip: toolTipStyles() }}
      placement={placement}
      data-testid={'toolTip'}
    >
      {children}
    </MuiTooltip>
  );
};

export { Tooltip, TooltipPlacements };
