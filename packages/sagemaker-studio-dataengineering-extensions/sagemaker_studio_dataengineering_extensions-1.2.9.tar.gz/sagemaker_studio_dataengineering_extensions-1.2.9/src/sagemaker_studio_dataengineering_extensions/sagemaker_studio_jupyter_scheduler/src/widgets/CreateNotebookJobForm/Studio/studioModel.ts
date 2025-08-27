export interface KernelSpecResponse {
  default: string;
  kernelspecs: ImagesMapStudio;
}

export interface ImagesMapStudio {
  [key: string]: KernelSpecItem;
}

export interface KernelSpecItem {
  name: string;
  spec: KernelSpec;
  resources: KernelSpecResources;
}

export interface KernelSpecResources {
  'logo-64x64': string;
  'logo-32x32': string;
}

export interface KernelSpec {
  argv: string[];
  display_name: string;
  language: string;
  metadata: KernelSpecMetadata;
}

export interface KernelSpecMetadata {
  sme_metadata: SmeMetadata;
  instance_type: string;
}

export interface SmeMetadata {
  environment_arn: string;
  display_name: string;
  description?: string;
  gpu_optimized?: boolean;
  is_template?: boolean;
  supported_instance_types?: string[];
}
