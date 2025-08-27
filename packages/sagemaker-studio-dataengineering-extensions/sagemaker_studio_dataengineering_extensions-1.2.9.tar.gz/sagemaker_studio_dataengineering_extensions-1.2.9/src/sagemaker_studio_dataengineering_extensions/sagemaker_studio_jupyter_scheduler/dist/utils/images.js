const parseListSageMakerImagesAPIResponse = (apiResponse) => {
    if (apiResponse.length > 0) {
        const mapKernelSpecsToOptions = (kernelspecs) => {
            if (kernelspecs) {
                return kernelspecs.map((kernelspec) => ({ displayName: kernelspec.DisplayName, name: kernelspec.Name }));
            }
            return [];
        };
        return Object.fromEntries(apiResponse.map((imageMetadata) => [
            imageMetadata.image_arn,
            {
                arnEnvironment: imageMetadata.image_arn,
                displayName: imageMetadata.image_display_name,
                description: imageMetadata.image_description,
                kernelOptions: mapKernelSpecsToOptions(imageMetadata.kernelspecs),
            },
        ]));
    }
    return {};
};
function getImageOptionsFromMap(imagesMap) {
    const imageOptions = [];
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
//# sourceMappingURL=images.js.map