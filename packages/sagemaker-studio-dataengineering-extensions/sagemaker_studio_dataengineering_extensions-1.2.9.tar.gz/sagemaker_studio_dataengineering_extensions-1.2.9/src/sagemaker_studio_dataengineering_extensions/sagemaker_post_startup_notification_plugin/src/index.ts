import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ILauncher } from '@jupyterlab/launcher';
import { PostStartupNotificationsService } from './services/PostStartupNotificationService';
/**
 * Initialization data for the sagemaker_post_startup_notification_plugin extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: '@amzn/sagemaker-post-startup-notification-plugin:plugin',
  description: 'A JupyterLab extension.',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('JupyterLab extension sagemaker-post-startup-notification-plugin is activated!');
    app.restored.then(async () => {
      const service = new PostStartupNotificationsService();
      await service.initialize();
    });
  }
};

const terminalWithQ = 'Terminal with Q';
/**
 * Custom Terminal Launcher Plugin - Modifies Terminal launcher card text
 */
const customTerminalLauncherPlugin: JupyterFrontEndPlugin<void> = {
  id: '@amzn/sagemaker-post-startup-notification-plugin:custom-terminal-launcher-plugin',
  autoStart: true,
  requires: [ILauncher],
  activate: (app: JupyterFrontEnd, launcher: ILauncher) => {
    const updateTerminalText = (): void => {
      try {
        const terminalLabels = document.querySelectorAll<HTMLParagraphElement>('.jp-LauncherCard-label[title="Start a new terminal session"] p');
        if (terminalLabels.length > 0) {
          terminalLabels.forEach(label => {
            if (label.innerHTML !== terminalWithQ) {
              label.innerHTML = terminalWithQ;
            }
          });
        }
      } catch (error) {
        // Silently handle errors
      }
    };
    // Set up observation for terminal elements
    const observeForTerminal = (): void => {
      // Run immediately once
      updateTerminalText();
      // Set up a MutationObserver to watch for DOM changes

      // Function to check if we should update based on mutations
      const shouldUpdateFromMutations = (mutations: MutationRecord[]): boolean => {
        for (const mutation of mutations) {
          // Check if any nodes were added
          if (mutation.addedNodes.length > 0) {
            return true;
          }
          
          // Check if attributes were modified on relevant elements
          if (mutation.type === 'attributes') {
            const mutationTarget = mutation.target as Element;
            if (mutationTarget.classList?.contains('jp-Launcher') || 
                mutationTarget.classList?.contains('jp-LauncherCard')) {
              return true;
            }
          }
        }
        return false;
      };
      
      const observer = new MutationObserver((mutations) => {
        if (shouldUpdateFromMutations(mutations)) {
          updateTerminalText();
        }
      });
      // Observe the main content area instead of the entire body
      const mainArea = document.querySelector('#jp-main-dock-panel') || document.body;
      observer.observe(mainArea, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['title'] // Only care about title attribute changes
      });

    };
    console.log('JupyterLab extension sagemaker-post-startup-notification-custom-terminal-launcher-plugin is running');
    // Wait for the app to be restored and then start observing
    app.restored.then(() => {
      // Use a delay to ensure the launcher is fully loaded
      setTimeout(observeForTerminal, 2000);
    });
  }
};
export default [plugin, customTerminalLauncherPlugin];