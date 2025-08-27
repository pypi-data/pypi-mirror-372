import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ICompletionProviderManager, ICompletionContext, ICompletionProvider } from '@jupyterlab/completer';
import { Constants } from '../constants';

/**
 * LSP provider identifier
 */
const LSP_PROVIDER_ID = 'lsp';

/**
 * Plugin that disables LSP completions only when the cursor is right after "%%sql "
 */
export const sqlCompletionControlPlugin: JupyterFrontEndPlugin<void> = {
  id: '@amzn/sagemaker-connection-magics-jlextension:sql-completion-control',
  requires: [ICompletionProviderManager],
  autoStart: true,
  activate: (app: JupyterFrontEnd, completionManager: ICompletionProviderManager) => {
    app.started.then(() => {
      try {
        const providers = getProviders(completionManager);
        const lspProvider = providers.find(p => p?.identifier === LSP_PROVIDER_ID);
        
        if (!lspProvider || typeof lspProvider.isApplicable !== 'function') {
          console.warn('Sql Completion Control: LSP provider not found or invalid');
          return;
        }
        
        patchLspProvider(lspProvider);
        console.log('Sql Completion Control: Successfully monkey-patched LSP provider');
      } catch (error) {
        console.error('Sql Completion Control: Failed to initialize plugin:', error);
      }
    });
  }
};

/**
 * Extracts providers from the completion manager's internal structure.
 * Handles different internal representations across JupyterLab versions:
 * - Map: JupyterLab 4.x
 * - Array: JupyterLab 3.x legacy
 * - Object: Fallback for other versions
 */
function getProviders(completionManager: ICompletionProviderManager): any[] {
  const providersMap = (completionManager as any)._providers;
  
  // Add runtime validation after type assertion
  if (!providersMap) {
    console.warn('Sql Completion Control: Unable to access completion providers');
    return [];
  }
  
  if (providersMap instanceof Map) return Array.from(providersMap.values());
  if (Array.isArray(providersMap)) return providersMap;
  if (providersMap && typeof providersMap === 'object') return Object.values(providersMap);
  
  return [];
}

function patchLspProvider(lspProvider: ICompletionProvider): void {
  const originalIsApplicable = lspProvider.isApplicable.bind(lspProvider);
  
  lspProvider.isApplicable = async (context: ICompletionContext) => {
    let originalResult = false;
    
    try {
      originalResult = await originalIsApplicable(context);
      if (!originalResult) return false;
      
      const editor = context.editor;
      if (!editor?.model) return originalResult;
      
      const text = getEditorText(editor);
      if (!text) return originalResult;
      
      // Get first line more efficiently
      const firstLine = getFirstLine(text);
      if (!firstLine.startsWith(Constants.CONNECT_SQL_CELL_MAGIC_ALIAS)) {
        return originalResult;
      }
      
      const position = editor.getCursorPosition();
      // Disable completions for the entire first line when it starts with %%sql
      if (position.line === 0) {
        return false;
      }
      
      return originalResult;
    } catch {
      return originalResult;
    }
  };
}

/**
 * Efficiently extracts the first line from text without processing the entire document
 */
function getFirstLine(text: string): string {
  const newlineIndex = text.indexOf('\n');
  return newlineIndex !== -1 ? text.substring(0, newlineIndex) : text;
}

/**
 * Extracts text content from editor with multiple fallback methods for compatibility
 * across different JupyterLab versions and editor implementations
 */
function getEditorText(editor: any): string {
  try {
    const model = editor.model;
    
    if (model.sharedModel?.getSource) return model.sharedModel.getSource();
    if (model.value?.text) return model.value.text;
    if (model.toString) return model.toString();
    
    const editorValue = editor.getOption?.('value');
    return typeof editorValue === 'string' ? editorValue : '';
  } catch (error) {
    console.warn('Sql Completion Control: Error accessing editor text:', error);
    return '';
  }
}
