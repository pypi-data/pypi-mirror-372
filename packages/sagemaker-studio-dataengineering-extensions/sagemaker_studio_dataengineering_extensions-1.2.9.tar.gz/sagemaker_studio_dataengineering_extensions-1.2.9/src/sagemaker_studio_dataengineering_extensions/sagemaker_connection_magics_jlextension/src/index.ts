import { connectionDropdownPlugin } from './ConnectionDropdownWidget';
import { codeMirrorPlugin } from './ConnectionMagicFormat';
import { sqlCompletionControlPlugin } from './ConnectionMagicFormat/SqlCompletionControlPlugin';
import { libManagementPlugin } from './LibManagementEditor';
import { newCellMagicLineHandler } from './NewCellMagicLineHandler';
import { sqlQuerybookEditor } from './SqlQuerybookEditor';
import { visualEtlFileEditor } from './VisualEtlFileEditor';
import { sagemakerDisplayMimeRender } from "./DataVisualizationRender";
import { invokeAgenticQPlugin } from "./InvokeAgenticQ";

export default [
  connectionDropdownPlugin,
  newCellMagicLineHandler,
  codeMirrorPlugin,
  sqlCompletionControlPlugin,
  libManagementPlugin,
  sqlQuerybookEditor,
  visualEtlFileEditor,
  sagemakerDisplayMimeRender,
  invokeAgenticQPlugin
];
