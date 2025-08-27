import React, { useEffect, useState } from 'react';
import { i18nStrings } from '../../../constants';
import * as Styles from '../../styles';
import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { SelectInputContainer } from '../SelectInputContainer';
import { getPreSelectedNotebookKernelSpec } from '../Studio/studioHelpers';
const tooltipsStrings = i18nStrings.ScheduleNoteBook.MainPanel.Tooltips;
export const JupyterLabJobEnvironment = ({ setFormState, formState, isDisabled, formErrors, setFormErrors, contentsManager, model, }) => {
    const [imagesOptions, setImagesOptions] = useState([]);
    const [kernelOptions, setKernelOptions] = useState([]);
    const fetchImages = async () => {
        const settings = ServerConnection.makeSettings();
        const url = URLExt.join(settings.baseUrl, '/sagemaker_studio_jupyter_scheduler/sagemaker_images');
        const response = await ServerConnection.makeRequest(url, {}, settings);
        if (response.status == 200) {
            const responseJson = await response.json();
            return responseJson.map((imageMetadata) => ({
                label: imageMetadata.image_display_name,
                value: imageMetadata.image_arn,
            }));
        }
        return [];
    };
    const fetchKernelNames = async () => {
        const settings = ServerConnection.makeSettings();
        const url = URLExt.join(settings.baseUrl, '/api/kernelspecs');
        const response = await ServerConnection.makeRequest(url, {}, settings);
        let defaultKernelName = null;
        const kernelNames = [];
        const kernelOptions = [];
        if (response.status === 200) {
            const kernelSpecsResponse = await response.json();
            defaultKernelName = kernelSpecsResponse.default;
            if (kernelSpecsResponse.kernelspecs) {
                Object.values(kernelSpecsResponse.kernelspecs).forEach((kernelSpec) => {
                    if (kernelSpec) {
                        kernelNames.push(kernelSpec.name);
                        let kernelDisplayName = kernelSpec.name;
                        if (kernelSpec.spec) {
                            kernelDisplayName = kernelSpec.spec.display_name;
                        }
                        kernelOptions.push({ label: kernelDisplayName, value: kernelSpec.name });
                    }
                });
            }
        }
        return { defaultKernelName, kernelNames, kernelOptions };
    };
    useEffect(() => {
        Promise.all([
            getPreSelectedNotebookKernelSpec(model.inputFile, contentsManager),
            fetchImages(),
            fetchKernelNames()
        ]).then((values) => {
            const preSelectedNotebookKernelName = values[0];
            const imagesOptions = values[1];
            const kernelDetails = values[2];
            let defaultImageValue;
            let defaultKernelValue;
            if (imagesOptions && imagesOptions.length > 0) {
                setImagesOptions(imagesOptions);
            }
            if (model.runtimeEnvironmentParameters && model.runtimeEnvironmentParameters.sm_image) {
                defaultImageValue = model.runtimeEnvironmentParameters.sm_image;
            }
            else if (imagesOptions && imagesOptions.length > 0) {
                defaultImageValue = imagesOptions[0].value;
            }
            if (kernelDetails && kernelDetails.kernelOptions && kernelDetails.kernelOptions.length > 0) {
                setKernelOptions(kernelDetails.kernelOptions);
            }
            if (model.runtimeEnvironmentParameters && model.runtimeEnvironmentParameters.sm_kernel) {
                defaultKernelValue = model.runtimeEnvironmentParameters.sm_kernel;
            }
            else {
                if (kernelDetails.kernelNames.indexOf(preSelectedNotebookKernelName) >= 0) {
                    defaultKernelValue = preSelectedNotebookKernelName;
                }
                else {
                    defaultKernelValue = kernelDetails.defaultKernelName || '';
                }
            }
            setFormState(state => ({
                ...state,
                sm_image: defaultImageValue !== null && defaultImageValue !== void 0 ? defaultImageValue : '',
                sm_kernel: defaultKernelValue !== null && defaultKernelValue !== void 0 ? defaultKernelValue : '',
            }));
        })
            .catch((error) => console.error(error));
    }, []);
    const handleImageSelection = (item) => {
        if (!item || typeof item === 'string') {
            return;
        }
        setFormState({
            ...formState,
            sm_image: item.value,
        });
    };
    const handleKernelSelection = (item) => {
        if (!item || typeof item === 'string') {
            return;
        }
        setFormState({
            ...formState,
            sm_kernel: item.value,
        });
    };
    return (React.createElement("div", { className: Styles.WidgetFieldsContainer },
        React.createElement(SelectInputContainer, { "data-testid": "sm_image_dropdown", options: imagesOptions, value: formState.sm_image, label: i18nStrings.ImageSelector.label, onChange: handleImageSelection, readOnly: isDisabled, toolTipText: tooltipsStrings.ImageTooltipText, required: true }),
        React.createElement(SelectInputContainer, { "data-testid": "sm_kernel_dropdown", options: kernelOptions, value: formState.sm_kernel, label: i18nStrings.KernelSelector.label, onChange: handleKernelSelection, readOnly: isDisabled, toolTipText: tooltipsStrings.KernelTooltipText, required: true })));
};
//# sourceMappingURL=JupyterLabJobEnvironment.js.map