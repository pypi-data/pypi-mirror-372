import React from 'react';
import { SelectInputProps } from '../../components/selectinput';
interface SelectInputContainerProps extends SelectInputProps {
    required?: boolean;
    errorMessage?: string;
    toolTipText?: string;
    toolTipArea?: {
        descriptionText: string;
        toolTipComponent: React.ReactNode;
    };
}
declare const SelectInputContainer: React.FunctionComponent<SelectInputContainerProps>;
export { SelectInputContainer, SelectInputContainerProps };
//# sourceMappingURL=SelectInputContainer.d.ts.map