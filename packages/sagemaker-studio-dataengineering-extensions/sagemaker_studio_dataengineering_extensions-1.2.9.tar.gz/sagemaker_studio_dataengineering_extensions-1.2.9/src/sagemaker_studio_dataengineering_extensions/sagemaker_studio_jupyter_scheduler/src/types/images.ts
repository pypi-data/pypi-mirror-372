interface KernelOption {
  name: string;
  displayName: string;
}

interface VersionOption {
  displayName: string;
  version: string;
}

interface ImageMapValue {
  kernelOptions: KernelOption[];
  versionOptions?: VersionOption[];
  arnEnvironment: string;
  displayName: string;
  group: string;
  description?: string;
}

type ImagesMap = { [imageArn: string]: ImageMapValue };

export { ImageMapValue, ImagesMap };
