import { observer } from 'mobx-react-lite';
import React from 'react';
import ReactTimeAgo from 'react-timeago';

import { useCellStore, useNotebookStore } from '../store';
import { ProgressBar } from './progress-bar';
import prettyMilliseconds from 'pretty-ms';
import { ErrorBoundary } from './error-boundary';

const StageItem = observer((props: { stageId: string }) => {
  const notebook = useNotebookStore();
  const stage = notebook.stages[props.stageId];
  
  return (
    <tr className="stagerow">
      <td className="tdstageid">{stage.stageId}</td>
      <td className="tdstagename">{stage.name}</td>
      <td className="tdstagestatus">
        <span className={stage.status}>{stage.status}</span>
      </td>
      <td className="tdtasks">
        <ProgressBar
          total={stage.numTasks}
          running={stage.numActiveTasks}
          completed={stage.numCompletedTasks}
        />
      </td>
      <td className="tdstagestarttime">
        {React.createElement(ReactTimeAgo as any, { date: stage.submissionTime, minPeriod: 10 })}
      </td>
      <td className="tdstageduration">
        {stage.completionTime
          ? prettyMilliseconds(
              stage.completionTime?.getTime() - stage.submissionTime.getTime()
            )
          : '-'}
      </td>
    </tr>
  );
});

const StageTable = observer((props: { jobId: string }) => {
  const notebook = useNotebookStore();
  const stageIds = notebook.jobs[props.jobId].uniqueStageIds;
  const rows = stageIds.map(stageId => {
    return <StageItem stageId={stageId} key={stageId} />;
  });

  const trans = notebook.trans;

  const TEXT_ID = trans.__('ID');
  const TEXT_STAGE = trans.__('Stage');
  const TEXT_STATUS = trans.__('Status');
  const TEXT_TASKS = trans.__('Tasks');
  const TEXT_SUBMISSION_TIME = trans.__('Submission Time');
  const TEXT_DURATION = trans.__('Duration');

  return (
    <table className="stagetable">
      <thead>
        <tr>
          <th className="thstageid">{ TEXT_ID }</th>
          <th className="thstagename">{ TEXT_STAGE }</th>
          <th className="thstagestatus">{ TEXT_STATUS }</th>
          <th className="thstagetasks">{ TEXT_TASKS }</th>
          <th className="thstagestart">{ TEXT_SUBMISSION_TIME }</th>
          <th className="thstageduration">{ TEXT_DURATION }</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  );
});

const JobItem = observer((props: { jobId: string }) => {
  const notebook = useNotebookStore();
  const job = notebook?.jobs[props.jobId];
  const [stagesCollapsed, setStageTableCollapsed] = React.useState(true);
  const onClickCollapseStageTable = () => {
    setStageTableCollapsed(value => !value);
  };

  return (
    <>
      <tr className="jobrow">
        <td className="tdstagebutton" onClick={onClickCollapseStageTable}>
          <svg className={
              'tdstageicon ' + (!stagesCollapsed ? 'tdstageiconcollapsed' : '')
            } width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M19.376 12.4154L8.77735 19.4811C8.54759 19.6343 8.23715 19.5722 8.08397 19.3425C8.02922 19.2603 8 19.1638 8 19.0651V4.93359C8 4.65744 8.22386 4.43359 8.5 4.43359C8.59871 4.43359 8.69522 4.46281 8.77735 4.51756L19.376 11.5833C19.6057 11.7365 19.6678 12.047 19.5146 12.2767C19.478 12.3316 19.4309 12.3788 19.376 12.4154Z"
           fill="var(--jp-inverse-layout-color0)"/>
          </svg>

        </td>
        <td className="tdjobid">{job.jobId}</td>
        <td className="tdjobname">{job.name}</td>
        <td className="tdjobstatus">
          <span className={'tditemjobstatus ' + job.status}>{job.status}</span>
        </td>
        <td className="tdjobstages">
          {job.numCompletedStages}/{job.numStages}
          {job.numSkippedStages > 0 ? `(${job.numSkippedStages} skipped)` : ''}
          {job.numActiveStages > 0 ? `(${job.numActiveStages} active)` : ''}
        </td>
        <td className="tdtasks">
          <ProgressBar
            total={job.numTasks}
            running={job.numActiveTasks}
            completed={job.numCompletedTasks}
          />
        </td>
        <td className="tdjobstarttime">
          {React.createElement(ReactTimeAgo as any, { date: job.startTime })}
        </td>
        <td className="tdjobduration">
          {job.endTime
            ? prettyMilliseconds(
                job.endTime?.getTime() - job.startTime.getTime()
              )
            : '-'}
        </td>
      </tr>
      {!stagesCollapsed && (
        <tr className="jobstagedatarow">
          <td className="stagetableoffset"></td>
          <td colSpan={7} className="stagedata">
            <StageTable jobId={props.jobId} />
          </td>
        </tr>
      )}
    </>
  );
});

export const JobTable = observer(() => {
  const cell = useCellStore();
  const notebook = useNotebookStore();

  const trans = notebook.trans;

  const TEXT_ID = trans.__('ID');
  const TEXT_JOB = trans.__('Job');
  const TEXT_STATUS = trans.__('Status');
  const TEXT_STAGES = trans.__('Stages');
  const TEXT_TASKS = trans.__('Tasks');
  const TEXT_SUBMISSION_TIME = trans.__('Submission Time');
  const TEXT_DURATION = trans.__('Duration');

  return (
    <ErrorBoundary>
      <div className="tabcontent">
        <table className="jobtable">
          <thead>
            <tr>
              <th className="thbutton"></th>
              <th className="thjobid">{ TEXT_ID }</th>
              <th className="thjobname">{ TEXT_JOB }</th>
              <th className="thjobstatus">{ TEXT_STATUS }</th>
              <th className="thjobstages">{TEXT_STAGES}</th>
              <th className="thjobtasks">{TEXT_TASKS}</th>
              <th className="thjobstart">{TEXT_SUBMISSION_TIME}</th>
              <th className="thjobtime">{TEXT_DURATION}</th>
            </tr>
          </thead>
          <tbody className="jobtablebody">
            {cell.uniqueJobIds.map(jobId => (
              <JobItem jobId={jobId} key={jobId} />
            ))}
          </tbody>
        </table>
      </div>
    </ErrorBoundary>
  );
});
