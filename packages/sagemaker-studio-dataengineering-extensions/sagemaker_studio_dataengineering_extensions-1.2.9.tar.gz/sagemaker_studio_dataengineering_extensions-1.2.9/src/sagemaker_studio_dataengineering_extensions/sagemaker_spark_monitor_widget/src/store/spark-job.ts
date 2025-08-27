import { makeAutoObservable } from 'mobx';

import type { Cell } from './cell';
import type { NotebookStore } from './notebook';

export class SparkJob {
  uniqueId!: string;
  cellId!: string;
  jobId!: string;
  status: 'RUNNING' | 'SUCCEEDED' | 'FAILED' = 'RUNNING';
  name = 'unnamed';
  startTime!: Date;
  endTime?: Date;
  stageIds: string[] = [];
  uniqueStageIds: string[] = [];

  // numStages = 0;

  // numTasks = 0;
  numActiveTasks = 0;
  numCompletedTasks = 0;
  numFailedTasks = 0;
  numSkippedTasks = 0;

  cell?: Cell;

  get numTasks() {
    return this.numActiveTasks + this.numCompletedTasks + this.numFailedTasks;
  }

  get numStages() {
    return this.uniqueStageIds.length - this.numSkippedStages;
  }

  get numActiveStages() {
    return this.uniqueStageIds.filter(stageId => {
      return this.notebookStore.stages[stageId].status === 'PENDING';
    }).length;
  }

  get numCompletedStages() {
    return this.uniqueStageIds.filter(stageId => {
      return this.notebookStore.stages[stageId].status === 'COMPLETE';
    }).length;
  }

  get numFailedStages() {
    return this.uniqueStageIds.filter(stageId => {
      return this.notebookStore.stages[stageId].status === 'FAILED';
    }).length;
  }

  get numSkippedStages() {
    return this.uniqueStageIds.filter(stageId => {
      return this.notebookStore.stages[stageId].status === 'SKIPPED';
    }).length;
  }

  constructor(private notebookStore: NotebookStore) {
    makeAutoObservable(this);
  }
}
