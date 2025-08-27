/* eslint-disable @typescript-eslint/no-var-requires */
const base = require('./jest.config.base.js');

module.exports = {
  ...base,
  roots: ['<rootDir>/src'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  setupFilesAfterEnv: [
    '<rootDir>/setupTests/setupTests.js',
    '<rootDir>/setupTests/setupFetch.js',
    '<rootDir>/setupTests/setupEvents.js',
    '<rootDir>/setupTests/setupRequestIdleCallback.js',
  ],
  testEnvironmentOptions:{
    url: "http://localhost",
  },
  moduleNameMapper: {
    '\\.(css|less)$': 'identity-obj-proxy',
    '\\.svg$': '<rootDir>/src/__mocks__/fileMock.ts',
  },
  globals: {
    ...base.globals,
  },
};