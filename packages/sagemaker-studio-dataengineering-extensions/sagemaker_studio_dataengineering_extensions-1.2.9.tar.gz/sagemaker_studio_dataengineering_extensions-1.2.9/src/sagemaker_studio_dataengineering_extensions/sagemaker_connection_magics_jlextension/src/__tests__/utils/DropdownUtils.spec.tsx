import {
  getCellConnectionName,
  getInterpreterList,
  getSqlOnlyConnections,
  getSqlOnlyInterpreterList,
} from '../../utils/DropdownUtils';

jest.mock('@jupyterlab/notebook');

jest.mock('@jupyterlab/cells');

describe('test getInterpreterList', () => {
  it('test getInterpreterList with empty connection list', function () {
    expect(getInterpreterList([])).toEqual([
      { label: 'Connection Type', value: '' },
      { label: '-', value: '-', disabled: true },
    ]);
  });

  it('test getInterpreterList with all types connection list', function () {
    expect(
      getInterpreterList([
        { name: 'emr-s.test', type: 'SPARK_EMR_SERVERLESS', enableTrustedIdentityPropagation: false },
        { name: 'emr.test', type: 'SPARK_EMR_EC2', enableTrustedIdentityPropagation: false },
        { name: 'project.lakehouse', type: 'REDSHIFT', enableTrustedIdentityPropagation: false },
        { name: 'project.redshift', type: 'REDSHIFT', enableTrustedIdentityPropagation: false },
        { name: 'project.athena', type: 'ATHENA', enableTrustedIdentityPropagation: false },
        { name: 'project.iam', type: 'IAM', enableTrustedIdentityPropagation: false },
        { name: 'project.spark', type: 'SPARK_GLUE', enableTrustedIdentityPropagation: false },
      ])
    ).toEqual([
      { label: 'Connection Type', value: '' },
      { label: '-', value: '-', disabled: true },
      { label: 'PySpark', value: 'pyspark' },
      { label: 'ScalaSpark', value: 'scalaspark' },
      { label: 'SQL', value: 'sql' },
      { label: 'Local Python', value: 'local' },
    ]);
  });
});

describe('test getSqlOnlyInterpreterList', () => {
  it('test getSqlOnlyInterpreterList with empty connection list', function () {
    expect(getSqlOnlyInterpreterList([])).toEqual([
      { label: 'Connection Type', value: '' },
      { label: '-', value: '-', disabled: true },
    ]);
  });

  it('test getSqlOnlyInterpreterList with all types connection list', function () {
    expect(
      getSqlOnlyInterpreterList([
        { name: 'emr-s.test', type: 'SPARK_EMR_SERVERLESS', enableTrustedIdentityPropagation: false },
        { name: 'emr.test', type: 'SPARK_EMR_EC2', enableTrustedIdentityPropagation: false },
        { name: 'project.lakehouse', type: 'REDSHIFT', enableTrustedIdentityPropagation: false },
        { name: 'project.redshift', type: 'REDSHIFT', enableTrustedIdentityPropagation: false },
        { name: 'project.athena', type: 'ATHENA', enableTrustedIdentityPropagation: false },
        { name: 'project.iam', type: 'IAM', enableTrustedIdentityPropagation: false },
        { name: 'project.spark', type: 'SPARK_GLUE', enableTrustedIdentityPropagation: false },
      ])
    ).toEqual([
      { label: 'Connection Type', value: '' },
      { label: '-', value: '-', disabled: true },
      { label: 'SQL', value: 'sql' },
    ]);
  });
});

describe('test getSqlOnlyConnections', () => {
  it('test getSqlOnlyInterpreterList with empty connection list', function () {
    expect(getSqlOnlyConnections([])).toEqual([]);
  });

  it('test getSqlOnlyInterpreterList with all types connection list', function () {
    expect(
      getSqlOnlyConnections([
        { name: 'emr-s.test', type: 'SPARK_EMR_SERVERLESS', enableTrustedIdentityPropagation: false },
        { name: 'emr.test', type: 'SPARK_EMR_EC2', enableTrustedIdentityPropagation: false },
        { name: 'project.lakehouse', type: 'REDSHIFT', enableTrustedIdentityPropagation: false },
        { name: 'project.redshift', type: 'REDSHIFT', enableTrustedIdentityPropagation: false },
        { name: 'project.athena', type: 'ATHENA', enableTrustedIdentityPropagation: false },
        { name: 'project.iam', type: 'IAM', enableTrustedIdentityPropagation: false },
        { name: 'project.spark', type: 'SPARK_GLUE', enableTrustedIdentityPropagation: false },
      ])
    ).toEqual([
      { name: 'project.lakehouse', type: 'REDSHIFT' },
      { name: 'project.redshift', type: 'REDSHIFT' },
      { name: 'project.athena', type: 'ATHENA' },
    ]);
  });
});

describe('test getCellConnectionName', () => {
  it('test getCellConnectionName with undefined code cell', function () {
    expect(getCellConnectionName(undefined)).toEqual('project.python');
  });
});
