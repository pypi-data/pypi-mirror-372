import { Notification, ReactWidget } from '@jupyterlab/apputils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { Terminal } from '@jupyterlab/services';
import { Terminal as TerminalWidget } from '@jupyterlab/terminal';
import { LabIcon, UseSignal, errorIcon } from '@jupyterlab/ui-components';
import { ReadonlyJSONObject } from '@lumino/coreutils';
import { SplitPanel } from '@lumino/widgets';
import React from 'react';

import { createCommandPromise } from './CommandMonitor';
import { LibraryConfigListWidget } from './LibraryConfigList';
import { LibraryConfigPanelWidget } from './LibraryConfigPanel';
import { LIBRARY_CONFIG_SCHEMA } from './schema';

export class LibraryConfigEditor extends SplitPanel {
  private _config: ReadonlyJSONObject = {};
  private _context: DocumentRegistry.Context;
  private _updateSpace: boolean = false;
  private readonly _createTerminal: () => Promise<Terminal.ITerminalConnection>;
  private readonly _openTerminal: (terminal: TerminalWidget) => void;

  constructor(
    context: DocumentRegistry.Context,
    createTerminal: () => Promise<Terminal.ITerminalConnection>,
    openTerminal: (terminal: TerminalWidget) => void
  ) {
    super({
      orientation: 'horizontal',
      renderer: SplitPanel.defaultRenderer,
      spacing: 1,
    });
    this._context = context;
    this._createTerminal = createTerminal;
    this._openTerminal = openTerminal;
    this.onCheckUpdateSpace = this.onCheckUpdateSpace.bind(this);
    this.onChange = this.onChange.bind(this);
    this.onSave = this.onSave.bind(this);
    this._initialize()
      .then(() => {
        this.addClass('jp-SettingsPanel');
        const list = new LibraryConfigListWidget({
          schema: LIBRARY_CONFIG_SCHEMA,
          updateSpace: this._updateSpace,
          onCheckUpdateSpace: this.onCheckUpdateSpace,
          onSave: this.onSave,
        });
        list.handleSelectSourceSignal.connect(() => {
          this.update();
        });
        this.addWidget(list);
        const libManagementPanel = ReactWidget.create(
          <UseSignal signal={list.handleSelectSourceSignal}>
            {() => (
              <LibraryConfigPanelWidget
                schema={LIBRARY_CONFIG_SCHEMA}
                configs={this._config}
                handleSelectTypeSignal={list.handleSelectTypeSignal}
                handleSelectSourceSignal={list.handleSelectSourceSignal}
                onConfigsChange={this.onChange}
                setError={list.setError}
              />
            )}
          </UseSignal>
        );
        this.addWidget(libManagementPanel);
      })
      .catch(e => {
        this.addWidget(
          ReactWidget.create(
            <div className="jp-PluginList-entry-label">
              <LabIcon.resolveReact icon={errorIcon} iconClass={'jp-Icon'} tag="span" stylesheet="settingsEditor" />
              <span style={{ color: 'var(--jp-error-color0)' }} className="jp-PluginList-entry-label-text">
                The file {this._context.path} is corrupted, please remove or fix the file and reopen the UI again.
              </span>
            </div>
          )
        );
      });
  }

  onCheckUpdateSpace(updateSpace: boolean) {
    this._updateSpace = updateSpace;
    const newConfigs = JSON.parse(JSON.stringify(this._config));
    newConfigs['ApplyChangeToSpace'] = updateSpace;
    this._context.model.fromJSON(newConfigs);
  }

  onChange(configs: ReadonlyJSONObject) {
    this._context.model.fromJSON(configs);
    this._config = configs;
    this.update();
  }

  async onSave() {
    await this._context.save();
    Notification.success('Saving completed. Restart the spark compute to apply the new library configuration.', {
      autoClose: 5000,
    });

    // install conda lib and pip lib if any of them are selected
    if (this._updateSpace && this._config['Python']) {
      let commands: string[] = [];
      const pythonConfig = this._config['Python'] as ReadonlyJSONObject;
      if (pythonConfig['CondaPackages']) {
        const condaConfig = pythonConfig['CondaPackages'] as ReadonlyJSONObject;
        const packages = condaConfig['PackageSpecs'] as string[];
        const channels = condaConfig['Channels'] as string[];
        if (packages.length > 0) {
          commands.push(
            `micromamba install --freeze-installed -y ${
              channels.map(channel => `-c "${channel}"`).join(' ')} ${
              packages.map(p => `"${p}"`).join(' ')}`
          );
        }
      }
      if (commands.length > 0) {
        const terminal = await this._createTerminal();
        const terminalWidget = new TerminalWidget(terminal);
        terminalWidget.id = 'installLab' + new Date().getMilliseconds();
        terminalWidget.title.closable = true;
        Notification.promise(createCommandPromise(terminal, commands), {
          pending: {
            message: `Updating python environment for JupyterLab compute...`,
            options: {
              actions: [
                {
                  label: 'View in terminal',
                  callback: () => {
                    if (terminal.isDisposed) {
                      Notification.error('Terminal is disposed');
                    } else {
                      this._openTerminal(terminalWidget);
                    }
                  },
                },
              ],
              autoClose: false,
            },
          },
          success: {
            message: () => `Update completed. Restart the kernel to ensure you are using the updated libraries.`,
            options: { actions: [], autoClose: 5000 },
          },
          error: {
            message: () => 'Failed to update python libraries for JupyterLab compute. Check error logs in terminal.',
          },
        });
      }
    }
  }

  private async _initialize() {
    await this._context.ready;

    this._context.model.contentChanged.connect(this.onContentChange, this);
    this._config = this._context.model.toJSON() as ReadonlyJSONObject;
    this._updateSpace = (this._config['ApplyChangeToSpace'] as boolean) ?? false;
  }

  private onContentChange() {
    this._config = this._context.model.toJSON() as ReadonlyJSONObject;
  }
}
