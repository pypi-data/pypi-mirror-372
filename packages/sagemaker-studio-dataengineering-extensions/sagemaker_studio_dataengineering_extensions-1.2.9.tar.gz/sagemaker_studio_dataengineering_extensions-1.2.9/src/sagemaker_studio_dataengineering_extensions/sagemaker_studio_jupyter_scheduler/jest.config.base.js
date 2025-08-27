const { defaults } = require('jest-config');

// jest doesn't support es6 modules, so these need to be transformed using jest-babel
const es6Modules = ['nanoid','vscode-ws-jsonrpc', 'y-protocols', 'lib0', '@jupyter'].join('|');

module.exports = {
  moduleFileExtensions: [...defaults.moduleFileExtensions, 'ts', 'tsx'],
  verbose: true,
  testEnvironmentOptions:{
    url: "http://localhost",
  },
  testMatch: [`<rootDir>/**/*.spec.ts`, `<rootDir>/**/*.spec.tsx`],
  preset: 'ts-jest/presets/js-with-babel',
  collectCoverage: true,
  coverageReporters: ['html'],
  transform: {
    '^.+\\.(ts|tsx)?$': 'ts-jest',
	  "^.+\\.(js|jsx)$": "babel-jest",
  },
  transformIgnorePatterns: [`/node_modules/(?!${es6Modules})`],
  globals: {
    'ts-jest': {
      isolatedModules: true,
      tsconfig: '<rootDir>/tsconfig.json',
    },
  },
  testEnvironment: 'jsdom',
};
