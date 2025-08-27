import Alert from '@mui/material/Alert';
import React, { useEffect, useMemo, useState } from 'react';
import { DropdownItem } from '../../../components/selectinput';
import { i18nStrings } from '../../../constants';
import { ParsedSpecName } from '../../../types';
import { JobEnvironmentProps } from '../JobEnvironment';
import { SelectInputContainer } from '../SelectInputContainer';
import * as sharedStyles from '../styles';
import { StudioImageSelectorOption } from './StudioImageSelectorOption';
import { fetchKernelAndImagesForStudio } from './studioApi';
import {
  ImageGroup,
  ImageMapValue,
  getImageOptionsFromMap,
  getImagesFromMap,
  getInitialImageValueForStudio,
  getPreSelectedNotebookKernelSpec,
} from './studioHelpers';
import * as styles from './studioStyles';
import { usePluginEnvironment } from '../../../utils/PluginEnvironmentProvider';

const tooltipsStrings = i18nStrings.ScheduleNoteBook.MainPanel.Tooltips;
const studioTooltipsStrings = i18nStrings.ScheduleNoteBook.MainPanel.StudioTooltips;


const StudioJobEnvironment: React.FunctionComponent<JobEnvironmentProps> = ({
  isDisabled,
  formState,
  formErrors,
  setFormState,
  setFormErrors,
  model,
  jobsView,
  requestClient,
  contentsManager,
}) => {
  const { pluginEnvironment } = usePluginEnvironment();
  const [selectedKernel, setSelectedKernel] = useState<ParsedSpecName>({ arnEnvironment: null, kernel: null, version: null });
  const [imageMap, setImageMap] = useState<Record<string, ImageMapValue>>({});

  useEffect(() => {
    fetchKernelAndImagesForStudio(requestClient).then(async (kernelSpecs) => {
      if (kernelSpecs) {
        setImageMap(getImagesFromMap(kernelSpecs));
      }

      const preSelectedSpec = await getPreSelectedNotebookKernelSpec(model.inputFile, contentsManager);
      const doesPreselectedSpecExist = preSelectedSpec in (kernelSpecs?.kernelspecs ?? {});
      const preSelectedNotebookKernelSpec = (doesPreselectedSpecExist ? preSelectedSpec : '');

      const defaultKernelSelectorValue = getInitialImageValueForStudio(
        model.runtimeEnvironmentParameters,
        preSelectedNotebookKernelSpec,
        jobsView
      );
      setSelectedKernel(defaultKernelSelectorValue);

      setFormState(formState => ({
        ...formState,
        sm_kernel: defaultKernelSelectorValue.kernel || '',
        sm_image: defaultKernelSelectorValue.arnEnvironment || '',
      }));
    });
  }, []);

  const smImages = getImageOptionsFromMap(imageMap, ImageGroup.Sagemaker, false).options ?? [];
  const customImages = getImageOptionsFromMap(imageMap, ImageGroup.Custom).options ?? [];
  const imageDropdownItems: DropdownItem[] = [...smImages, ...customImages];

  const kernelDropdownItems: DropdownItem[] = useMemo(() => {
    if (!selectedKernel.arnEnvironment) {
      return [];
    }

    return imageMap[selectedKernel.arnEnvironment]?.kernelOptions || [];
  }, [imageMap, selectedKernel]);

  const handleImageSelection = (
    item: DropdownItem | string,
    subOption?: DropdownItem
  ) => {
    if (!item || typeof item === 'string') {
      return;
    }

    const kernelItems: DropdownItem[] =
      item.optionMetadata?.kernelOptions || [];
    const kernel: string | null =
      kernelItems.length > 0 ? kernelItems[0].value : null;
    const version: string | null = subOption ? subOption.value : null;

    setFormState({
      ...formState,
      //Property sm_image can be either of the form 'arn:aws[a-z\-]*:sagemaker:[a-z0-9\-]*:[0-9]{12}:image/custom-image-name'
      // or 'arn:aws[a-z\-]*:sagemaker:[a-z0-9\-]*:[0-9]{12}:image-version/custom-image-name/2'
      sm_image: item.value + (version ? "/" + version : ''),
      sm_kernel: kernel ?? ''
    });
    setSelectedKernel({ arnEnvironment: item.value, kernel, version });
  };

  const handleKernelSelection = (item: DropdownItem | string) => {
    if (!item || typeof item === 'string') {
      return;
    }

    if (item) {
      setFormState({ ...formState, sm_kernel: item.value });
      setSelectedKernel({ ...selectedKernel, kernel: item.value });
    }
  };

  const isError = !!formErrors.jobEnvironmentError;
  const errorMessageWithIcon = (
    <div className={sharedStyles.ErrorIconStyled}>
      <Alert severity="error">{formErrors.jobEnvironmentError}</Alert>
    </div>
  );

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

  return (
    <div className={styles.JobEnvironmentContainer}>
      <div className={styles.KernelImageSelectorContainer}>
        <div className={styles.ImageContainer}>
          <SelectInputContainer
            data-testid="sm_image_dropdown"
            options={imageDropdownItems}
            value={selectedKernel.arnEnvironment}
            label={i18nStrings.ImageSelector.label}
            customListItemRender={StudioImageSelectorOption}
            onChange={handleImageSelection}
            readOnly={isDisabled}
            groupBy={(item) => item.group ?? ''}
            toolTipText={pluginEnvironment.isStudio ? studioTooltipsStrings.ImageTooltipText : tooltipsStrings.ImageTooltipText}
          />
          {formErrors.jobEnvironmentError && (
            <div className={sharedStyles.ValidationMessageStyled}>
              {isError && errorMessageWithIcon}
            </div>
          )}
        </div>
        <SelectInputContainer
          options={kernelDropdownItems}
          value={selectedKernel.kernel}
          label={i18nStrings.KernelSelector.label}
          onChange={handleKernelSelection}
          readOnly={isDisabled}
          toolTipText={pluginEnvironment.isStudio ? studioTooltipsStrings.KernelTooltipText : tooltipsStrings.KernelTooltipText}
        />
      </div>
    </div>
  );
};

export { StudioJobEnvironment };
