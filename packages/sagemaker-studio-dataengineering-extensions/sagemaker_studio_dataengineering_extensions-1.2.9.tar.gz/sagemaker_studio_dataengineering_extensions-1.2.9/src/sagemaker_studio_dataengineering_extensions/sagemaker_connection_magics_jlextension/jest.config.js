const jestJupyterLab = require('@jupyterlab/testutils/lib/jest-config');

const esModules = [
    '@codemirror/',
    '@jupyter/',
    '@microsoft/',
    '@jupyter-lsp/',
    'vscode-languageserver-types',
    '@jupyterlab/',
    'lib0',
    'nanoid',
    'vscode-ws-jsonrpc',
    'y\\-protocols',
    'y\\-websocket',
    'yjs',
    'exenv-es6',
    '@amzn',
    'uuid'
].join('|');

const jlabConfig = jestJupyterLab(__dirname);

const {
  moduleFileExtensions,
  moduleNameMapper,
  preset,
  setupFilesAfterEnv,
  setupFiles,
  testPathIgnorePatterns,
  transform
} = jlabConfig;

module.exports = {
  moduleFileExtensions,
  moduleNameMapper,
  preset,
  setupFilesAfterEnv,
  setupFiles,
  transform,
  automock: false,
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/.ipynb_checkpoints/*'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['lcov', 'text'],
  globals: {
    'ts-jest': {
      tsconfig: 'tsconfig.json'
    }
  },
  testEnvironment: 'jsdom',
  verbose: true,
  testRegex: 'src/.*/.*.spec.ts[x]?$',
  testPathIgnorePatterns: [
      ...testPathIgnorePatterns,
      '/dist/'
  ],
  transformIgnorePatterns: [`/node_modules/(?!${esModules}).+`
],
  transform: {
    '^.+\\.[t|j]sx?$': 'babel-jest',
  },
  moduleNameMapper: {
    '\\.svg$': '<rootDir>/src/__mocks__/filemock.ts',
  },
};