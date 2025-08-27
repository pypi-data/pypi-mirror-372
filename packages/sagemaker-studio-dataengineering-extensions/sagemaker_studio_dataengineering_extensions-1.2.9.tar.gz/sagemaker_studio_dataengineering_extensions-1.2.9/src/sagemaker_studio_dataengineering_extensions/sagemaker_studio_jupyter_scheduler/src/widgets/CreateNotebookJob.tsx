import React, { useEffect, useState } from 'react';
import { Dialog } from '@jupyterlab/apputils';
import { StyledEngineProvider, ThemeProvider } from '@mui/material/styles';

import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection, ContentsManager } from '@jupyterlab/services';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { JobsView, Scheduler } from '@jupyterlab/scheduler';
import { CommandRegistry } from '@lumino/commands';

import { CreateNotebookJobForm } from './CreateNotebookJobForm';
import { errorCodes, i18nStrings, JUPYTER_COMMAND_IDS } from '../constants';
import { renderTextWithLinks } from '../utils';
import * as Styles from './styles';

import { getJupyterLabTheme } from '../themeProvider';
import { Theme } from '@mui/material/styles';
import { usePluginEnvironment } from '../utils/PluginEnvironmentProvider';

declare module '@mui/material' {
  // eslint-disable-next-line @typescript-eslint/no-empty-interface
  interface DefaultTheme extends Theme { }
}


type CreateNotebookJobProps = Scheduler.IAdvancedOptionsProps & {
  requestClient: ServerConnection.ISettings;
  contentsManager: ContentsManager;
  commands: CommandRegistry;
  settingRegistry: ISettingRegistry;
};

const showCredentialsErrorDialog = async (commands: CommandRegistry) => {
  const body = (
    <>
      {i18nStrings.Dialog.awsCredentialsError.body.text.map((text, idx) => (
        <p key={idx} className={Styles.CredentialsErrorDialogParagraph}>
          {renderTextWithLinks(text, i18nStrings.Dialog.awsCredentialsError.body.links)}
        </p>
      ))}
    </>
  );
  const dialog = new Dialog({
    title: i18nStrings.Dialog.awsCredentialsError.title,
    body,
    buttons: [
      Dialog.cancelButton(),
      Dialog.okButton({ label: i18nStrings.Dialog.awsCredentialsError.buttons.enterKeysInTerminal }),
    ],
  });
  const result = await dialog.launch();
  if (result.button.label === i18nStrings.Dialog.awsCredentialsError.buttons.enterKeysInTerminal) {
    commands.execute(JUPYTER_COMMAND_IDS.terminal.createNew);
  }
};

const CreateNotebookJob: React.FC<CreateNotebookJobProps> = ({
  requestClient,
  contentsManager,
  commands,
  jobsView,
  errors,
  handleErrorsChange,
  ...rest
}) => {
  const { pluginEnvironment } = usePluginEnvironment();
  const [apiError, setApiError] = useState<string>('');

  const fetchExecutionEnvironments = async () => {
    const url = URLExt.join(requestClient.baseUrl, '/sagemaker_studio_jupyter_scheduler/advanced_environments');
    const response = await ServerConnection.makeRequest(url, {}, requestClient);

    if (response.status !== 200 && pluginEnvironment.isLocalJL) {
      const responseJson = await response.json();
      const responseErrorCode = responseJson.error_code;
      const awsCredentialsErrors = Object.values(errorCodes.awsCredentials);
      if (awsCredentialsErrors.indexOf(responseErrorCode) >= 0) {
        showCredentialsErrorDialog(commands);
      }
      throw new Error(response.statusText);
    } else {
      const executionEnvironmentsResponse = await response.json();
      return executionEnvironmentsResponse;
    }
  };

  useEffect(() => {
    const loadingErrors = {
      ...errors,
      environmentsStillLoading: 'EnvironmentsStillLoadingError',
      kernelsStillLoading: 'KernelsStillLoadingError',
    };

    handleErrorsChange(loadingErrors);

    if (jobsView === JobsView.CreateForm) {
      fetchExecutionEnvironments()
        .then(async (executionEnvironments: any) => {
          setEnvironmentsLoading(false);
          setExecutionEnvironments(executionEnvironments);
        })
        .catch(error => {
          setApiError(error.message);
        });
    } else {
      setEnvironmentsLoading(false);
    }
  }, [jobsView, rest.model.inputFile]);

  const [executionEnvironments, setExecutionEnvironments] = useState<any>({});

  const [environmentsLoading, setEnvironmentsLoading] = useState<boolean>(true);

  if (apiError) {
    return <div className={Styles.ErrorMessageBlock}>{apiError}</div>
  }

  const loading = environmentsLoading;

  if (loading) {
    return null;
  }

  if (jobsView === JobsView.CreateForm && !executionEnvironments?.auto_detected_config) {
    return null;
  }

  return (
    <ThemeProvider theme={getJupyterLabTheme()}>
      <StyledEngineProvider injectFirst>
        <CreateNotebookJobForm
          executionEnvironments={executionEnvironments}
          requestClient={requestClient}
          contentsManager={contentsManager}
          jobsView={jobsView as any}
          errors={errors}
          handleErrorsChange={handleErrorsChange}
          {...rest}
        />
      </StyledEngineProvider>
    </ThemeProvider>
  );
};

export { CreateNotebookJob };
