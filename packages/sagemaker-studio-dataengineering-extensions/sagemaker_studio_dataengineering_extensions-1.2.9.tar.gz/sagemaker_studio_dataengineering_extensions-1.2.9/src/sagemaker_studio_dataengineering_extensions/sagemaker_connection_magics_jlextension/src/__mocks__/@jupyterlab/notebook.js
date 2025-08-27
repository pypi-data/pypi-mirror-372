const mockINotebookModel = {
  kernelChanged: jest.fn(),
  contentChanged: jest.fn(),
  getMetadata: jest.fn(),
  setMetadata: jest.fn()
};

module.exports = {
  INotebookModel: mockINotebookModel,
};