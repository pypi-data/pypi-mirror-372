import { DropdownItem } from '../components/selectinput';
import { ImagesMap } from '../types';

type SageMakerImagesApiResponse = {
  image_arn: string;
  image_display_name: string;
  image_description?: string;
  kernelspecs?: { DisplayName: string; Name: string }[];
}[];

const parseListSageMakerImagesAPIResponse = (apiResponse: SageMakerImagesApiResponse) => {
  if (apiResponse.length > 0) {
    const mapKernelSpecsToOptions = (kernelspecs: any) => {
      if (kernelspecs) {
        return kernelspecs.map((kernelspec: any) => ({ displayName: kernelspec.DisplayName, name: kernelspec.Name }));
      }
      return [];
    };
    return Object.fromEntries(
      apiResponse.map((imageMetadata: any) => [
        imageMetadata.image_arn,
        {
          arnEnvironment: imageMetadata.image_arn,
          displayName: imageMetadata.image_display_name,
          description: imageMetadata.image_description,
          kernelOptions: mapKernelSpecsToOptions(imageMetadata.kernelspecs),
        },
      ]),
    );
  }
  return {};
};

function getImageOptionsFromMap(imagesMap: ImagesMap): DropdownItem[] {
  const imageOptions: DropdownItem[] = [];
  Object.keys(imagesMap).forEach((imageArn) => {
    imageOptions.push({
      label: imagesMap[imageArn].displayName,
      value: imagesMap[imageArn].arnEnvironment,
      optionMetadata: {
        description: imagesMap[imageArn].description,
      },
    });
  });
  return imageOptions;
}

export { parseListSageMakerImagesAPIResponse, getImageOptionsFromMap };
