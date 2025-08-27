import { JobsView } from '@jupyterlab/scheduler';
import { retro, toArray } from '@lumino/algorithm';
import isString from 'lodash/isString';
import { KERNELSPEC_NAME_SEPARATOR } from '../../../constants';
import { parseSpecName } from '../../../utils';
const constructArnName = (env, kernel, version) => {
    const scrubbedVersion = version ? `/${version}` : '';
    return `${kernel}${KERNELSPEC_NAME_SEPARATOR}${env}${scrubbedVersion}`;
};
const AXIS_IMAGE_NAME = 'Geospatial';
const EMR_COMPATIBLE_IMAGES_LIST = [
    'datascience-1.0',
    'sagemaker-data-science-38',
    '1.8.1-cpu-py36',
    'pytorch-1.8-gpu-py36',
    'sagemaker-sparkmagic',
    'tensorflow-2.6-cpu-py38-ubuntu20.04-v1',
    'tensorflow-2.6-gpu-py38-cu112-ubuntu20.04-v1',
    'sagemaker-sparkanalytics-v1',
];
var ImageGroup;
(function (ImageGroup) {
    ImageGroup["Custom"] = "customImage";
    ImageGroup["Sagemaker"] = "smeImage";
    ImageGroup["Session"] = "session";
})(ImageGroup || (ImageGroup = {}));
const createImageMap = (options) => {
    const { specs, sessions } = options;
    const imageMap = {};
    const kernelspecs = specs ? specs.kernelspecs : {};
    Object.values(kernelspecs).forEach((spec) => {
        if (!spec) {
            return;
        }
        const smeMetadata = spec.metadata ? spec.metadata.sme_metadata : null;
        const { imageName, kernelName } = parseSpecDisplayName(spec.display_name);
        const { kernel, arnEnvironment, version } = parseSpecName(spec.name);
        // If parsing failed, something is wrong, so skip. Only version can be null after parsing.
        if (!kernel || !arnEnvironment || !imageName || !kernelName) {
            return;
        }
        const specMetaData = {
            arnEnvironment,
            kernelOptions: [{ label: kernelName, value: kernel }],
            versionOptions: version ? [{ label: `v${version}`, value: version }] : undefined,
            label: imageName,
            description: (smeMetadata === null || smeMetadata === void 0 ? void 0 : smeMetadata.description) ? smeMetadata.description : undefined,
            group: smeMetadata && smeMetadata.is_template ? ImageGroup.Sagemaker : ImageGroup.Custom,
        };
        if (!imageMap[arnEnvironment]) {
            imageMap[arnEnvironment] = specMetaData;
        }
        else {
            const { kernelOptions } = imageMap[arnEnvironment];
            if (!kernelOptions.some((opt) => opt.value === kernel)) {
                const newKernelOptions = [...kernelOptions, { label: kernelName, value: kernel }];
                imageMap[arnEnvironment].kernelOptions = newKernelOptions;
            }
            if (version) {
                const { versionOptions } = imageMap[arnEnvironment];
                if (!versionOptions.some((opt) => opt.value === version)) {
                    const optionToAdd = {
                        label: `v${version}`,
                        value: version.toString(),
                    };
                    const newVersionOptions = Array.isArray(versionOptions) ? [...versionOptions, optionToAdd] : [optionToAdd];
                    imageMap[arnEnvironment].versionOptions = newVersionOptions;
                }
            }
        }
    });
    const sessionData = retro(sessions);
    const sessionList = toArray(sessionData);
    // Loop over all sessions, so that we can populate the "Image from other session" selection
    // We need to loop everytime in case more notebooks have been opened that we'd like to add to this list
    sessionList.forEach((sess) => {
        var _a, _b, _c;
        if (!(sess === null || sess === void 0 ? void 0 : sess.name) || !((_a = sess.kernel) === null || _a === void 0 ? void 0 : _a.name)) {
            return;
        }
        const sessionLabel = sess.name;
        const { kernel, arnEnvironment, version } = parseSpecName(sess.kernel.name);
        // If parsing failed, something is wrong or this session isn't relevant, so skip. Only version can be null after parsing.
        if (!kernel || !arnEnvironment) {
            return;
        }
        const environmentName = version ? `${arnEnvironment}/${version}` : arnEnvironment;
        let kernelOptions = [];
        if (imageMap && ((_b = imageMap[arnEnvironment]) === null || _b === void 0 ? void 0 : _b.kernelOptions)) {
            const options = (_c = imageMap[arnEnvironment].kernelOptions) === null || _c === void 0 ? void 0 : _c.find((o) => o.value === kernel);
            kernelOptions = options ? [options] : [];
        }
        const sessionMetaData = {
            arnEnvironment: environmentName,
            kernelOptions: kernelOptions,
            label: sessionLabel,
            group: ImageGroup.Session,
            versionOptions: [],
        };
        imageMap[sessionLabel] = sessionMetaData;
    });
    return imageMap;
};
export async function getPreSelectedNotebookKernelSpec(filePath, contentsManager) {
    if (filePath.endsWith('.ipynb')) {
        try {
            const notebookContent = await contentsManager.get(filePath);
            return notebookContent.content.metadata.kernelspec.name;
        }
        catch (e) {
            return '';
        }
    }
    return '';
}
;
function parseSpecDisplayName(displayName) {
    try {
        if (!isString(displayName) || displayName.length === 0) {
            return { imageName: null, kernelName: null };
        }
        const [kernelPart, imagePart] = displayName.split('(');
        const imageName = imagePart && imagePart.slice(0, -1).split('/')[0];
        const kernelName = kernelPart && kernelPart.slice(0, -1);
        return { imageName, kernelName };
    }
    catch (e) {
        // TODO @mgoguen add logging here if / when possible
        return { imageName: null, kernelName: null };
    }
}
const OPTION_GROUP_LABELS = {
    smeImage: 'Sagemaker Image',
    customImage: 'Custom Image',
    prefered: 'Use image from preferred session',
    session: 'Use image from other session',
};
function getImageOptionsFromMap(imageMap, group, isFromCluster) {
    const filteredImages = Object.values(imageMap).filter((img) => {
        const env = img.arnEnvironment.split('/')[1];
        // If notebook is open from a cluster, only show EMR compatible images
        if (isFromCluster) {
            return (img === null || img === void 0 ? void 0 : img.group) === group && EMR_COMPATIBLE_IMAGES_LIST.includes(env);
        }
        // filter out axis image
        if ((img === null || img === void 0 ? void 0 : img.group) === ImageGroup.Sagemaker && img.label.includes(AXIS_IMAGE_NAME)) {
            return false;
        }
        // Show the image if the group matches
        return (img === null || img === void 0 ? void 0 : img.group) === group;
    });
    return {
        label: OPTION_GROUP_LABELS[group],
        value: '',
        options: filteredImages.map((img) => ({
            label: img.label,
            value: group === ImageGroup.Session ? img.label : img.arnEnvironment,
            group: OPTION_GROUP_LABELS[group],
            optionMetadata: img,
            options: img.versionOptions,
        })),
    };
}
function getSessionOptionsFromMap(imageMap, prefered) {
    var _a;
    if (!imageMap) {
        return [];
    }
    const filteredSessions = Object.values(imageMap).filter((img) => (img === null || img === void 0 ? void 0 : img.group) === ImageGroup.Session);
    let preferedSession;
    if ((_a = prefered === null || prefered === void 0 ? void 0 : prefered.name) === null || _a === void 0 ? void 0 : _a.includes(KERNELSPEC_NAME_SEPARATOR)) {
        const { kernel, arnEnvironment, version } = parseSpecName(prefered.name);
        if (kernel && arnEnvironment) {
            const environmentName = version ? `${arnEnvironment}/${version}` : arnEnvironment;
            preferedSession = filteredSessions.find((sess) => { var _a; return sess.arnEnvironment === environmentName && ((_a = sess.kernelOptions) === null || _a === void 0 ? void 0 : _a.some((s) => s.value === kernel)); });
        }
    }
    const preferedOption = preferedSession
        ? [
            {
                label: preferedSession.label,
                value: preferedSession.label,
                optionMetadata: preferedSession,
                options: preferedSession.versionOptions,
            },
        ]
        : [];
    return [
        { label: OPTION_GROUP_LABELS.prefered, value: '', options: preferedOption },
        {
            label: OPTION_GROUP_LABELS.session,
            value: '',
            options: filteredSessions.map((sess) => ({
                label: sess.label,
                value: sess.label,
                optionMetadata: sess,
                options: sess.versionOptions,
            })),
        },
    ];
}
export const getInitialImageValueForStudio = (runtimeEnvironmentParameters, preSelectedKernelFromNotebook, view) => {
    if (view === JobsView.JobDetail || view === JobsView.JobDefinitionDetail) {
        if (runtimeEnvironmentParameters) {
            const { sm_kernel, sm_image } = runtimeEnvironmentParameters;
            const KERNEL_IMAGE_KEY = `${sm_kernel}__SAGEMAKER_INTERNAL__${sm_image}`;
            return parseSpecName(KERNEL_IMAGE_KEY);
        }
        return {
            kernel: null,
            arnEnvironment: null,
            version: null
        };
    }
    else if (view === JobsView.CreateForm) {
        if (runtimeEnvironmentParameters &&
            'sm_image' in runtimeEnvironmentParameters) {
            const { sm_kernel, sm_image } = runtimeEnvironmentParameters;
            const KERNEL_IMAGE_KEY = `${sm_kernel}__SAGEMAKER_INTERNAL__${sm_image}`;
            return parseSpecName(KERNEL_IMAGE_KEY);
        }
        return (parseSpecName(preSelectedKernelFromNotebook) || {
            kernel: null,
            arnEnvironment: null,
            version: null
        });
    }
    return (parseSpecName(preSelectedKernelFromNotebook) || {
        kernel: null,
        arnEnvironment: null,
        version: null
    });
};
export function getImagesFromMap(options) {
    const imageMap = {};
    const specs = options.kernelspecs;
    Object.values(specs).forEach((spec) => {
        var _a;
        if (!spec) {
            return;
        }
        const smeMetadata = ((_a = spec.spec) === null || _a === void 0 ? void 0 : _a.metadata)
            ? spec.spec.metadata.sme_metadata
            : null;
        const { imageName, kernelName } = parseSpecDisplayName(spec.spec.display_name);
        const { kernel, arnEnvironment, version } = parseSpecName(spec.name);
        // If parsing failed, something is wrong, so skip. Only version can be null after parsing.
        if (!kernel || !arnEnvironment || !imageName || !kernelName) {
            return;
        }
        const imageLabel = version ? `${imageName} v${version}` : imageName;
        const specMetaData = {
            arnEnvironment,
            kernelOptions: [{ label: kernelName, value: kernel }],
            versionOptions: version
                ? [{ label: `v${version}`, value: version }]
                : undefined,
            label: imageLabel,
            description: (smeMetadata === null || smeMetadata === void 0 ? void 0 : smeMetadata.description)
                ? smeMetadata.description
                : undefined,
            group: smeMetadata && smeMetadata.is_template ? ImageGroup.Sagemaker : ImageGroup.Custom,
        };
        if (!imageMap[arnEnvironment]) {
            imageMap[arnEnvironment] = specMetaData;
        }
        else {
            const { kernelOptions } = imageMap[arnEnvironment];
            if (!kernelOptions.some(opt => opt.value === kernel)) {
                const newKernelOptions = [
                    ...kernelOptions,
                    { label: kernelName, value: kernel }
                ];
                imageMap[arnEnvironment].kernelOptions = newKernelOptions;
            }
            if (version) {
                const { versionOptions } = imageMap[arnEnvironment];
                if (!versionOptions.some(opt => opt.value === version)) {
                    const optionToAdd = {
                        label: `v${version}`,
                        value: version.toString()
                    };
                    const newVersionOptions = Array.isArray(versionOptions)
                        ? [...versionOptions, optionToAdd]
                        : [optionToAdd];
                    imageMap[arnEnvironment].versionOptions = newVersionOptions;
                }
            }
        }
    });
    return imageMap;
}
export { constructArnName, createImageMap, parseSpecName, parseSpecDisplayName, getImageOptionsFromMap, getSessionOptionsFromMap, ImageGroup, };
//# sourceMappingURL=studioHelpers.js.map