import React, { useEffect, useMemo } from 'react';
import { i18nStrings } from '../../../constants';
import * as Styles from '../../styles';
import { validateImage, validateKernel } from '../AdvancedOptions/validationHelpers';
import { InputContainer } from '../InputContainer';
import { getInitialImageValue } from '../initialValueHelpers';
const widgetStrings = i18nStrings.ScheduleNoteBook.MainPanel.AdvancedOptions;
const tooltipsStrings = i18nStrings.ScheduleNoteBook.MainPanel.Tooltips;
export const DefaultJobEnvironment = ({ setFormState, formState, isDisabled, formErrors, setFormErrors, model, executionEnvironments, }) => {
    const defaultKernelSelectorValue = useMemo(() => {
        return getInitialImageValue(model.runtimeEnvironmentParameters, executionEnvironments === null || executionEnvironments === void 0 ? void 0 : executionEnvironments.auto_detected_config);
    }, []);
    useEffect(() => {
        setFormState({
            ...formState,
            sm_kernel: defaultKernelSelectorValue.kernel || '',
            sm_image: defaultKernelSelectorValue.arnEnvironment || '',
        });
    }, [defaultKernelSelectorValue]);
    const handleChange = (e) => {
        const name = e.target.name;
        const value = e.target.value;
        setFormState({ ...formState, [name]: value });
    };
    const handleImageOnBlur = (e) => {
        const { value } = e.target;
        const errorMessage = validateImage(value);
        setFormErrors({
            ...formErrors,
            ImageError: errorMessage,
        });
    };
    const handleKernelOnBlur = (e) => {
        const { value } = e.target;
        const errorMessage = validateKernel(value);
        setFormErrors({
            ...formErrors,
            KernelError: errorMessage,
        });
    };
    return (React.createElement("div", { className: Styles.WidgetFieldsContainer },
        React.createElement(InputContainer, { name: 'sm_image', onChange: handleChange, readOnly: isDisabled, required: true, value: formState.sm_image, placeholder: widgetStrings.Placeholders.ImagePlaceHolder, labelInfo: widgetStrings.Image, errorMessage: formErrors.ImageError, onBlur: handleImageOnBlur, toolTipText: tooltipsStrings.ImageTooltipText }),
        React.createElement(InputContainer, { name: 'sm_kernel', onChange: handleChange, readOnly: isDisabled, required: true, value: formState.sm_kernel, placeholder: widgetStrings.Placeholders.KernelPlaceHolder, labelInfo: widgetStrings.Kernel, errorMessage: formErrors.KernelError, onBlur: handleKernelOnBlur, toolTipText: tooltipsStrings.KernelTooltipText })));
};
//# sourceMappingURL=DefaultJobEnvironment.js.map