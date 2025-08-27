import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { nullTranslator } from '@jupyterlab/translation';
import { notebookIcon } from '@jupyterlab/ui-components';

export const visualEtlFileEditor: JupyterFrontEndPlugin<void> = {
  id: '@amzn/sagemaker-connection-magics-jlextension:visual-etl-file-editor',
  autoStart: true,
  optional: [],
  activate: (app: JupyterFrontEnd) => {
    const { docRegistry } = app;
    // TODO add translator
    const translator = nullTranslator;
    const trans = translator?.load('jupyterlab');

    // Create new file type refer to https://github.com/jupyterlab/jupyterlab/blob/c7426e494067765bb314c5ff3bd7c052913c5674/packages/docregistry/src/registry.ts#L1346-L1362
    const vetl: DocumentRegistry.IFileType = {
      name: 'vetl',
      displayName: trans.__('Visual Editor file'),
      mimeTypes: ['application/x-vetl+json'],
      extensions: ['.vetl'],
      contentType: 'notebook',
      fileFormat: 'json',
      // TODO check with UX designer
      icon: notebookIcon,
    };

    // Registry new file type to notebook factory
    // https://github.com/jupyterlab/jupyterlab/blob/c7426e494067765bb314c5ff3bd7c052913c5674/packages/notebook-extension/src/index.ts#L340
    docRegistry.addFileType(vetl, ['Notebook']);
  },
};
