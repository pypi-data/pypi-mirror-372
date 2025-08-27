import React from 'react';
import { ServerConnection, ContentsManager } from '@jupyterlab/services';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { Scheduler } from '@jupyterlab/scheduler';
import { CommandRegistry } from '@lumino/commands';
import { Theme } from '@mui/material/styles';
declare module '@mui/material' {
    interface DefaultTheme extends Theme {
    }
}
type CreateNotebookJobProps = Scheduler.IAdvancedOptionsProps & {
    requestClient: ServerConnection.ISettings;
    contentsManager: ContentsManager;
    commands: CommandRegistry;
    settingRegistry: ISettingRegistry;
};
declare const CreateNotebookJob: React.FC<CreateNotebookJobProps>;
export { CreateNotebookJob };
//# sourceMappingURL=CreateNotebookJob.d.ts.map