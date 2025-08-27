import { python } from '@codemirror/lang-python';
import { sql } from '@codemirror/lang-sql';
import { StreamLanguage } from '@codemirror/language';
import { scala } from '@codemirror/legacy-modes/mode/clike';
import { Compartment, Extension, Facet, RangeSetBuilder } from '@codemirror/state';
import { EditorSelection, EditorState, Transaction } from '@codemirror/state';
import { Decoration, DecorationSet, EditorView, ViewPlugin, ViewUpdate, WidgetType } from '@codemirror/view';
import { CodeMirrorEditor } from '@jupyterlab/codemirror';
import { Notebook } from '@jupyterlab/notebook';

import { Constants } from '../constants';
import {getCellLanguageName, isCellStartWithSupportedMagics} from '../utils/DropdownUtils';

const displayTheme = EditorView.baseTheme({
  '&light .cm-readonly-connect-magic': {
    color: 'grey',
    display: '',
  },
  '&dark .cm-readonly-connect-magic': {
    color: 'grey',
    display: '',
  },
});

const hideTheme = EditorView.baseTheme({
  '&light .cm-hide-connect-magic': {
    color: 'grey',
    display: 'none',
  },
  '&dark .cm-hide-connect-magic': {
    color: 'grey',
    display: 'none',
  },
});

const toDisplay = Facet.define<boolean, boolean>({
  combine: values => (values.length ? values[0] : false),
});

const toEdit = Facet.define<boolean, boolean>({
  combine: values => (values.length ? values[0] : false),
});

class MagicLineWidget extends WidgetType {
  toDOM(view: EditorView) {
    let value = document.createElement('span');
    value.textContent = view.state.doc.lineAt(0).text;
    return value;
  }
}

// Add decoration to editor lines
const readOnlyDecoration = Decoration.line({
  class: 'cm-readonly-connect-magic',
  inclusive: true,
});

const hideDecoration = Decoration.line({
  class: 'cm-hide-connect-magic',
  inclusive: true,
});

const magicLineDecoration = Decoration.replace({
  widget: new MagicLineWidget(),
});

export function modifyFirstLineFormat(view: EditorView) {
  const display = view.state.facet(toDisplay) as boolean;
  const edit = view.state.facet(toEdit) as boolean;
  const builder = new RangeSetBuilder<Decoration>();
  if (view.state.doc.lines > 1 && isCellStartWithSupportedMagics(view.state.doc.lineAt(0).text)) {
    if (display && !edit) {
      builder.add(0, 0, readOnlyDecoration);
      builder.add(0, view.state.doc.lineAt(0).length, magicLineDecoration);
    } else if (!display) {
      builder.add(0, 0, hideDecoration);
    }
  }
  return builder.finish();
}

export const compartment = new Compartment();

export function SageMakerConnectMagicExtension(options: Record<string, boolean>): Extension {
  return [
    compartment.of([smartSelect, formatFirstLine]),
    displayTheme,
    hideTheme,
    toDisplay.of(options.toDisplay),
    toEdit.of(options.toEdit),
  ];
}

export const formatFirstLine = ViewPlugin.fromClass(
  class {
    decorations: DecorationSet;
    constructor(view: EditorView) {
      this.decorations = modifyFirstLineFormat(view);
    }

    update(update: ViewUpdate) {
      const oldToDisplay = update.startState.facet(toDisplay);
      const oldToEdit = update.startState.facet(toEdit);
      if (
        update.docChanged ||
        update.viewportChanged ||
        oldToDisplay !== update.view.state.facet(toDisplay) ||
        oldToEdit != update.view.state.facet(toEdit)
      ) {
        this.decorations = modifyFirstLineFormat(update.view);
      }
    }
  },
  {
    decorations: v => v.decorations,
  }
);

export const smartSelect = EditorState.transactionFilter.of((tr: Transaction) => {
  const display = tr.state.facet(toDisplay);
  const edit = tr.state.facet(toEdit);
  const sel = tr.newSelection;
  if (
    (display && edit) ||
    !isCellStartWithSupportedMagics(tr.state.doc.sliceString(0, 15)) ||
    tr.startState.doc.lines <= 1
  ) {
    return tr;
  }

  const allowedFrom = tr.startState.doc.line(1).to + 1;
  // allowed to the end of the doc
  const allowedTo = tr.newDoc.length - tr.newDoc.line(1).length + tr.startState.doc.line(1).length;

  if (!sel.ranges.some(({ from, to }) => from < allowedFrom || to > allowedTo)) {
    return tr;
  }
  const clip = (n: number) => Math.min(Math.max(n, allowedFrom), allowedTo);
  let newSelection = sel.ranges;

  //filter out deletion
  if (tr.isUserEvent('delete')) {
    newSelection = newSelection
      .map(r => EditorSelection.range(r.anchor, r.head))
      .filter(range => {
        // filter out any selection range which are totally within the first line
        return range.to > tr.startState.doc.line(1).to;
      });
  }
  // reset the new range and filter out any selection that is out of the range
  newSelection = newSelection
    .map(r => EditorSelection.range(clip(r.anchor), clip(r.head)))
    .filter(range => {
      return range.from >= allowedFrom && range.to <= allowedTo;
    });
  if (newSelection.length === 0) return [];
  return [tr, { selection: EditorSelection.create(newSelection, sel.mainIndex) }];
});

export async function updateSageMakerCodeMirrorExtensionForNotebook(notebook: Notebook, kernelName: string | undefined) {
  const cells = notebook.widgets;
  let compartmentExtensions: Extension = [];
  for (const cell of cells) {
    await cell.ready;
    if (
      cell &&
      cell.model &&
      cell.model.type === 'code' &&
      kernelName === Constants.SAGEMAKER_MAGIC_SUPPORTED_KERNEL_NAME
    ) {
      const cellLanguageName = getCellLanguageName(cell);
      if (cellLanguageName === Constants.LANGUAGE_SQL) {
        compartmentExtensions = [smartSelect, formatFirstLine, sql()];
      } else if (cellLanguageName === Constants.LANGUAGE_SCALA) {
        compartmentExtensions = [smartSelect, formatFirstLine, StreamLanguage.define(scala)];
      } else {
        compartmentExtensions = [smartSelect, formatFirstLine, python()];
      }
    } else {
      compartmentExtensions = [python()];
    }
    const editor = cell.editor as CodeMirrorEditor;
    if (editor && editor.editor) {
      editor.editor.dispatch({ effects: compartment.reconfigure(compartmentExtensions) });
    }
  }
}
