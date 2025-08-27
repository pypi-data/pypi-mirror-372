import { NotebookStore } from './notebook';

class Point {
  date: number = 0;
  val: number = 0;
  text: string = '';
}

export class TaskChartStore {
  jobDataX: Array<number> = [];
  jobDataY: Array<number> = [];
  jobDataText: Array<string> = [];
  executorDataX: Array<number> = [];
  executorDataY: Array<number> = [];
  taskDataX: Array<number> = [];
  taskDataY: Array<number> = [];
  numActiveTasks = 0;

  constructor(private notebookStore: NotebookStore) {}

  addExecutorData(time: number, numCores: number) {
    this.executorDataX.push(time);
    this.executorDataY.push(numCores);
  }


  addTaskData(time: number, numTasks: number) {
    this.taskDataX.push(new Date(time).getTime());
    this.taskDataY.push(numTasks);
    this.addExecutorData(
      new Date(time).getTime(),
      this.notebookStore.numTotalCores || 0
    );
  }

  onSparkJobStart(data: any) {
    const submissionTimestamp = new Date(data.submissionTime).getTime();
    this.jobDataX.push(submissionTimestamp);
    this.jobDataY.push(0);
    this.jobDataText.push(`Job ${data.jobId} started`);

    this.addExecutorData(submissionTimestamp, data.totalCores);
  }

  onSparkJobEnd(data: any) {
    const completionTime = new Date(data.completionTime).getTime();
    this.jobDataX.push(completionTime);
    this.jobDataY.push(0);
    this.jobDataText.push(`Job ${data.jobId} ended`);
  }

  onSparkTaskStart(data: any) {
    this.addTaskData(data.launchTime, this.numActiveTasks);
    this.numActiveTasks += 1;
    this.addTaskData(data.launchTime, this.numActiveTasks);
  }

  onSparkTaskEnd(data: any) {
    this.addTaskData(data.finishTime, this.numActiveTasks);
    this.numActiveTasks -= 1;
    this.addTaskData(data.finishTime, this.numActiveTasks);
  }

  createDateAsUTC(date: any) {
    return new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate(), date.getHours(), date.getMinutes(), date.getSeconds()));
  }

  onSparkExecutorDataUpdate(executors: any) {
    const points: Array<Point> = [];
    for (const data of executors) {
      const date = new Date(data.addTime.substring(0, data.addTime.length - 3))
      const point = new Point();
      point.date = this.createDateAsUTC(date).getTime();
      point.val = 1;
      points.push(point)

      if (data.removeTime) {
        const date = new Date(data.removeTime.substring(0, data.addTime.length - 3))
        const point = new Point();
        point.date = this.createDateAsUTC(date).getTime();
        point.val = -1;
        points.push(point)
      }
    }

    const sortedPoints = points.sort((n1,n2) => n1.date - n2.date)

    const executorData_X: Array<number> = [];
    const executorData_Y: Array<number> = [];

    let coreCnt = 0
    for (const point of sortedPoints) {
      executorData_X.push(point.date)
      coreCnt += point.val;
      executorData_Y.push(coreCnt || 0)
    }

    this.executorDataX = executorData_X;
    this.executorDataY = executorData_Y;
    // console.log(`task chart -this.executorDataX is ${this.executorDataX} `);
  }

  onSparkJobDataUpdate(jobDatas: any) {
    const points: Array<Point> = [];

    for (const data of jobDatas) {
      const submissionTimestamp = new Date(data.submissionTime.substring(0, data.submissionTime.length - 3));
      const point = new Point();
      point.date = this.createDateAsUTC(submissionTimestamp).getTime();
      point.val = 0;
      point.text = `Job ${data.jobId} started`;
      points.push(point);

      // check default time for completion
      if (data.completionTime) {
        const point2 = new Point();
        const completionTimestamp = new Date(data.completionTime.substring(0, data.completionTime.length - 3));
        point2.date = this.createDateAsUTC(completionTimestamp).getTime();
        point2.val = 0;
        point2.text = `Job ${data.jobId} ended`;
        points.push(point2);
      }
    }

    const sortedPoints = points.sort((n1,n2) => n1.date - n2.date)

    const jobData_x: Array<number> = [];
    const jobData_y: Array<number> = [];
    const jobData_text: Array<string> = [];

    for (const p of sortedPoints) {
      jobData_x.push(p.date);
      jobData_y.push(p.val);
      jobData_text.push(p.text);
    }
    
    this.jobDataX = jobData_x;
    this.jobDataY = jobData_y;
    this.jobDataText = jobData_text;
    // console.log(`task chart -this.jobDataX is ${this.jobDataX} `);
    // console.log(`task chart -this.jobDataY is ${this.jobDataY} `);
    // console.log(`task chart -this.jobDataText is ${this.jobDataText} `);
  }

  onSparkTaskDataUpdate(taskDatas: any) {
    const points: Array<Point> = [];
    for (const taskDataInStage of taskDatas) {
      for (const data of taskDataInStage) {
        const date = new Date(data.launchTime.substring(0, data.launchTime.length - 3))
        const point = new Point();
        point.date = this.createDateAsUTC(date).getTime();
        point.val = 1;
        points.push(point)
  
        if (data.status == 'SUCCESS') {
          const date = new Date(data.launchTime.substring(0, data.launchTime.length - 3))
          const point = new Point();
          point.date = this.createDateAsUTC(date).getTime() + data.duration;
          point.val = -1;
          points.push(point)
        }
      }
    }

    const sortedPoints = points.sort((n1,n2) => n1.date - n2.date)

    const taskData_X: Array<number> = [];
    const taskData_Y: Array<number> = [];

    let taskCnt = 0
    for (const point of sortedPoints) {
      taskData_X.push(point.date)
      taskCnt += point.val;
      taskData_Y.push(taskCnt || 0)
    }

    this.taskDataX = taskData_X;
    this.taskDataY = taskData_Y;

    // console.log(`task chart -this.taskDataX is ${this.taskDataX} `);
    // console.log(`task chart -this.taskDataY is ${this.taskDataY} `);
  }
}
