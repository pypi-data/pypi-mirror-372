import React from 'react';
import { Cell as JupyterCell, ICellModel } from '@jupyterlab/cells';
import { IStateDB } from '@jupyterlab/statedb';
import { NotebookActions, NotebookPanel, NotebookTracker } from '@jupyterlab/notebook';
import {
  IComm,
  IKernelConnection
} from '@jupyterlab/services/lib/kernel/kernel';
import { ICommMsgMsg } from '@jupyterlab/services/lib/kernel/messages';
import { PanelLayout } from '@lumino/widgets';
import CurrentCellTracker from './current-cell';
import { CellWidget } from '../components';
import { ReactWidget } from '@jupyterlab/apputils';
import { getConnectionTypeMap, isSparkCell, getCellConnectionName } from './utils'
import { SPARK_MONITOR_CELL_WIDGET_CLASS } from './constants';
import dummy_data from './dummy-data'

import type { NotebookStore } from '../store/notebook';
import { PLUGIN_ID } from '.';
import { KernelMessage } from '@jupyterlab/services';
export default class JupyterLabSparkMonitor {
  currentCellTracker: CurrentCellTracker;
  cellExecCountSinceSparkJobStart = 0;
  kernel?: IKernelConnection;

  /** Communication object with the kernel. */
  comm?: IComm;

  lastExecutedCellModel?: ICellModel;

  constructor(
    private notebookPanel: NotebookPanel,
    private notebookStore: NotebookStore,
    private stateDb: IStateDB,
    private notebooks: NotebookTracker
  ) {
    this.createCellReactElements();
    this.currentCellTracker = new CurrentCellTracker(notebookPanel);
    this.kernel = (notebookPanel as any).session
      ? (this.notebookPanel as any).session.kernel
      : this.notebookPanel.sessionContext.session?.kernel;

    // Fixes Reloading the browser
    this.startComm();

    // load connection list in advance
    getConnectionTypeMap()

    // Fixes Restarting the Kernel
    this.kernel?.statusChanged.connect((_, status) => {
      if (status === 'restarting') {
        // Add safety check for currentCellTracker
        if (this.currentCellTracker) {
          this.currentCellTracker.cellReexecuted = false;
        }
        this.startComm();
      }
    });

    // listen for cell removed
    this.notebookPanel.content.model?.cells.changed.connect((_, data) => {
      if (data.type === 'remove') {
        data.oldValues.forEach(cell => {
          notebookStore.onCellRemoved(cell.id);
        });
      }
    });

    NotebookActions.executionScheduled.connect(async (_, args) => {
      // execute python code to get connection type
      // if (this.kernel) {
      //   const code = `
      //   txt = 'adsfasdfas'
      //   txt`
      //   const result = await this.executeCode({code})
      //   console.log(`result is ${result}`)
      // }

      let cell: JupyterCell;
      cell = args["cell"];
      const model = cell.model

      const cellContent = model?.sharedModel.source

      if (cellContent != undefined && !isSparkCell(cell)) {
        return
      }

      this.notebookStore.clearAllData()

      // console.log(`executing cell with id ${model.id}`)
      this.lastExecutedCellModel = model

      // this.loadDummyData()

      const cellConnectionName = getCellConnectionName(cell)

      if (this.comm && cell && cellConnectionName){
        this.comm.send({ msgtype: 'newExecution', content: {
          cell_id: model.id,
          connection_name : cellConnectionName
        }})
      }
    });

    NotebookActions.executed.connect((_, args) => {
      let cell: JupyterCell;
      cell = args["cell"];
      if (this.comm && cell){
        this.comm.send({ msgtype: 'executed', content: {}})
      }
    });

  }

  getNoteBookPanel() {
    return this.notebookPanel
  }

  async executeCode(
    code: KernelMessage.IExecuteRequestMsg['content']
  ): Promise<string> {
    const kernel = this.kernel;
    if (!kernel) {
      throw new Error('Session has no kernel.');
    }
    return new Promise<string>((resolve, reject) => {
      const future = kernel.requestExecute(code, false, undefined);
      future.onIOPub = (msg: KernelMessage.IIOPubMessage): void => {
        console.log(`onIOPub : ${msg}`)
        const msgType = msg.header.msg_type;
        if (msgType === 'execute_result') {
          const content = (msg as KernelMessage.IExecuteResultMsg).content.data[
            'text/plain'
          ] as string;
          resolve(content);
        } else if (msgType === 'error') {
          console.error('Kernel operation failed', msg.content);
          reject(msg.content);
        }
      };
    });
  }

  async createCellReactElements() {
    const createElementIfNotExists = async (cellModel: ICellModel) => {
      if (cellModel.type === 'code') {

        const codeCell = this.notebookPanel.content.widgets.find(
          widget => widget.model === cellModel
        );

        if (codeCell && !codeCell.node.querySelector('.sparkMonitorCellRoot')) {
          // delay to ensure widget is added to the last one
          await codeCell.ready;

          const widget = ReactWidget.create(
            React.createElement(CellWidget, {
              notebookId: this.notebookPanel.id,
              cellId: cellModel.id
            })
          );
          widget.addClass(SPARK_MONITOR_CELL_WIDGET_CLASS);
          // console.log(`adding widget for cell id ${cellModel.id}`)

          const panel = (codeCell.layout as PanelLayout);
          panel.addWidget(widget);
          codeCell.update();
        }
      }
    };

    const cells = this.notebookPanel.context.model.cells;

    // Ensure new cells created have a monitoring display
    cells.changed.connect(async (cells, cell) => {
      if (cell.type != "add") return
      createElementIfNotExists(cells.get(cell.newIndex))
    });

    // Do it the first time
    for (let i = 0; i < cells.length; i += 1) {
      createElementIfNotExists(cells.get(i));
    }
  }

  wait(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  toggleAll() {
    this.notebookStore.toggleHideAllDisplays();
  }

  startComm() {
    console.log('SparkMonitor: Starting Comm with kernel.');
    this.currentCellTracker.ready().then(() => {
      this.comm =
        'createComm' in (this.kernel || {})
          ? this.kernel?.createComm('SparkMonitor')
          : (this.kernel as any).connectToComm('SparkMonitor');
      if (!this.comm) {
        console.warn('SparkMonitor: Unable to connect to comm');
        return;
      }
      this.comm.open({ msgtype: 'openfromfrontend' });
      this.comm.onMsg = message => {
        this.handleMessage(message);
      };
      this.comm.onClose = message => {
        // noop
      };
      console.log('SparkMonitor: Connection with comms established');
    });
  }

  getLastExecutedCellModel() {
    return this.lastExecutedCellModel
  }

  getActiveCell() {
    return this.notebooks.activeCell;
  }

  setLastExecutedCellModelWithId(lastExecutedCellModelId: string) {
    const codeCell = this.notebookPanel.content.widgets.find(
      widget => widget.model.id === lastExecutedCellModelId
    );
    if (codeCell) {
      this.setLastExecutedCellModel(codeCell.model)
    } else {
      console.error(`sparkmonitor: cannot find last executed cell with id ${lastExecutedCellModelId}`)
    }
  }

  setLastExecutedCellModel(lastExecutedCellModel: ICellModel) {
    this.lastExecutedCellModel = lastExecutedCellModel
  }

  onSparkJobStart(data: any) {
    // Add safety check for currentCellTracker initialization race condition
    if (!this.currentCellTracker) {
      console.warn('SparkMonitor: currentCellTracker not initialized yet, deferring onSparkJobStart');
      return;
    }
    
    const cell = this.currentCellTracker.getActiveCell();
    if (!cell) {
      console.warn('SparkMonitor: Job started with no running cell.');
      return;
    }
    // See if we have a new execution. If it's new (a cell has been run again) we need to clear the cell monitor
    const newExecution =
      this.currentCellTracker.getNumCellsExecuted() >
      this.cellExecCountSinceSparkJobStart;
    if (newExecution) {
      this.cellExecCountSinceSparkJobStart =
        this.currentCellTracker.getNumCellsExecuted();
      this.notebookStore.onCellExecutedAgain(cell.model.id);
    }
    this.notebookStore.onSparkJobStart(cell.model.id, data);
  }

  onSparkStageSubmitted(data: any) {
    // Add safety check for currentCellTracker initialization race condition
    if (!this.currentCellTracker) {
      console.warn('SparkMonitor: currentCellTracker not initialized yet, deferring onSparkStageSubmitted');
      return;
    }
    
    const cell = this.currentCellTracker.getActiveCell();
    if (!cell) {
      console.warn('SparkMonitor: Stage started with no running cell.');
      return;
    }
    this.notebookStore.onSparkStageSubmitted(cell.model.id, data);
  }

  async handleMessage(msg: ICommMsgMsg) {
    if (!msg.content.data.msgtype) {
      console.warn('SparkMonitor: Unknown message');
    }
    if (msg.content.data.msgtype === 'fromscala') {
      const data: any = msg.content.data.msg;
      switch (data.msgtype) {
        case 'sparkJobStart':
          this.onSparkJobStart(data);
          break;
        case 'sparkJobEnd':
          this.notebookStore.onSparkJobEnd(data);
          break;
        case 'sparkStageSubmitted':
          this.onSparkStageSubmitted(data);
          break;
        case 'sparkStageCompleted':
          this.notebookStore.onSparkStageCompleted(data);
          break;
        case 'sparkStageActive':
          this.notebookStore.onSparkStageActive(data);
          break;
        case 'sparkTaskStart':
          this.notebookStore.onSparkTaskStart(data);
          break;
        case 'sparkTaskEnd':
          this.notebookStore.onSparkTaskEnd(data);
          break;
        case 'sparkApplicationStart':
          this.notebookStore.onSparkApplicationStart(data);
          break;
        case 'sparkApplicationEnd':
          // noop
          break;
        case 'sparkExecutorAdded':
          this.notebookStore.onSparkExecutorAdded(data);
          break;
        case 'sparkExecutorRemoved':
          this.notebookStore.onSparkExecutorRemoved(data);
          break;
        case 'clean':
          console.info(`clean sparkmonitor data`)
          this.clearAllData()
          break;
        case 'log':
          console.info(`SparkMonitor: log msg: ${JSON.stringify(data?.msg)}`)
          break;
        case 'error':
          this.onHandleError(JSON.stringify(data?.msg))
          break;
        case 'sparkData':
          await this.stateDb.save(PLUGIN_ID, { 
            'data' : data,
            'lastExecutedCellId': this.getLastExecutedCellId() 
          })
          this.onHandleSparkData(data)
          break;
        default:
          console.warn('SparkMonitor: Unknown message');
          break;
      }
    }
  }

  onHandleError(msg: string) {
    console.log(msg)
  }

  async clearAllData() {
    this.notebookStore.clearAllData()

    // clear saved data as well
    await this.stateDb.remove(PLUGIN_ID)
  }

  onHandleSparkData(data:any, lastExecutedCellId:string | undefined=undefined){
    // console.log(`spark data is ${JSON.stringify(data)}`)
    if (lastExecutedCellId) {
      this.setLastExecutedCellModelWithId(lastExecutedCellId);
    }
    this.notebookStore.clearAllData()
    this.notebookStore.onSparkJobStarted(this.getLastExecutedCellId())

    // Process session info if available - now cell-specific
    const cellId = this.getLastExecutedCellId();
    if (data.sessionInfo && cellId) {
      // Ensure cell exists and update session info for SPECIFIC cell only
      const cell = this.notebookStore.ensureCell(cellId);
      cell.updateSessionInfo(data.sessionInfo);
      console.log(`[Spark Monitor] Updated session info for cell ${cellId}:`, {
        connection_name: data.sessionInfo.connection_name,
        connection_type: data.sessionInfo.connection_type
      });
    } else if (cellId) {
      const cell = this.notebookStore.ensureCell(cellId);
      cell.updateSessionInfo(undefined);
      console.log(`[Spark Monitor] Cleared session info for cell ${cellId}`);
    }

    this.onGetSparkApplicationStatus(data.sparkApplicationStatus);
    this.onGetSparkExecutorStatus(data.sparkExecutorStatus);
    this.onGetSparkJobStatus(data.sparkJobStatus);
    this.onGetSparkStageStatus(data.sparkStageStatus);
    this.onGetSparkTaskStatus(data.sparkTaskStatus)
  }

  onGetSparkApplicationStatus(json: any) {
    this.notebookStore.onSparkApplicationStart({
      appId: json?.id,
      appName: json?.name,
      appAttemptId: Object.keys(json?.attempts).length
    })
  }

  onGetSparkExecutorStatus(json: any) {
    let totalCores = 0;
    let numExecutors = 0;

    const cell = this.getLastExecutedCellModel();
    if (!cell) {
      console.warn('SparkMonitor: Job started with no running cell.');
      return;
    }

    for (const executor of json) {
      if (executor.isActive) {
        totalCores += executor.totalCores;
        numExecutors += 1;
      }
    }

    this.notebookStore.onSparkExecutorUpdated(cell.id, {
      numTotalCores: totalCores,
      numExecutors: numExecutors,
      rawData: json
    })

  }

  onGetSparkJobStatus(data: any) {
    // get cell id
    const cell = this.getLastExecutedCellModel();
    if (!cell) {
      console.warn('SparkMonitor: Job started with no running cell.');
      return;
    }

    this.notebookStore.onSparkJobStatusUpdate(cell.id, data)
  }

  onGetSparkStageStatus(data: any) {
    // get cell id
    const cell = this.getLastExecutedCellModel();
    if (!cell) {
      console.warn('SparkMonitor: Job started with no running cell.');
      return;
    }

    this.notebookStore.onSparkStageStatusUpdate(cell.id, data)
  }

  onGetSparkTaskStatus(data: any) {
    this.notebookStore.onSparkTaskStatusUpdate(data)
  }

  getLastExecutedCellId() {
    const cell = this.getLastExecutedCellModel();
    if (!cell) {
      console.warn('SparkMonitor: Job started with no running cell.');
      return;
    }

    return cell.id
  }

  loadDummyData(is_error=false) {
    this.notebookStore.onSparkJobStarting(this.getLastExecutedCellId())

    const time = new Date()
    dummy_data.dummy_job_data[0].submissionTime = time.toISOString().replace('Z', 'GMT')

    if (is_error === true) {
      dummy_data.dummy_job_data[0].status = 'SPARK API ERROR'
      this.notebookStore.onSparkJobError(this.getLastExecutedCellId())
    } else {
      dummy_data.dummy_job_data[0].status = 'STARTING'
    }

    this.onGetSparkApplicationStatus(dummy_data.dummy_application_data[0]);
    this.onGetSparkExecutorStatus(dummy_data.dummy_executor_data);
    this.onGetSparkJobStatus(dummy_data.dummy_job_data);
  }
}
