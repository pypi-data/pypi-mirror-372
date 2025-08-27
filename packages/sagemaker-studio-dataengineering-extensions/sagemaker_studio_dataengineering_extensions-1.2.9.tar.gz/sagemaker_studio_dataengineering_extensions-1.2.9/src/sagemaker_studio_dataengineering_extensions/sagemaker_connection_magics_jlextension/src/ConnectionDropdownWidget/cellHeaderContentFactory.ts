import { JupyterFrontEnd, LabShell } from '@jupyterlab/application';
import { Cell, CodeCell, type ICellHeader } from '@jupyterlab/cells';
import { IEditorServices } from '@jupyterlab/codeeditor';
import { Notebook, NotebookPanel } from '@jupyterlab/notebook';

import { Constants } from '../constants';
import { getMainPanels } from '../utils';
import {
  SageMakerConnectionSummary,
  getDefaultShowCellLevelConnectionSelection,
  getInterpreterList,
  getSqlOnlyConnections,
  getSqlOnlyInterpreterList,
  listDataZoneConnections,
} from '../utils/DropdownUtils';
import { ConnectionHeaderWidget } from './ConnectionDropdownWidget';

type CustomContentFactoryOptions = Cell.ContentFactory.IOptions & {
  app: JupyterFrontEnd;
  editorServices: IEditorServices;
};

export class CellHeaderContentFactory extends NotebookPanel.ContentFactory {
  private notebookPanels: Set<string>;

  private static interpreters: { label: string; value: string }[];
  private static sqlOnlyInterpreters: { label: string; value: string }[];
  private static connections: SageMakerConnectionSummary[];
  private static sqlOnlyConnections: SageMakerConnectionSummary[];

  constructor(private options: CustomContentFactoryOptions) {
    super(options);
    this.notebookPanels = new Set<string>();
    this.initialize();
  }

  private async initialize(): Promise<void> {
    const app = this.options.app;
    if (app.shell instanceof LabShell) {
      await app.shell.restored;

      const mainNotebookPanels = getMainPanels(app);

      mainNotebookPanels.forEach(notebookPanel => {
        this.notebookPanels.add(notebookPanel.id);
        this.connectCellHeader(notebookPanel);
      });

      app.shell.activeChanged.connect((_, changed) => {
        const notebookPanel = changed.newValue;
        if (notebookPanel && notebookPanel instanceof NotebookPanel) {
          if (this.notebookPanels.has(notebookPanel.id)) {
            // If new active notebook panel is an existing panel, just refresh the cell header.
            this.updateCellHeader(notebookPanel);
          } else {
            // If new active notebook panel is a new created panel, connect cell header to content and kernel signal
            this.connectCellHeader(notebookPanel);
            this.notebookPanels.add(notebookPanel.id);
          }
        }
      }, this);

      await this.refreshConnections(false);
    }
  }

  private async refreshConnections(forceRefresh: boolean) {
    try {
      let connectionList = await listDataZoneConnections(forceRefresh);
      CellHeaderContentFactory.connections = connectionList;
      CellHeaderContentFactory.sqlOnlyConnections = getSqlOnlyConnections(connectionList);
      CellHeaderContentFactory.interpreters = getInterpreterList(connectionList);
      CellHeaderContentFactory.sqlOnlyInterpreters = getSqlOnlyInterpreterList(connectionList);

      // Force cellHeader rerender in current notebook panel
      const app = this.options.app;
      if (app.shell instanceof LabShell) {
        await app.shell.restored;
        const mainNotebookPanel = app.shell.activeWidget;

        if (mainNotebookPanel instanceof NotebookPanel) {
          this.updateCellHeader(mainNotebookPanel);
        }
      }
    } catch (error) {
      console.error(error);
    }
  }

  private updateCellHeader(notebookPanel: NotebookPanel) {
    this.updateHeaderContent(
      notebookPanel.content,
      notebookPanel.sessionContext.session?.kernel?.name,
      notebookPanel.content.activeCell?.model.id,
      notebookPanel.sessionContext.name.endsWith('.sqlnb')
    );
  }

  private connectCellHeader(notebookPanel: NotebookPanel) {
    const isSqlnb = notebookPanel.sessionContext.name.endsWith('.sqlnb');
    notebookPanel.content.modelContentChanged.connect(notebook => {
      this.updateHeaderContent(
        notebook,
        notebookPanel.sessionContext.session?.kernel?.name,
        notebookPanel.content.activeCell?.model.id,
        isSqlnb
      );
    });
    notebookPanel.content.activeCellChanged.connect((notebook, cell) => {
      this.updateHeaderContent(notebook, notebookPanel.sessionContext.session?.kernel?.name, cell?.model.id, isSqlnb);
    });
    notebookPanel.sessionContext.kernelChanged.connect((sessionContext, kernel) => {
      this.updateHeaderContent(
        notebookPanel.content,
        kernel.newValue?.name,
        notebookPanel.content.activeCell?.model.id,
        isSqlnb
      );
    });
    notebookPanel.disposed.connect(() => {
      this.notebookPanels.delete(notebookPanel.id);
    });
    this.updateCellHeader(notebookPanel);
  }

  public async updateHeaderContent(
    notebook: Notebook,
    kernelName: string | undefined,
    activeCellId: string | undefined,
    isSqlnb?: boolean
  ): Promise<void> {
    for (const cell of notebook.widgets) {
      await cell.ready;
      if (cell instanceof CodeCell && cell.model) {
        await this.updateHeaderContentForCell(cell, kernelName, activeCellId, isSqlnb);
      }
    }
  }

  private async updateHeaderContentForCell(
    cell: CodeCell,
    kernelName: string | undefined,
    activeCellId: string | undefined,
    isSqlnb?: boolean
  ): Promise<void> {
    const headerWidget = this.getConnectionHeaderWidget(cell);
    const active =
      kernelName != Constants.SAGEMAKER_MAGIC_SUPPORTED_KERNEL_NAME
        ? false
        : cell.model.id === activeCellId || getDefaultShowCellLevelConnectionSelection();
    headerWidget?.updateProps({
      active: active,
      codeCell: cell,
      interpreters: isSqlnb ? CellHeaderContentFactory.sqlOnlyInterpreters : CellHeaderContentFactory.interpreters,
      connections: isSqlnb ? CellHeaderContentFactory.sqlOnlyConnections : CellHeaderContentFactory.connections,
      onRefresh: () => this.refreshConnections(true),
    });
  }

  /**
   * Iterate through the cell's layout widgets to find the connection header widget of this cell
   * @param cell cell that potentiall contains the connection header widget
   * @returns connection header widget or undefined
   */
  private getConnectionHeaderWidget(cell: CodeCell): ConnectionHeaderWidget | undefined {
    const widgets = Array.from(cell.children());
    return widgets.find((widget): widget is ConnectionHeaderWidget => widget instanceof ConnectionHeaderWidget);
  }

  /**
   * The factory method that gets called for each cell to retrieve the header widget element.
   * It returns the ConnectionHeaderWidget which responsible for rendering cell header with connection dropdown.
   * @returns ConnectionHeaderWidget which is the instance of ICellHeader
   */
  public override createCellHeader(): ICellHeader {
    return new ConnectionHeaderWidget();
  }
}
