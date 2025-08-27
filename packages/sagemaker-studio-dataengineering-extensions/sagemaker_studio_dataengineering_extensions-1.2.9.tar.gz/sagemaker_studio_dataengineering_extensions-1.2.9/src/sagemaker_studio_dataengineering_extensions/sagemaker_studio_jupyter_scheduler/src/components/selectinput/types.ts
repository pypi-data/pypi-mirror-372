import { AutocompleteProps, AutocompleteRenderInputParams } from '@mui/material';

interface DropdownItem {
  readonly label: string;
  readonly value: string;
  readonly isDisabled?: boolean;
  readonly labelMetadata?: { [key: string]: React.ReactNode }; // metadata that helps construct complex option label
  readonly optionMetadata?: { [key: string]: any }; // any metadata for the option
  readonly options?: DropdownItem[];
  readonly group?: string;
}

type CustomListItemRender = (option: DropdownItem, label: string | JSX.Element, selected?: boolean) => JSX.Element;

interface SelectInputProps
  extends Omit<AutocompleteProps<DropdownItem, false, boolean, boolean>, 'renderInput' | 'onChange'> {
  label: string;
  onChange?: (item: DropdownItem | string) => void;
  renderInput?: (params: AutocompleteRenderInputParams) => React.ReactNode;
  customListItemRender?: CustomListItemRender;
}

export { DropdownItem, CustomListItemRender, SelectInputProps };
