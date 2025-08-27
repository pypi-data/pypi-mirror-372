import { DropdownItem } from '../components/selectinput';
import { ImagesMap } from '../types';
type SageMakerImagesApiResponse = {
    image_arn: string;
    image_display_name: string;
    image_description?: string;
    kernelspecs?: {
        DisplayName: string;
        Name: string;
    }[];
}[];
declare const parseListSageMakerImagesAPIResponse: (apiResponse: SageMakerImagesApiResponse) => any;
declare function getImageOptionsFromMap(imagesMap: ImagesMap): DropdownItem[];
export { parseListSageMakerImagesAPIResponse, getImageOptionsFromMap };
//# sourceMappingURL=images.d.ts.map