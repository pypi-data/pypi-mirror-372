import { Button, LabIcon, ReactWidget, errorIcon } from '@jupyterlab/ui-components';
import { ISignal, Signal } from '@lumino/signaling';
import { JSONSchema7 } from 'json-schema';
import React, { ChangeEvent } from 'react';

import {CONFIGS} from './config';

export class LibraryConfigListWidget extends ReactWidget {
  private _selectedType = 'Jar';
  private _selectedSource = 'MavenArtifacts';
  private _updateSpace: boolean;
  private _onCheckUpdateSpace: (updateSpace: boolean) => void;
  private _onSave: () => Promise<void>;
  private _schema: JSONSchema7;
  private _handleSelectTypeSignal = new Signal<this, string>(this);
  private _handleSelectSourceSignal = new Signal<this, string>(this);
  private _errors: { [type: string]: { [source: string]: boolean } };

  constructor(options: LibraryConfigListWidget.IOptions) {
    super();
    this.addClass('jp-PluginList');
    this._updateSpace = options.updateSpace;
    this._onCheckUpdateSpace = (updateSpace: boolean) => {
      this._updateSpace = updateSpace;
      options.onCheckUpdateSpace(updateSpace);
      this.update();
    };
    this._onSave = options.onSave;
    this._schema = options.schema;
    this._evtMousedown = this._evtMousedown.bind(this);
    this._onSave = this._onSave.bind(this);
    this.setError = this.setError.bind(this);
    this._errors = {};
  }

  get handleSelectTypeSignal(): ISignal<this, string> {
    return this._handleSelectTypeSignal;
  }

  get handleSelectSourceSignal(): ISignal<this, string> {
    return this._handleSelectSourceSignal;
  }

  mapConfig(type: string, source: string, schema: JSONSchema7): JSX.Element {
    const title = schema.title;
    const configMetadata = CONFIGS[type][source];
    return (
      <div
        onClick={this._evtMousedown}
        className={`${
          type === this._selectedType && source === this._selectedSource
            ? 'jp-mod-selected jp-PluginList-entry'
            : 'jp-PluginList-entry'
        } ${this.hasError(type, source) ? 'jp-ErrorPlugin' : ''}`}
        selected-type={type}
        selected-source={source}
      >
        <div className="jp-PluginList-entry-label" role="tab">
          <div className="jp-SelectedIndicator" />
          <LabIcon.resolveReact icon={configMetadata.icon} iconClass={'jp-Icon'} tag="span" stylesheet="settingsEditor" />
          <span className="jp-PluginList-entry-label-text">{title}</span>
        </div>
      </div>
    );
  }

  protected render() {
    let configs: JSX.Element[] = [];
    if (this._schema.properties) {
      const properties = this._schema.properties;
      configs = Object.keys(properties).map(typeKey => {
        const sourceConfig = (properties[typeKey] as JSONSchema7).properties;
        const sourceList = sourceConfig
          ? Object.keys(sourceConfig).map(sourceKey =>
              this.mapConfig(typeKey, sourceKey, sourceConfig[sourceKey] as JSONSchema7)
            )
          : [];
        return (
          <div>
            <h1 className="jp-PluginList-header">{typeKey}</h1>
            <ul>{sourceList}</ul>
          </div>
        );
      });
    }
    return (
      <div className="jp-PluginList-wrapper">
        <div className="jp-SettingsHeader">
          <h3>{'Library Management'}</h3>
        </div>
        {configs}
        <div className="jp-PluginList-entry" style={{ paddingTop: '8px', marginTop: '10px' }}>
          <div className="jp-PluginList-entry">
            <div className="jp-PluginList-entry-label">
              <input
                type="checkbox"
                className="jp-mod-styled jp-pluginmanager-Disclaimer-checkbox"
                checked={this._updateSpace}
                onChange={(event: ChangeEvent<HTMLInputElement>) => this._onCheckUpdateSpace(event.target.checked)}
              />
              <span>Apply the change to JupyterLab</span>
            </div>
          </div>
          <div className="jp-PluginList-entry">
            <Button className="jp-mod-styled jp-mod-reject jp-ArrayOperationsButton" onClick={() => this.onSave()}>
              Save all changes
            </Button>
          </div>
          {this.hasErrors && (
            <div className="jp-PluginList-entry">
              <div className="jp-PluginList-entry-label">
                <LabIcon.resolveReact icon={errorIcon} iconClass={'jp-Icon'} tag="span" stylesheet="settingsEditor" />
                <span style={{ color: 'var(--jp-error-color0)' }} className="jp-PluginList-entry-label-text">
                  You must resolve all errors to save
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  private _evtMousedown(event: React.MouseEvent<HTMLDivElement>): void {
    const target = event.currentTarget;
    const type = target.getAttribute('selected-type');
    const source = target.getAttribute('selected-source');

    if (!type || !source) {
      return;
    }

    this._selectedType = type;
    this._handleSelectTypeSignal.emit(type);
    this._selectedSource = source;
    this._handleSelectSourceSignal.emit(source);
    this.update();
  }

  private async onSave(): Promise<void> {
    if (this.hasErrors) {
      this.update();
    } else {
      await this._onSave();
    }
  }

  private hasError(type: string, source: string): boolean {
    return this._errors[type] ? this._errors[type][source] : false;
  }

  get hasErrors(): boolean {
    for (const type in this._errors) {
      for (const source in this._errors[type]) {
        if (this._errors[type][source]) {
          return true;
        }
      }
    }
    return false;
  }

  setError(type: string, source: string, error: boolean) {
    if (!this._errors[type]) {
      this._errors[type] = {};
    }
    if (this._errors[type][source] !== error) {
      this._errors[type][source] = error;
      this.update();
    } else {
      this._errors[type][source] = error;
    }
  }
}

export namespace LibraryConfigListWidget {
  export interface IOptions {
    updateSpace: boolean;
    onCheckUpdateSpace: (updateSpace: boolean) => void;
    onSave: () => Promise<void>;
    schema: JSONSchema7;
  }
}
