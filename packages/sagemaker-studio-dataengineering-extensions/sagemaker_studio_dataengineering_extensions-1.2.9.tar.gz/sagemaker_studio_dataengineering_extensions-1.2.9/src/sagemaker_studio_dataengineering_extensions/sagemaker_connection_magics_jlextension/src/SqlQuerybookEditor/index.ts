import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { nullTranslator } from '@jupyterlab/translation';
import { notebookIcon } from '@jupyterlab/ui-components';

export const sqlQuerybookEditor: JupyterFrontEndPlugin<void> = {
  id: '@amzn/sagemaker-connection-magics-jlextension:sql-querybook-editor',
  autoStart: true,
  optional: [],
  activate: (app: JupyterFrontEnd) => {
    const { docRegistry } = app;
    // TODO add translator
    const translator = nullTranslator;
    const trans = translator?.load('jupyterlab');

    // Create new file type refer to https://github.com/jupyterlab/jupyterlab/blob/c7426e494067765bb314c5ff3bd7c052913c5674/packages/docregistry/src/registry.ts#L1346-L1362
    const sqlnb: DocumentRegistry.IFileType = {
      name: 'sqlnb',
      displayName: trans.__('SQL querybook'),
      mimeTypes: ['application/x-sqlnb+json'],
      extensions: ['.sqlnb'],
      contentType: 'notebook',
      fileFormat: 'json',
      // TODO check with UX designer
      icon: notebookIcon,
    };

    // Registry new file type to notebook factory
    // https://github.com/jupyterlab/jupyterlab/blob/c7426e494067765bb314c5ff3bd7c052913c5674/packages/notebook-extension/src/index.ts#L340
    docRegistry.addFileType(sqlnb, ['Notebook']);
  },
};
