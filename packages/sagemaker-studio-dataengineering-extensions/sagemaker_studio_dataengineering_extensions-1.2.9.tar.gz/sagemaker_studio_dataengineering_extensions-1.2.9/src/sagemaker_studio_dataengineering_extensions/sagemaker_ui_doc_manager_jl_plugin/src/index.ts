import {
  JupyterFrontEnd,
  type JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { shouldOpenFile, shouldOpenOrCreateFile, shouldOpenUntitledFile } from './handler';
import { NB_COMMANDS } from './constants';
import type { DocManagerFileEvent } from './models';
import { Contents } from '@jupyterlab/services';

const id = '@amzn/sagemaker-ui-doc-manager-jl-plugin:plugin';
const description = 'A JupyterLab extension for handling notebook documents.';


const fileExists = async (app: JupyterFrontEnd, path:string)=>{
  //code based on other examples: https://code.amazon.com/search?term=filepath%3A*.ts%2C*.tsx%2C%21*.test.*%2C%21*.spec.*+%22serviceManager.contents.get%22+%22%40jupyterlab%22
  //however, I could not find the error type, so we're casting to keep TS happy
  try {
    await app.serviceManager.contents.get(path,{content:false});
    return true;
  } catch (e){
    const error = e as {response?:{status?:number}};
    if(error?.response?.status === 404){
      return false;
    }
    throw e;
  }}

/**
 * Initialization for the sagemaker-ui-doc-manager-jl-plugin extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id,
  description,
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('sagemaker-ui-doc-manager-jl-plugin is activated!');

    window.addEventListener('message', async e => {
      const event = e.data as DocManagerFileEvent;
      if (shouldOpenFile(e)) {
        await app.commands.execute(NB_COMMANDS.OpenFileCommand, { path: event.payload.path });
        await app.commands.execute(NB_COMMANDS.ShowFileInBrowser);
      }
      if (shouldOpenUntitledFile(e)) {
          const { type, ext, path, content, format } = event.payload
          await app.serviceManager.contents.newUntitled({ type, ext, path }).then(async (model: Contents.IModel) => {
            if (content) {
              await app.serviceManager.contents.save(model.path, { type: model.type, content, format: format || 'text' })
            }
            await app.commands.execute(NB_COMMANDS.OpenFileCommand, { path: model.path });
            await app.commands.execute(NB_COMMANDS.ShowFileInBrowser);
          })
      }
      else if(shouldOpenOrCreateFile(e)){
        const { type,  path, content, format } = event.payload;

        if(!content){
          console.error("Missing content", e);
          return ;
        }

        if(!path){
          console.error("Missing path", e);
          return ;
        }
        
        try{
          if(!(await fileExists(app,path))){
            await app.serviceManager.contents.save(path, { type: type, content, format: format || 'text' });
          }
        }
        catch(e){
          console.error("Unable to check if file exists", e);
          return;
        }
        await app.commands.execute(NB_COMMANDS.OpenFileCommand, { path: path });
        await app.commands.execute(NB_COMMANDS.ShowFileInBrowser);
      }
    });
  }
};

export default plugin;
