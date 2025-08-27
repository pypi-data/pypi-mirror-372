import { JSONSchema7 } from 'json-schema';

import { CONFIGS } from './config';

/**
 * According to spark.jars.packages meaning in https://spark.apache.org/docs/latest/configuration.html
 * The coordinate should be groupId:artifactId:version
 * https://maven.apache.org/pom.html#Maven_Coordinates
 */
const MAVEN_COORDINATES_SCHEMA: JSONSchema7 = {
  type: 'string',
  pattern: CONFIGS.Jar.MavenArtifacts.regex,
};

// https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_S3Location.html
const S3_JAR_PATH_SCHEMA: JSONSchema7 = {
  type: 'string',
  pattern: CONFIGS.Jar.S3Paths.regex,
  maxLength: 2048,
};

const LOCAL_JAR_PATH_SCHEMA: JSONSchema7 = {
  type: 'string',
  pattern: CONFIGS.Jar.LocalPaths.regex,
};

// https://spark.apache.org/docs/latest/submitting-applications.html#advanced-dependency-management
const OTHER_JAR_PATH_SCHEMA: JSONSchema7 = {
  type: 'string',
  pattern: CONFIGS.Jar.OtherPaths.regex,
};

const CONDA_PACKAGE_SPECIFICATION_SCHEMA: JSONSchema7 = {
  type: 'string',
};

const CONDA_CHANNEL_SCHEMA: JSONSchema7 = {
  type: 'string',
};

// https://pip.pypa.io/en/stable/reference/requirement-specifiers/
const PYPI_PACKAGE_SPECIFICATION_SCHEMA: JSONSchema7 = {
  type: 'string',
};

// https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_S3Location.html
const S3_PYTHON_PATH_SCHEMA: JSONSchema7 = {
  type: 'string',
  pattern: CONFIGS.Python.S3Paths.regex,
  maxLength: 2048,
};

const LOCAL_PYTHON_PATH_SCHEMA: JSONSchema7 = {
  type: 'string',
  pattern: CONFIGS.Python.LocalPaths.regex,
};

// https://spark.apache.org/docs/latest/submitting-applications.html#advanced-dependency-management
const OTHER_PYTHON_PATH_SCHEMA: JSONSchema7 = {
  type: 'string',
  pattern: CONFIGS.Python.OtherPaths.regex,
};

export const LIBRARY_CONFIG_SCHEMA: JSONSchema7 = {
  title: 'Library management configuration',
  description: 'Library management configuration',
  type: ['object', 'null'],
  properties: {
    Jar: {
      type: 'object',
      title: 'Jar',
      properties: {
        MavenArtifacts: {
          title: 'Maven Artifacts',
          type: ['array', 'null'],
          items: MAVEN_COORDINATES_SCHEMA,
        },
        S3Paths: {
          title: 'S3 Paths',
          type: ['array', 'null'],
          items: S3_JAR_PATH_SCHEMA,
        },
        LocalPaths: {
          title: 'Disk Location Paths',
          type: ['array', 'null'],
          items: LOCAL_JAR_PATH_SCHEMA,
        },
        OtherPaths: {
          title: 'Other Paths',
          type: ['array', 'null'],
          items: OTHER_JAR_PATH_SCHEMA,
        },
      },
    },
    Python: {
      type: 'object',
      title: 'Python',
      properties: {
        CondaPackages: {
          title: 'Conda Packages',
          type: ['object', 'null'],
          properties: {
            Channels: {
              title: 'Channel',
              type: ['array', 'null'],
              items: CONDA_CHANNEL_SCHEMA,
            },
            PackageSpecs: {
              title: 'Package Spec',
              type: ['array', 'null'],
              items: CONDA_PACKAGE_SPECIFICATION_SCHEMA,
            },
          },
        },
        PyPIPackages: {
          title: 'PyPI Packages',
          type: ['array', 'null'],
          items: PYPI_PACKAGE_SPECIFICATION_SCHEMA,
        },
        S3Paths: {
          title: 'S3 Paths',
          type: ['array', 'null'],
          items: S3_PYTHON_PATH_SCHEMA,
        },
        LocalPaths: {
          title: 'Disk Location Paths',
          type: ['array', 'null'],
          items: LOCAL_PYTHON_PATH_SCHEMA,
        },
        OtherPaths: {
          title: 'Other Paths',
          type: ['array', 'null'],
          items: OTHER_PYTHON_PATH_SCHEMA,
        },
      },
    },
  },
};
