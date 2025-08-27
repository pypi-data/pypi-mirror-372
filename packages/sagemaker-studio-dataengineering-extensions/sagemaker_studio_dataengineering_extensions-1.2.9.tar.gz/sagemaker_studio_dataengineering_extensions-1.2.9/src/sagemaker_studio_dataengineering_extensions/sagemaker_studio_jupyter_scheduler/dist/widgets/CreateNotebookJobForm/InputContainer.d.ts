import React from 'react';
import { TextInputProps } from '../../components/textinput';
interface InputContainerProps extends TextInputProps {
    labelInfo: string;
    required?: boolean;
    errorMessage?: string;
    toolTipText?: string;
    readOnly?: boolean;
}
declare const InputContainer: React.FunctionComponent<InputContainerProps>;
export { InputContainer };
//# sourceMappingURL=InputContainer.d.ts.map