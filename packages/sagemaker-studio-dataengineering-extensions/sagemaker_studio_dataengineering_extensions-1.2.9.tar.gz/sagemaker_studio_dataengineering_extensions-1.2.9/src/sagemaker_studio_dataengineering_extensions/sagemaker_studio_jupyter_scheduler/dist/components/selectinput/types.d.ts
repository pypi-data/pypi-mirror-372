/// <reference types="react" />
import { AutocompleteProps, AutocompleteRenderInputParams } from '@mui/material';
interface DropdownItem {
    readonly label: string;
    readonly value: string;
    readonly isDisabled?: boolean;
    readonly labelMetadata?: {
        [key: string]: React.ReactNode;
    };
    readonly optionMetadata?: {
        [key: string]: any;
    };
    readonly options?: DropdownItem[];
    readonly group?: string;
}
type CustomListItemRender = (option: DropdownItem, label: string | JSX.Element, selected?: boolean) => JSX.Element;
interface SelectInputProps extends Omit<AutocompleteProps<DropdownItem, false, boolean, boolean>, 'renderInput' | 'onChange'> {
    label: string;
    onChange?: (item: DropdownItem | string) => void;
    renderInput?: (params: AutocompleteRenderInputParams) => React.ReactNode;
    customListItemRender?: CustomListItemRender;
}
export { DropdownItem, CustomListItemRender, SelectInputProps };
//# sourceMappingURL=types.d.ts.map