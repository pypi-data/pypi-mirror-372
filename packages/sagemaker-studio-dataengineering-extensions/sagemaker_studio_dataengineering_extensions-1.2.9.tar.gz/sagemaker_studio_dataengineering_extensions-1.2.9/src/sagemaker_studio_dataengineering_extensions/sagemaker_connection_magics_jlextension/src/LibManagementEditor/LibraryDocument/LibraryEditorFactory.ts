import { ABCWidgetFactory, DocumentRegistry } from '@jupyterlab/docregistry';
import { Terminal } from '@jupyterlab/services';
import { Terminal as TerminalWidget } from '@jupyterlab/terminal';

import { LibraryDocumentWidget } from './LibraryDocumentWidget';

export class LibraryEditorFactory extends ABCWidgetFactory<LibraryDocumentWidget> {
  private readonly _createTerminal: () => Promise<Terminal.ITerminalConnection>;
  private readonly _openTerminal: (terminal: TerminalWidget) => void;

  constructor(
    options: DocumentRegistry.IWidgetFactoryOptions<LibraryDocumentWidget>,
    createTerminal: () => Promise<Terminal.ITerminalConnection>,
    openTerminal: (terminal: TerminalWidget) => void
  ) {
    super(options);
    this._createTerminal = createTerminal;
    this._openTerminal = openTerminal;
  }

  protected createNewWidget(context: DocumentRegistry.Context) {
    return new LibraryDocumentWidget(context, this._createTerminal, this._openTerminal);
  }
}
