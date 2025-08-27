import React, { useEffect, useMemo } from 'react';
import { i18nStrings } from '../../../constants';
import * as Styles from '../../styles';
import { validateImage, validateKernel } from '../AdvancedOptions/validationHelpers';
import { InputContainer } from '../InputContainer';
import { getInitialImageValue } from '../initialValueHelpers';
import { JobEnvironmentProps } from './jobEnvironment';

const widgetStrings = i18nStrings.ScheduleNoteBook.MainPanel.AdvancedOptions;
const tooltipsStrings = i18nStrings.ScheduleNoteBook.MainPanel.Tooltips;

export const DefaultJobEnvironment: React.FC<JobEnvironmentProps> = ({
  setFormState,
  formState,
  isDisabled,
  formErrors,
  setFormErrors,
  model,
  executionEnvironments,
}) => {
  const defaultKernelSelectorValue = useMemo(() => {
    return getInitialImageValue(model.runtimeEnvironmentParameters, executionEnvironments?.auto_detected_config);
  }, []);

  useEffect(() => {
    setFormState({
      ...formState,
      sm_kernel: defaultKernelSelectorValue.kernel || '',
      sm_image: defaultKernelSelectorValue.arnEnvironment || '',
    });
  }, [defaultKernelSelectorValue]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const name = e.target.name;
    const value = e.target.value;
    setFormState({ ...formState, [name]: value });
  };

  const handleImageOnBlur = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { value } = e.target;
    const errorMessage = validateImage(value);

    setFormErrors({
      ...formErrors,
      ImageError: errorMessage,
    });
  }

  const handleKernelOnBlur = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { value } = e.target;
    const errorMessage = validateKernel(value);

    setFormErrors({
      ...formErrors,
      KernelError: errorMessage,
    });
  }

  return (<div className={Styles.WidgetFieldsContainer}>
    <InputContainer
      name={'sm_image'}
      onChange={handleChange}
      readOnly={isDisabled}
      required
      value={formState.sm_image}
      placeholder={widgetStrings.Placeholders.ImagePlaceHolder}
      labelInfo={widgetStrings.Image}
      errorMessage={formErrors.ImageError}
      onBlur={handleImageOnBlur}
      toolTipText={tooltipsStrings.ImageTooltipText}
    />

    <InputContainer
      name={'sm_kernel'}
      onChange={handleChange}
      readOnly={isDisabled}
      required
      value={formState.sm_kernel}
      placeholder={widgetStrings.Placeholders.KernelPlaceHolder}
      labelInfo={widgetStrings.Kernel}
      errorMessage={formErrors.KernelError}
      onBlur={handleKernelOnBlur}
      toolTipText={tooltipsStrings.KernelTooltipText}
    />
  </div>)
}
