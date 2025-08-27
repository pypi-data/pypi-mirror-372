import { JupyterFrontEnd, type JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IThemeManager } from '@jupyterlab/apputils';

/**
 * Initialization data for the @amzn/sagemaker-ui-theme-jlplugin extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: '@amzn/sagemaker-ui-theme-jlplugin:plugin',
  description: 'A JupyterLab extension.',
  autoStart: true,
  requires: [IThemeManager],
  activate: (app: JupyterFrontEnd, manager: IThemeManager) => {
    const style = '@amzn/sagemaker-ui-theme-jlplugin/index.css';

    console.log('sagemaker_dataenginnering_extensions- sagemaker-ui-theme - plugin activated!');

    manager.register({
      name: 'Amazon SageMaker Unified Studio Dark',
      isLight: false,
      load: () => manager.loadCSS(style),
      unload: () => Promise.resolve(undefined),
    });
  },
};

export default plugin;
