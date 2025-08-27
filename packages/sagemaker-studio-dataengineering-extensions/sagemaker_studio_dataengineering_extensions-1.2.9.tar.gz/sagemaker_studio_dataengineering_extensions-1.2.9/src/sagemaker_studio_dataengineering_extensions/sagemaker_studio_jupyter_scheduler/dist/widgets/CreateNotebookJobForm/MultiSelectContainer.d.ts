import React from 'react';
import { AutocompleteProps, AutocompleteRenderInputParams } from '@mui/material/Autocomplete';
interface MultiSelectContainerProps extends Omit<AutocompleteProps<string, true, boolean, boolean>, 'renderInput'> {
    name: string;
    className?: string;
    label: string;
    errorMessage?: string;
    required?: boolean;
    renderInput?: (params: AutocompleteRenderInputParams) => React.ReactNode;
    tooltip?: string;
    disabledTooltip?: string;
}
declare const MultiSelectContainer: React.FunctionComponent<MultiSelectContainerProps>;
export { MultiSelectContainer, MultiSelectContainerProps };
//# sourceMappingURL=MultiSelectContainer.d.ts.map