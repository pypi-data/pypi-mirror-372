import { DocumentRegistry, DocumentWidget } from '@jupyterlab/docregistry';
import { Terminal } from '@jupyterlab/services';
import { Terminal as TerminalWidget } from '@jupyterlab/terminal';

import { LibraryConfigEditor } from '../LibraryConfigEditor';
import { libMgmtIcon } from '../config';

export class LibraryDocumentWidget extends DocumentWidget<LibraryConfigEditor> {
  constructor(
    context: DocumentRegistry.Context,
    createTerminal: () => Promise<Terminal.ITerminalConnection>,
    openTerminal: (terminal: TerminalWidget) => void
  ) {
    const content = new LibraryConfigEditor(context, createTerminal, openTerminal);
    super({ content, context });
    this.title.icon = libMgmtIcon;
  }
}
