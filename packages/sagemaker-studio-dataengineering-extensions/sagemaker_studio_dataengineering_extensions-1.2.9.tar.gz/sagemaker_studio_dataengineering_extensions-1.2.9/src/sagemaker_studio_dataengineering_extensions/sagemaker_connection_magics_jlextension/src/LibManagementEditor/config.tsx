import { LabIcon } from '@jupyterlab/ui-components';
import React from 'react';

import libraryIconStr from '../../style/icons/md-library-icon.svg';
import mavenIconStr from '../../style/icons/maven-icon.svg';
import condaIconStr from '../../style/icons/conda-icon.svg';
import pypiIconStr from '../../style/icons/pypi-icon.svg';
import s3PathsIconStr from '../../style/icons/s3-paths-icon.svg';
import diskLocationPathsIconStr from '../../style/icons/disk-location-paths-icon.svg';
import otherPathsIconStr from '../../style/icons/other-paths-icon.svg';
import { ConnectionType } from '../constants';

const S3_PREFIX_REGEX = '^s3://.*';
const LOCAL_PREFIX_REGEX = '^(file:/|local:/).*';
const OTHER_PREFIX_REGEX = '^(hdfs://|http://|https://|ftp://).*';
const JAR_SUFFIX_REGEX = '(.jar)$';
const PYTHON_SUFFIX_REGEX = '(.py|.zip|.egg|.whl)$';

export const libMgmtIcon = new LabIcon({
  name: 'libmgmt:library-management-icon',
  svgstr: libraryIconStr,
});
export const mavenIcon = new LabIcon({
  name: 'libmgmt:maven-icon',
  svgstr: mavenIconStr,
});

export const condaIcon = new LabIcon({
  name: 'libmgmt:conda-icon',
  svgstr: condaIconStr,
});

export const pypiIcon = new LabIcon({
  name: 'libmgmt:pypi-icon',
  svgstr: pypiIconStr,
});

export const s3PathsIcon = new LabIcon({
  name: 'libmgmt:s3-paths-icon',
  svgstr: s3PathsIconStr,
});

export const diskLocationPathsIcon = new LabIcon({
  name: 'libmgmt:disk-location-paths-icon',
  svgstr: diskLocationPathsIconStr,
});

export const otherPathsIcon = new LabIcon({
  name: 'libmgmt:other-paths-icon',
  svgstr: otherPathsIconStr,
});

export const CONFIGS: { [key: string]: { [key: string]: configMetadata } } = {
  Jar: {
    MavenArtifacts: {
      title: 'Jar - Maven Artifacts',
      icon: mavenIcon,
      supportedConnectionType: [
        ConnectionType.SPARK_EMR_EC2,
        ConnectionType.SPARK_EMR_SERVERLESS,
      ],
      regex: '^([\\w\\.\\-]+):([\\w\\.\\-]+):([\\w\\.\\-]+)$',
      additionalDescription: [
        <div>Provide the Maven coordinates in the following format: groupId:artifactId:version</div>,
        <div>
          For more information on Maven coordinates, see&nbsp;
          {link('Spark Configuration', 'https://spark.apache.org/docs/latest/configuration.html#spark.jars.packages')}
        </div>,
      ],
    },
    S3Paths: {
      title: 'Jar - S3 Paths',
      icon: s3PathsIcon,
      supportedConnectionType: [
        ConnectionType.SPARK_EMR_EC2,
        ConnectionType.SPARK_EMR_SERVERLESS,
        ConnectionType.SPARK_GLUE,
      ],
      regex: `${S3_PREFIX_REGEX}${JAR_SUFFIX_REGEX}`,
      additionalDescription: [<div>Provide URLs starting with "s3" for the JAR files</div>],
    },
    LocalPaths: {
      title: 'Jar - Disk Location Paths',
      icon: diskLocationPathsIcon,
      supportedConnectionType: [ConnectionType.SPARK_EMR_EC2],
      regex: `${LOCAL_PREFIX_REGEX}${JAR_SUFFIX_REGEX}`,
      additionalDescription: [
        <div>Provide URLs starting with "file" for the JAR files</div>,
        <div>
          For more information on supported URLs, see&nbsp;
          {link(
            'Advanced Dependency Management',
            'https://spark.apache.org/docs/latest/submitting-applications.html#advanced-dependency-management'
          )}
        </div>,
        <div>
          To use a local path with EMR on EC2, configure the path in cluster configuration: livy-conf
          livy.file.local-dir-whitelist
        </div>,
        <div>
          For more information on cluster configuration, see&nbsp;
          {link(
            'Reconfigure an instance group in a running cluster',
            'https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-configure-apps-running-cluster.html'
          )}
        </div>,
      ],
    },
    OtherPaths: {
      title: 'Jar - Other Paths',
      icon: otherPathsIcon,
      supportedConnectionType: [ConnectionType.SPARK_EMR_EC2, ConnectionType.SPARK_EMR_SERVERLESS],
      regex: `${OTHER_PREFIX_REGEX}${JAR_SUFFIX_REGEX}`,
      additionalDescription: [
        <div>Provide URLs to JAR files that begin with one of the following: "hdfs", "http", "https", or "ftp"</div>,
        <div>
          For more information on supported URLs, see&nbsp;
          {link(
            'Advanced Dependency Management',
            'https://spark.apache.org/docs/latest/submitting-applications.html#advanced-dependency-management'
          )}
        </div>,
      ],
    },
  },
  Python: {
    CondaPackages: {
      title: 'Python - Conda Packages',
      icon: condaIcon,
      supportedConnectionType: [ConnectionType.IAM],
      // https://docs.conda.io/projects/conda-build/en/latest/resources/package-spec.html
      additionalDescription: [
        <div>Provide the package specification supported by Conda</div>,
        <div>
          For more information on package specification, see&nbsp;
          {link(
            'Conda package specification',
            'https://docs.conda.io/projects/conda-build/en/latest/resources/package-spec.html'
          )}
        </div>,
      ],
    },
    PyPIPackages: {
      title: 'Python - PyPI Packages',
      icon: pypiIcon,
      supportedConnectionType: [ConnectionType.SPARK_EMR_EC2, ConnectionType.SPARK_GLUE],
      additionalDescription: [
        <div>Provide the requirement specifiers supported by pip</div>,
        <div>
          For more information on supported requirement specifiers, see&nbsp;
          {link('pip install', 'https://pip.pypa.io/en/stable/cli/pip_install/')}
        </div>,
        <div>
          To use PyPI with EMR on EC2, provide the requirement specifiers in the format: packageName or
          packageName==version
        </div>,
        <div>
          WARNING: We do not recommend you to use pip in the JupyterLab environment. This could lead to an unstable environment .
          For more information, please refer to this {link('link', 'https://github.com/aws/sagemaker-distribution?tab=readme-ov-file#customizing-image')}.
        </div>,
      ],
    },
    S3Paths: {
      title: 'Python - S3 Paths',
      icon: s3PathsIcon,
      supportedConnectionType: [
        ConnectionType.SPARK_EMR_EC2,
        ConnectionType.SPARK_EMR_SERVERLESS,
        ConnectionType.SPARK_GLUE,
      ],
      regex: `${S3_PREFIX_REGEX}${PYTHON_SUFFIX_REGEX}`,
      additionalDescription: [
        <div>Provide URLs for one of the following file types: zip, egg, whl. URL must begin with "s3".</div>,
      ],
    },
    LocalPaths: {
      title: 'Python - Disk Location Paths',
      icon: diskLocationPathsIcon,
      supportedConnectionType: [ConnectionType.SPARK_EMR_EC2],
      regex: `${LOCAL_PREFIX_REGEX}${PYTHON_SUFFIX_REGEX}`,
      additionalDescription: [
        <div>Provide URLs for one of the following file types: zip, egg, whl. URL must begin with "file".</div>,
        <div>
          For more information on supported URLs, see&nbsp;
          {link(
            'Advanced Dependency Management',
            'https://spark.apache.org/docs/latest/submitting-applications.html#advanced-dependency-management'
          )}
        </div>,
        <div>
          To use a local path with EMR on EC2, configure the path in cluster configuration: livy-conf
          livy.file.local-dir-whitelist
        </div>,
        <div>
          For more information on cluster configuration, see&nbsp;
          {link(
            'Reconfigure an instance group in a running cluster',
            'https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-configure-apps-running-cluster.html'
          )}
        </div>,
      ],
    },
    OtherPaths: {
      title: 'Python - Other Paths',
      icon: otherPathsIcon,
      supportedConnectionType: [ConnectionType.SPARK_EMR_EC2, ConnectionType.SPARK_GLUE],
      regex: `${OTHER_PREFIX_REGEX}${PYTHON_SUFFIX_REGEX}`,
      additionalDescription: [
        <div>
          Provide URLs for one of the following file types: zip, egg, whl. URL must begin with "hdfs", "http", "https",
          or "ftp".
        </div>,
        <div>
          For more information on supported URLs, see&nbsp;
          {link(
            'Advanced Dependency Management',
            'https://spark.apache.org/docs/latest/submitting-applications.html#advanced-dependency-management'
          )}
        </div>,
      ],
    },
  },
};

export interface configMetadata {
  title: string;
  icon: LabIcon;
  supportedConnectionType: ConnectionType[];
  regex?: string;
  additionalDescription?: JSX.Element[];
}

export const initConfig = {
  ApplyChangeToSpace: false,
  Jar: {
    MavenArtifacts: [],
    S3Paths: [],
    LocalPaths: [],
    OtherPaths: [],
  },
  Python: {
    CondaPackages: {
      Channels: [],
      PackageSpecs: [],
    },
    PyPIPackages: [],
    S3Paths: [],
    LocalPaths: [],
    OtherPaths: [],
  },
};

function link(linkName: string, href: string) {
  return (
    <a target="_blank" style={{ color: 'var(--jp-content-link-color)' }} rel="noopener noreferrer" href={href}>
      {linkName}
    </a>
  );
}
