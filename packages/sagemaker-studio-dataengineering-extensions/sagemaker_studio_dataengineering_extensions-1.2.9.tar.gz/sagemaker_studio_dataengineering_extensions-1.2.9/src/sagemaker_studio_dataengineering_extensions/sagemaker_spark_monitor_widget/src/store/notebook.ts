import { makeAutoObservable } from 'mobx';
import { SparkStage } from './spark-stage';
import { SparkJob } from './spark-job';
import { Cell } from './cell';
import { ITranslator, TranslationBundle } from '@jupyterlab/translation';
import { PLUGIN_ID } from '../lab-extension';

export class NotebookStore {
  numExecutors?: number;
  numTotalCores?: number;
  applicationName?: string;
  applicationId?: string;
  applicationAttemptId?: string;
  uniqueId = 'default-key';
  hideAllDisplays = false;

  cells: { [cellId: string]: Cell } = {};
  jobs: { [jobId: string]: SparkJob } = {};
  stages: { [stageId: string]: SparkStage } = {};

  numJobsToShow = 20

  trans: TranslationBundle;
  
  constructor(public notebookPanelId: string, translator: ITranslator,) {
    makeAutoObservable(this);
    this.trans = translator.load(PLUGIN_ID);
  }

  clearAllData() {
    this.cells = {}
    this.jobs = {}
    this.stages = {}
  }

  toggleHideAllDisplays() {
    this.hideAllDisplays = !this.hideAllDisplays;
  }

  onSparkApplicationStart(data: any) {
    this.applicationId = data.appId;
    this.applicationName = data.appName;
    this.applicationAttemptId = data.appAttemptId;
    this.uniqueId = `app${this.applicationId}-attempt${this.applicationAttemptId}`;
    // console.log(`application status - this.applicationId is ${this.applicationId}`)
  }

  private deleteCellData(cellId: string) {
    const cell = this.cells[cellId];
    if (cell) {
      cell.uniqueJobIds.forEach(uniqueJobId => {
        const job = this.jobs[uniqueJobId];
        if (job) {
          job.uniqueStageIds.forEach(uniqueStageId => {
            const stage = this.stages[uniqueStageId];
            if (stage) {
              delete this.stages[uniqueStageId];
            }
          });
          delete this.jobs[uniqueJobId];
        }
      });
      delete this.cells[cellId];
    }
  }

  onCellRemoved(cellId: string) {
    if(cellId) {
      this.deleteCellData(cellId);
    }
  }

  /**
   * Ensures a cell exists for the given cellId, creating it if necessary.
   * This is the centralized factory method for cell creation.
   */
  ensureCell(cellId: string): Cell {
    if (!this.cells[cellId]) {
      this.cells[cellId] = new Cell(cellId, this);
    }
    return this.cells[cellId];
  }

  /**
   * Forces creation of a new cell, replacing any existing cell.
   * Use this when you need to guarantee a fresh cell instance.
   */
  createFreshCell(cellId: string): Cell {
    this.cells[cellId] = new Cell(cellId, this);
    return this.cells[cellId];
  }


  onCellExecutedAgain(cellId: string) {
    this.deleteCellData(cellId);
    this.createFreshCell(cellId);
  }

  onSparkJobStart(cellId: string, data: any) {
    // These values are set here as previous messages may
    // be missed if reconnecting from a browser reload.
    this.numTotalCores = data.totalCores;
    this.numExecutors = data.numExecutors;

    const job = new SparkJob(this);
    job.uniqueId = `${this.uniqueId}-job-${data.jobId}`;
    job.jobId = data.jobId;
    job.status = data.status;
    job.cellId = cellId;
    job.name = String(data.name).split(' ')[0];
    job.startTime = new Date(data.submissionTime);
    job.stageIds = data.stageIds;
    // job.numStages = data.stageIds.length;
    // job.numTasks = data.numTasks;

    data.stageIds.forEach((stageId: string) => {
      const uniqueStageId = `${this.uniqueId}-stage-${stageId}`;
      let stage = this.stages[uniqueStageId];
      if (!stage) {
        stage = new SparkStage();
        stage.status = 'PENDING';
        this.stages[uniqueStageId] = stage;
      }
      stage.uniqueJobId = job.uniqueId;
      stage.numTasks = data.stageInfos[stageId].numTasks;
      stage.name = data.stageInfos[stageId].name;
      job.uniqueStageIds.push(uniqueStageId);
    });
    job.uniqueStageIds.sort((a, b) =>
      a.localeCompare(b, undefined, { numeric: true })
    );

    if (job.name === 'null') {
      const lastStageId = Math.max.apply(null, data.stageIds);
      job.name = this.stages[`${this.uniqueId}-stage-${lastStageId}`].name;
    }

    const cell = this.ensureCell(cellId);
    cell.uniqueJobIds.push(job.uniqueId);
    job.cell = cell;
    job.cell.taskChartStore.onSparkJobStart(data);
    this.jobs[job.uniqueId] = job;
  }

  onSparkJobEnd(data: any) {
    const uniqueId = `${this.uniqueId}-job-${data.jobId}`;
    const job = this.jobs[uniqueId];
    if (job) {
      job.status = data.status;
      job.endTime = new Date(data.completionTime);
      job.uniqueStageIds.forEach(uniqueStageId => {
        if (this.stages[uniqueStageId]?.status === 'PENDING') {
          this.stages[uniqueStageId].status = 'SKIPPED';
          // job.numTasks -= this.stages[uniqueStageId].numTasks;
        }
      });
      job.cell?.taskChartStore.onSparkJobEnd(data);
    } else {
      console.warn('SparkMonitor: Could not identify job');
    }
  }

  onSparkStageSubmitted(cellId: string, data: any) {
    const submissionTime =
      data.submissionTime === -1 ? new Date() : new Date(data.submissionTime);
    const uniqueStageId = `${this.uniqueId}-stage-${data.stageId}`;
    if (!this.stages[uniqueStageId]) {
      this.stages[uniqueStageId] = new SparkStage();
      this.stages[uniqueStageId].uniqueId = uniqueStageId;
    }
    const stage = this.stages[uniqueStageId];
    stage.cellId = cellId;
    stage.stageId = data.stageId;
    stage.status = 'RUNNING';
    stage.name = String(data.name).split(' ')[0];
    stage.submissionTime = submissionTime;
    stage.numTasks = data.numTasks;
  }

  onSparkStageCompleted(data: any) {
    const uniqueStageId = `${this.uniqueId}-stage-${data.stageId}`;
    const stage = this.stages[uniqueStageId];
    if (stage) {
      stage.status = data.status;
      stage.completionTime = new Date(data.completionTime);
      stage.submissionTime = new Date(data.submissionTime);
      stage.numActiveTasks = 0;
      stage.numCompletedTasks = data.numCompletedTasks;
      stage.numFailedTasks = data.numFailedTasks;
      stage.numTasks = data.numTasks;

      const job = this.jobs[stage.uniqueJobId];
      if (job) {
        job.numActiveTasks = 0;
        job.numCompletedTasks = 0;
        job.numFailedTasks = 0;
        // job.numTasks = 0;

        // Update active/completed/failed tasks number (scan all job stages tasks stats)
        job.uniqueStageIds.forEach(uniqueStageId => {
          job.numActiveTasks += this.stages[uniqueStageId]?.numActiveTasks || 0;
          job.numCompletedTasks +=
            this.stages[uniqueStageId]?.numCompletedTasks || 0;
          job.numFailedTasks += this.stages[uniqueStageId]?.numFailedTasks || 0;
          // job.numTasks += this.stages[uniqueStageId]?.numTasks || 0;
        });
      }
    } else {
      console.warn('SparkMonitor: Unable to identify stage');
    }
  }

  onSparkExecutorAdded(data: any) {
    this.numTotalCores = data.totalCores;
    if (!this.numExecutors) {
      this.numExecutors = 0;
    }
    this.numExecutors += 1;
  }

  onSparkExecutorRemoved(data: any) {
    this.numTotalCores = data.totalCores;
    if (!this.numExecutors) {
      this.numExecutors = 0;
    }
    this.numExecutors -= 1;
  }

  onSparkTaskStart(data: any) {
    const uniqueStageId = `${this.uniqueId}-stage-${data.stageId}`;
    const stage = this.stages[uniqueStageId];
    if (stage) {
      const uniqueJobId = stage.uniqueJobId;
      const job = this.jobs[uniqueJobId];
      if (job) {
        job.cell?.taskChartStore.onSparkTaskStart(data);
      }
    }
  }

  onSparkTaskEnd(data: any) {
    const uniqueStageId = `${this.uniqueId}-stage-${data.stageId}`;
    const stage = this.stages[uniqueStageId];
    if (stage) {
      const uniqueJobId = stage.uniqueJobId;
      const job = this.jobs[uniqueJobId];
      if (job) {
        job.cell?.taskChartStore.onSparkTaskEnd(data);
      }
    }
  }

  // Periodic stage updates
  onSparkStageActive(data: any) {
    const uniqueStageId = `${this.uniqueId}-stage-${data.stageId}`;
    const stage = this.stages[uniqueStageId];
    if (stage && stage.status === 'RUNNING') {
      stage.numActiveTasks = data.numActiveTasks;
      stage.numCompletedTasks = data.numCompletedTasks;
      stage.numFailedTasks = data.numFailedTasks;

      const job = this.jobs[stage.uniqueJobId];
      if (job) {
        job.numActiveTasks = 0;
        job.numCompletedTasks = 0;
        job.numFailedTasks = 0;
        // job.numTasks = 0;

        // Update active/completed/failed tasks number (scan all job stages tasks stats)
        job.uniqueStageIds.forEach(uniqueStageId => {
          job.numActiveTasks += this.stages[uniqueStageId]?.numActiveTasks || 0;
          job.numCompletedTasks +=
            this.stages[uniqueStageId]?.numCompletedTasks || 0;
          job.numFailedTasks += this.stages[uniqueStageId]?.numFailedTasks || 0;
          // job.numTasks += this.stages[uniqueStageId]?.numTasks || 0;
        });
      }
    }
  }

  onSparkJobStatusUpdate(cellId: string, jobDatas: any) {
    let totalActiveTasks = 0;
    let uniqueJobIds: Array<string> = [];
    const cell = this.ensureCell(cellId);
    cell.uniqueJobIds = [];
    for (const data of jobDatas) {
      const job = new SparkJob(this);

      job.uniqueId = `${this.uniqueId}-job-${data.jobId}`;
      job.jobId = data.jobId;
      job.status = data.status;
      job.cellId = cellId;
      job.name = String(data.name).split(' ')[0];
      if (data.submissionTime) {
        job.startTime = this.transformDate(cellId, data.submissionTime);
      }
      if (data.completionTime) {
        job.endTime = this.transformDate(cellId, data.completionTime);
      }
      job.stageIds = data.stageIds;
      // job.numStages = data.stageIds.length;
      // job.numTasks = data.numTasks;

      job.numActiveTasks = data.numActiveTasks;
      job.numCompletedTasks = data.numCompletedTasks;
      job.numFailedTasks = data.numFailedTasks;
      job.numSkippedTasks = data.numSkippedTasks;

      totalActiveTasks += job.numActiveTasks;
      // console.log(`job uniqueId is ${job.uniqueId}`);
      // console.log(`job jobId is ${job.jobId}`);
      // console.log(`job status is ${job.status}`);
      // console.log(`job cellId is ${job.cellId}`);
      // console.log(`job name is ${job.name}`);
      // console.log(`job startTime is ${job.startTime}`);
      // console.log(`job endTime is ${job.endTime}`);
      // console.log(`job stageIds is ${job.stageIds}`);
      // console.log(`job numStages is ${job.numStages}`);
      // console.log(`job numTasks is ${job.numTasks}`);
      // console.log(`job numActiveTasks is ${job.numActiveTasks}`);
      // console.log(`job numCompletedTasks is ${job.numCompletedTasks}`);
      // console.log(`job numFailedTasks is ${job.numFailedTasks}`);
      

      const uniqueStageIds: string[] = [];
      data.stageIds.forEach((stageId: string) => {
        // console.log(`stage id is ${stageId}`)
        const uniqueStageId = `${this.uniqueId}-stage-${stageId}`;
        let stage = this.stages[uniqueStageId];
        if (!stage) {
          // console.log('job create stage')
          stage = new SparkStage();
          stage.status = 'PENDING';
          stage.uniqueJobId = job.uniqueId;
          this.stages[uniqueStageId] = stage;
          this.stages[uniqueStageId].uniqueId = uniqueStageId;
        }
        uniqueStageIds.push(uniqueStageId);
      });

      job.uniqueStageIds = uniqueStageIds;
  
      job.uniqueStageIds.sort((a, b) =>
        a.localeCompare(b, undefined, { numeric: true })
      );
  
      if (job.name === 'null') {
        const lastStageId = Math.max.apply(null, data.stageIds);
        job.name = this.stages[`${this.uniqueId}-stage-${lastStageId}`].name;
      }
  
      uniqueJobIds.push(job.uniqueId);

      uniqueJobIds.sort((a, b) =>
        b.localeCompare(a, undefined, { numeric: true })
      );

      job.cell = cell;
  
      this.jobs[job.uniqueId] = job;
    }

    cell.uniqueJobIds = uniqueJobIds.slice(0, this.numJobsToShow);
    cell.taskChartStore.onSparkJobDataUpdate(jobDatas);
    cell.taskChartStore.numActiveTasks = totalActiveTasks;
  }

  transformDate(cellId: string, date: string) {
    return this.cells[cellId].taskChartStore.createDateAsUTC(new Date(date.substring(0, date.length - 3)));
  }

  onSparkStageStatusUpdate(cellId: string, stageDatas: any) {
    for (const data of stageDatas) {
      const uniqueStageId = `${this.uniqueId}-stage-${data.stageId}`;
      const stage = this.stages[uniqueStageId];
      stage.cellId = cellId;

      if (data.submissionTime) {
        stage.submissionTime = this.transformDate(cellId, data.submissionTime);
      }
      
      if (!this.stages[uniqueStageId]) {
        // console.log('stage create stage')
        this.stages[uniqueStageId] = new SparkStage();
        this.stages[uniqueStageId].uniqueId = uniqueStageId;
      }
      
      stage.stageId = data.stageId;
      stage.status = data.status;
      stage.name = String(data.name).split(' ')[0];
      
      if (data.completionTime) {
        stage.completionTime = this.transformDate(cellId, data.completionTime);
      }
      stage.numTasks = data.numTasks;

      stage.numActiveTasks = data.numActiveTasks;
      stage.numCompletedTasks = data.numCompleteTasks;
      stage.numFailedTasks = data.numFailedTasks;

      // console.log(`stage uniqueId is ${this.stages[uniqueStageId].uniqueId}`);
      // console.log(`stage cellId is ${this.stages[uniqueStageId].cellId}`);
      // console.log(`stage stageId is ${this.stages[uniqueStageId].stageId}`);
      // console.log(`stage status is ${this.stages[uniqueStageId].status}`);
      // console.log(`stage name is ${this.stages[uniqueStageId].name}`);
      // console.log(`stage submissionTime is ${this.stages[uniqueStageId].submissionTime}`);
      // console.log(`stage completionTime is ${this.stages[uniqueStageId].completionTime}`);
      // console.log(`stage numTasks is ${this.stages[uniqueStageId].numTasks}`);
      // console.log(`stage numActiveTasks is ${this.stages[uniqueStageId].numActiveTasks}`);
      // console.log(`stage numCompletedTasks is ${this.stages[uniqueStageId].numCompletedTasks}`);
      // console.log(`stage numFailedTasks is ${this.stages[uniqueStageId].numFailedTasks}`);
    }
  }

  onSparkExecutorUpdated(cellId: string, data: any) {
    this.numTotalCores = data.numTotalCores;
    if (!this.numExecutors) {
      this.numExecutors = 0;
    }
    this.numExecutors = data.numExecutors;

    const cell = this.ensureCell(cellId);
    cell.taskChartStore.onSparkExecutorDataUpdate(data.rawData);
  }

  onSparkTaskStatusUpdate(data: any) {
    // console.log(`onSparkTaskStatusUpdate is ${JSON.stringify(data)}`)
    if (!data || !data[0] || !data[0][0]) {
      return
    }
    const uniqueStageId = `${this.uniqueId}-stage-${data[0][0].stageId}`;
    const stage = this.stages[uniqueStageId];
    if (stage) {
      const uniqueJobId = stage.uniqueJobId;
      const job = this.jobs[uniqueJobId];
      if (job) {
        job.cell?.taskChartStore.onSparkTaskDataUpdate(data);
      }
    }
  }

  onSparkJobStarting(cellId: string | undefined) {
    if (!cellId) return;
    
    const cell = this.ensureCell(cellId);
    cell.isStarting = true;
    cell.isError = false;
  }

  onSparkJobStarted(cellId: string | undefined) {
    if (!cellId) return;
    
    const cell = this.ensureCell(cellId);
    cell.isStarting = false;
    this.cells[cellId].isError = false
  }

  onSparkJobError(cellId: string | undefined) {
    if (!cellId) return;
    
    const cell = this.ensureCell(cellId);
    cell.isStarting = false;
    cell.isError = true;
  }
}
