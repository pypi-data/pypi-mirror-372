import { DocumentManager } from '@jupyterlab/docmanager';
import { Contents } from '@jupyterlab/services';

import { initConfig } from '../config';

export class LibManagementDocumentManager extends DocumentManager {
  constructor(options: DocumentManager.IOptions) {
    super(options);
    this.autosave = false;
  }

  async exist(path: string) {
    try {
      await this.services.contents.get(path);
      return true;
    } catch (err) {
      // @ts-ignore
      if (err.response && err.response.status === 404) {
        return false;
      } else {
        throw err;
      }
    }
  }

  async openOrCreate(path: string, widgetName = 'default') {
    try {
      await this.services.contents.get(path);
    } catch (err) {
      // @ts-ignore
      if (err.response && err.response.status === 404) {
        // file doesn't exist
        const currentTimestamp = new Date().toISOString();
        const model: Contents.IModel = {
          created: currentTimestamp,
          last_modified: currentTimestamp,
          mimetype: 'application/json',
          writable: true,
          type: 'file',
          format: 'text',
          name: path.split('/').pop() ?? '.lib.json',
          path,
          content: JSON.stringify(initConfig),
        };
        await this.services.contents.save(path, model);
      } else {
        throw err;
      }
    }

    return super.openOrReveal(path, widgetName);
  }
}
