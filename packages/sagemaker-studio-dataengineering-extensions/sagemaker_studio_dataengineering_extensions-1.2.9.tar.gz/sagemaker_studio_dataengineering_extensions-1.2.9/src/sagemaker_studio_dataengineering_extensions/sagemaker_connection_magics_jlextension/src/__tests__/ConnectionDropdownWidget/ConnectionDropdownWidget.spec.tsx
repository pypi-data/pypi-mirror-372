import { ConnectionHeaderWidget } from '../../ConnectionDropdownWidget/ConnectionDropdownWidget';

describe('Connection Dropdown Widget', () => {
  it('makes sure connection dropdown widget gets initialized', function () {
    const headerWidget = new ConnectionHeaderWidget();
    jest.spyOn(headerWidget, 'update').mockReturnValue();

    expect(headerWidget).toBeDefined();

    // widget class gets applied correctly
    expect(headerWidget.hasClass('jp-connection-dropdown-widget')).toBeTruthy();

    // is not active when initialized
    expect(headerWidget.hasClass('jp-connection-dropdown-widget-active')).toBeFalsy();

    // activate header widget
    headerWidget.updateProps({ active: true, codeCell: undefined, interpreters: [], connections: [] });

    // active class is applied correctly
    expect(headerWidget.hasClass('jp-connection-dropdown-widget-active')).toBeTruthy();

    // de-activate header  widget
    headerWidget.updateProps({ active: false, codeCell: undefined, interpreters: [], connections: [] });

    // active class is removed correctly
    expect(headerWidget.hasClass('jp-connection-dropdown-widget-active')).toBeFalsy();
  });
});
