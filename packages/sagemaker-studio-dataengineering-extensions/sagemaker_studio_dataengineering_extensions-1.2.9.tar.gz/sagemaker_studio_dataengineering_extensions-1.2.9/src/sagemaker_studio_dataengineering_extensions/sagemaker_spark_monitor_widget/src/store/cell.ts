import { makeAutoObservable } from 'mobx';

import { TaskChartStore } from './task-chart-store';
import type { NotebookStore } from './notebook';
import { SessionInfo } from './session-info';

export class Cell {
  view: 'jobs' | 'taskchart' | 'timeline' = 'jobs';
  isCollapsed = false;
  isRemoved = false;
  uniqueJobIds: Array<string> = [];
  taskChartStore: TaskChartStore;
  isStarting = false;
  isError = false;
  sessionInfo?: SessionInfo;
  
  constructor(
    public cellId: string,
    private notebookStore: NotebookStore
  ) {
    makeAutoObservable(this);
    this.taskChartStore = new TaskChartStore(this.notebookStore);
  }

  toggleCollapseCellDisplay() {
    this.isCollapsed = !this.isCollapsed;
  }

  toggleHideCellDisplay() {
    this.isRemoved = !this.isRemoved;
  }

  setView(view: 'jobs' | 'taskchart' | 'timeline') {
    this.view = view;
    this.isCollapsed = false;
    this.isRemoved = false;
  }

  updateSessionInfo(sessionInfo: SessionInfo | undefined) {
    this.sessionInfo = sessionInfo;
    console.log(`[Spark Monitor] Cell ${this.cellId} session info updated:`, {
      connection_name: sessionInfo?.connection_name,
      connection_type: sessionInfo?.connection_type
    });
  }

  get jobs() {
    return this.uniqueJobIds.map(id => this.notebookStore.jobs[id]);
  }

  get numActiveJobs() {
    return this.jobs.filter(job => job.status === 'RUNNING').length;
  }
  get numFailedJobs() {
    return this.jobs.filter(job => job.status === 'FAILED').length;
  }

  get numCompletedJobs() {
    return this.jobs.filter(job => job.status === 'SUCCEEDED').length;
  }

  get numTotalJobs() {
    return this.uniqueJobIds.length;
  }
}
