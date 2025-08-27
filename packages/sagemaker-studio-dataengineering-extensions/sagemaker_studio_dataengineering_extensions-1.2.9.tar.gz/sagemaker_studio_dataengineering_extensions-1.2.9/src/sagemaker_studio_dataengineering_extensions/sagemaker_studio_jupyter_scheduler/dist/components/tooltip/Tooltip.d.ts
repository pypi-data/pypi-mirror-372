import React from 'react';
import { TooltipClassKey, TooltipProps as MuiTooltipProps } from '@mui/material/Tooltip';
import { ClassNameMap } from '@mui/material';
declare enum TooltipPlacements {
    TopStart = "top-start",
    Top = "top",
    TopEnd = "top-end",
    RightStart = "right-start",
    Right = "right",
    RightEnd = "right-end",
    BottomStart = "bottom-start",
    Bottom = "bottom",
    BottomEnd = "bottom-end",
    LeftStart = "left-start",
    Left = "left",
    LeftEnd = "left-end"
}
export interface TooltipProps extends Omit<MuiTooltipProps, 'className' | 'classes' | 'arrow' | 'placement'> {
    readonly className?: string;
    readonly classes?: Partial<ClassNameMap<TooltipClassKey>>;
    readonly placement?: TooltipPlacements;
}
declare const Tooltip: React.FunctionComponent<TooltipProps>;
export { Tooltip, TooltipPlacements };
//# sourceMappingURL=Tooltip.d.ts.map