import React from 'react';
import { toolTipStyles, toolTipPopperStyles } from './styles';
import MuiTooltip from '@mui/material/Tooltip';
import { cx } from '@emotion/css';
var TooltipPlacements;
(function (TooltipPlacements) {
    TooltipPlacements["TopStart"] = "top-start";
    TooltipPlacements["Top"] = "top";
    TooltipPlacements["TopEnd"] = "top-end";
    TooltipPlacements["RightStart"] = "right-start";
    TooltipPlacements["Right"] = "right";
    TooltipPlacements["RightEnd"] = "right-end";
    TooltipPlacements["BottomStart"] = "bottom-start";
    TooltipPlacements["Bottom"] = "bottom";
    TooltipPlacements["BottomEnd"] = "bottom-end";
    TooltipPlacements["LeftStart"] = "left-start";
    TooltipPlacements["Left"] = "left";
    TooltipPlacements["LeftEnd"] = "left-end";
})(TooltipPlacements || (TooltipPlacements = {}));
const Tooltip = ({ children, classes, className, placement = TooltipPlacements.Right, ...materialTooltipProps }) => {
    const classNames = cx(className, toolTipPopperStyles(), classes === null || classes === void 0 ? void 0 : classes.popper);
    return (React.createElement(MuiTooltip, { ...materialTooltipProps, arrow: true, classes: { popper: classNames, tooltip: toolTipStyles() }, placement: placement, "data-testid": 'toolTip' }, children));
};
export { Tooltip, TooltipPlacements };
//# sourceMappingURL=Tooltip.js.map