import Alert from '@mui/material/Alert';
import React, { useEffect, useMemo, useState } from 'react';
import { i18nStrings } from '../../../constants';
import { SelectInputContainer } from '../SelectInputContainer';
import * as sharedStyles from '../styles';
import { StudioImageSelectorOption } from './StudioImageSelectorOption';
import { fetchKernelAndImagesForStudio } from './studioApi';
import { ImageGroup, getImageOptionsFromMap, getImagesFromMap, getInitialImageValueForStudio, getPreSelectedNotebookKernelSpec, } from './studioHelpers';
import * as styles from './studioStyles';
import { usePluginEnvironment } from '../../../utils/PluginEnvironmentProvider';
const tooltipsStrings = i18nStrings.ScheduleNoteBook.MainPanel.Tooltips;
const studioTooltipsStrings = i18nStrings.ScheduleNoteBook.MainPanel.StudioTooltips;
const StudioJobEnvironment = ({ isDisabled, formState, formErrors, setFormState, setFormErrors, model, jobsView, requestClient, contentsManager, }) => {
    var _a, _b;
    const { pluginEnvironment } = usePluginEnvironment();
    const [selectedKernel, setSelectedKernel] = useState({ arnEnvironment: null, kernel: null, version: null });
    const [imageMap, setImageMap] = useState({});
    useEffect(() => {
        fetchKernelAndImagesForStudio(requestClient).then(async (kernelSpecs) => {
            var _a;
            if (kernelSpecs) {
                setImageMap(getImagesFromMap(kernelSpecs));
            }
            const preSelectedSpec = await getPreSelectedNotebookKernelSpec(model.inputFile, contentsManager);
            const doesPreselectedSpecExist = preSelectedSpec in ((_a = kernelSpecs === null || kernelSpecs === void 0 ? void 0 : kernelSpecs.kernelspecs) !== null && _a !== void 0 ? _a : {});
            const preSelectedNotebookKernelSpec = (doesPreselectedSpecExist ? preSelectedSpec : '');
            const defaultKernelSelectorValue = getInitialImageValueForStudio(model.runtimeEnvironmentParameters, preSelectedNotebookKernelSpec, jobsView);
            setSelectedKernel(defaultKernelSelectorValue);
            setFormState(formState => ({
                ...formState,
                sm_kernel: defaultKernelSelectorValue.kernel || '',
                sm_image: defaultKernelSelectorValue.arnEnvironment || '',
            }));
        });
    }, []);
    const smImages = (_a = getImageOptionsFromMap(imageMap, ImageGroup.Sagemaker, false).options) !== null && _a !== void 0 ? _a : [];
    const customImages = (_b = getImageOptionsFromMap(imageMap, ImageGroup.Custom).options) !== null && _b !== void 0 ? _b : [];
    const imageDropdownItems = [...smImages, ...customImages];
    const kernelDropdownItems = useMemo(() => {
        var _a;
        if (!selectedKernel.arnEnvironment) {
            return [];
        }
        return ((_a = imageMap[selectedKernel.arnEnvironment]) === null || _a === void 0 ? void 0 : _a.kernelOptions) || [];
    }, [imageMap, selectedKernel]);
    const handleImageSelection = (item, subOption) => {
        var _a;
        if (!item || typeof item === 'string') {
            return;
        }
        const kernelItems = ((_a = item.optionMetadata) === null || _a === void 0 ? void 0 : _a.kernelOptions) || [];
        const kernel = kernelItems.length > 0 ? kernelItems[0].value : null;
        const version = subOption ? subOption.value : null;
        setFormState({
            ...formState,
            //Property sm_image can be either of the form 'arn:aws[a-z\-]*:sagemaker:[a-z0-9\-]*:[0-9]{12}:image/custom-image-name'
            // or 'arn:aws[a-z\-]*:sagemaker:[a-z0-9\-]*:[0-9]{12}:image-version/custom-image-name/2'
            sm_image: item.value + (version ? "/" + version : ''),
            sm_kernel: kernel !== null && kernel !== void 0 ? kernel : ''
        });
        setSelectedKernel({ arnEnvironment: item.value, kernel, version });
    };
    const handleKernelSelection = (item) => {
        if (!item || typeof item === 'string') {
            return;
        }
        if (item) {
            setFormState({ ...formState, sm_kernel: item.value });
            setSelectedKernel({ ...selectedKernel, kernel: item.value });
        }
    };
    const isError = !!formErrors.jobEnvironmentError;
    const errorMessageWithIcon = (React.createElement("div", { className: sharedStyles.ErrorIconStyled },
        React.createElement(Alert, { severity: "error" }, formErrors.jobEnvironmentError)));
    useEffect(() => {
        if (selectedKernel.arnEnvironment && selectedKernel.kernel) {
            if (formErrors.jobEnvironmentError) {
                setFormErrors({
                    ...formErrors,
                    jobEnvironmentError: ''
                });
            }
        }
    }, [selectedKernel.arnEnvironment, selectedKernel.kernel]);
    if (Object.keys(imageMap).length === 0) {
        return null;
    }
    return (React.createElement("div", { className: styles.JobEnvironmentContainer },
        React.createElement("div", { className: styles.KernelImageSelectorContainer },
            React.createElement("div", { className: styles.ImageContainer },
                React.createElement(SelectInputContainer, { "data-testid": "sm_image_dropdown", options: imageDropdownItems, value: selectedKernel.arnEnvironment, label: i18nStrings.ImageSelector.label, customListItemRender: StudioImageSelectorOption, onChange: handleImageSelection, readOnly: isDisabled, groupBy: (item) => { var _a; return (_a = item.group) !== null && _a !== void 0 ? _a : ''; }, toolTipText: pluginEnvironment.isStudio ? studioTooltipsStrings.ImageTooltipText : tooltipsStrings.ImageTooltipText }),
                formErrors.jobEnvironmentError && (React.createElement("div", { className: sharedStyles.ValidationMessageStyled }, isError && errorMessageWithIcon))),
            React.createElement(SelectInputContainer, { options: kernelDropdownItems, value: selectedKernel.kernel, label: i18nStrings.KernelSelector.label, onChange: handleKernelSelection, readOnly: isDisabled, toolTipText: pluginEnvironment.isStudio ? studioTooltipsStrings.KernelTooltipText : tooltipsStrings.KernelTooltipText }))));
};
export { StudioJobEnvironment };
//# sourceMappingURL=StudioJobEnvironment.js.map