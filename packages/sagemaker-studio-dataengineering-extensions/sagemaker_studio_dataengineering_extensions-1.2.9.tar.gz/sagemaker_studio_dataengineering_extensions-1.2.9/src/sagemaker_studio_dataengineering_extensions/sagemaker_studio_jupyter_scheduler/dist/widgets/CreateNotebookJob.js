import React, { useEffect, useState } from 'react';
import { Dialog } from '@jupyterlab/apputils';
import { StyledEngineProvider, ThemeProvider } from '@mui/material/styles';
import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { JobsView } from '@jupyterlab/scheduler';
import { CreateNotebookJobForm } from './CreateNotebookJobForm';
import { errorCodes, i18nStrings, JUPYTER_COMMAND_IDS } from '../constants';
import { renderTextWithLinks } from '../utils';
import * as Styles from './styles';
import { getJupyterLabTheme } from '../themeProvider';
import { usePluginEnvironment } from '../utils/PluginEnvironmentProvider';
const showCredentialsErrorDialog = async (commands) => {
    const body = (React.createElement(React.Fragment, null, i18nStrings.Dialog.awsCredentialsError.body.text.map((text, idx) => (React.createElement("p", { key: idx, className: Styles.CredentialsErrorDialogParagraph }, renderTextWithLinks(text, i18nStrings.Dialog.awsCredentialsError.body.links))))));
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
const CreateNotebookJob = ({ requestClient, contentsManager, commands, jobsView, errors, handleErrorsChange, ...rest }) => {
    const { pluginEnvironment } = usePluginEnvironment();
    const [apiError, setApiError] = useState('');
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
        }
        else {
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
                .then(async (executionEnvironments) => {
                setEnvironmentsLoading(false);
                setExecutionEnvironments(executionEnvironments);
            })
                .catch(error => {
                setApiError(error.message);
            });
        }
        else {
            setEnvironmentsLoading(false);
        }
    }, [jobsView, rest.model.inputFile]);
    const [executionEnvironments, setExecutionEnvironments] = useState({});
    const [environmentsLoading, setEnvironmentsLoading] = useState(true);
    if (apiError) {
        return React.createElement("div", { className: Styles.ErrorMessageBlock }, apiError);
    }
    const loading = environmentsLoading;
    if (loading) {
        return null;
    }
    if (jobsView === JobsView.CreateForm && !(executionEnvironments === null || executionEnvironments === void 0 ? void 0 : executionEnvironments.auto_detected_config)) {
        return null;
    }
    return (React.createElement(ThemeProvider, { theme: getJupyterLabTheme() },
        React.createElement(StyledEngineProvider, { injectFirst: true },
            React.createElement(CreateNotebookJobForm, { executionEnvironments: executionEnvironments, requestClient: requestClient, contentsManager: contentsManager, jobsView: jobsView, errors: errors, handleErrorsChange: handleErrorsChange, ...rest }))));
};
export { CreateNotebookJob };
//# sourceMappingURL=CreateNotebookJob.js.map