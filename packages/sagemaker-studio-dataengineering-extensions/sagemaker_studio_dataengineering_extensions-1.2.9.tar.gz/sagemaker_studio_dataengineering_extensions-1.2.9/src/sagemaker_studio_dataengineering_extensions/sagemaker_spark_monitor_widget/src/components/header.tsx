import React, { useState } from 'react';
import { observer } from 'mobx-react-lite';
import { useCellStore, useNotebookStore } from '../store';
import { triggerSparkUiWithSessionInfo, validateSessionInfoForSparkUI } from '../lab-extension/spark-ui-integration';

export const CellMonitorHeader = observer(() => {
  const notebook = useNotebookStore();
  const cell = useCellStore();

  // State for Spark UI loading feedback
  const [isSparkUiLoading, setIsSparkUiLoading] = useState(false);

  const isButtonActive = (view: string) =>
    !cell.isCollapsed && cell.view === view ? 'tabbuttonactive' : '';
  const jobButtonClassNames =
    'jobtabletabbuttonicon tabbutton ' + isButtonActive('jobs');
  const tasksButtonClassNames =
    'taskviewtabbuttonicon tabbutton ' + isButtonActive('taskchart');
  const timelineButtonClassNames =
    'timelinetabbuttonicon tabbutton ' + isButtonActive('timeline');

  const trans = notebook.trans

  const handleSparkUiClick = async (event: React.MouseEvent) => {
    event.preventDefault();
    
    // Prevent double-clicks
    if (isSparkUiLoading) {
      return;
    }
    
    try {
      setIsSparkUiLoading(true);
      
      // Use cell-specific session info instead of notebook-level
      if (!validateSessionInfoForSparkUI(cell.sessionInfo)) {
        console.warn(`[Spark Monitor] Invalid or missing session info for cell ${cell.cellId} - cannot open Spark UI`);
        return;
      }

      console.log(`[Spark Monitor] Opening Spark UI for cell ${cell.cellId} with session:`, cell.sessionInfo?.connection_name);
      
      // Use the enhanced integration function with timeout and error handling
      await triggerSparkUiWithSessionInfo(cell.sessionInfo!, 30000);
      
    } catch (error) {
      console.error(`[Spark Monitor] Error opening Spark UI for cell ${cell.cellId}:`, error);
    } finally {
      setIsSparkUiLoading(false);
    }
  };


  const TEXT_APACHE_SPARK = trans.__(' Apache Spark ');
  const TEXT_EXECUTORS = trans.__('EXECUTORS');
  const TEXT_CORES = trans.__('CORES');
  const TEXT_JOBS = trans.__('Jobs');
  const TEXT_STARTING = trans.__('STARTING');
  const TEXT_ERROR = trans.__('ERROR');
  const TEXT_RUNNING = trans.__('RUNNING');
  const TEXT_COMPLETED = trans.__('COMPLETED');
  const TEXT_FAILED = trans.__('FAILED');

  const TEXT_TASKS = trans.__('Tasks');
  const TEXT_EVENT_TIMELINE = trans.__('Event Timeline');
  const TEXT_CLOSE_DISPLAY = trans.__('Close Display');

  return (
    <div className="title">
      <div className="titleleft">
        <span
          className="tbitem titlecollapse "
          onClick={() => {
            cell.toggleCollapseCellDisplay();
          }}
        >
          <svg className={'headericon ' + (cell.isCollapsed ? 'headericoncollapsed' : '')}
            width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19.376 12.4154L8.77735 19.4811C8.54759 19.6343 8.23715 19.5722 8.08397 19.3425C8.02922 19.2603 8 19.1638 8 19.0651V4.93359C8 4.65744 8.22386 4.43359 8.5 4.43359C8.59871 4.43359 8.69522 4.46281 8.77735 4.51756L19.376 11.5833C19.6057 11.7365 19.6678 12.047 19.5146 12.2767C19.478 12.3316 19.4309 12.3788 19.376 12.4154Z"
              fill="var(--jp-inverse-layout-color0)" />
          </svg>

          <span

          ></span>
        </span>
        <span className="tbitem badgecontainer">
          <b>{TEXT_APACHE_SPARK}</b>
          {validateSessionInfoForSparkUI(cell.sessionInfo) && (
            <span 
              className={`header-spark-ui-link ${isSparkUiLoading ? 'header-spark-ui-loading' : ''}`}
              onClick={handleSparkUiClick}
              tabIndex={0}
              role="button"
              aria-label={isSparkUiLoading ? "Opening Spark UI..." : "Open Spark UI"}
              title={isSparkUiLoading ? "Opening Spark UI..." : `Open Spark UI for ${cell.sessionInfo?.connection_name}`}
              style={{ 
                cursor: isSparkUiLoading ? 'wait' : 'pointer',
                opacity: isSparkUiLoading ? 0.6 : 1,
                marginLeft: '8px',
                color: 'var(--jp-brand-color1)',
                textDecoration: 'none',
                fontSize: '0.9em',
                fontWeight: 'normal'
              }}
            >
              {isSparkUiLoading ? (
                'Opening...'
              ) : (
                <>
                  <svg 
                    width="14" 
                    height="14" 
                    viewBox="0 0 14 14" 
                    fill="none" 
                    xmlns="http://www.w3.org/2000/svg"
                    style={{ marginRight: '4px', verticalAlign: 'middle' }}
                  >
                    <path 
                      d="M5.83333 3.5V4.66667H2.91667V11.0833H9.33333V8.16667H10.5V11.6667C10.5 11.9888 10.2388 12.25 9.91667 12.25H2.33333C2.01117 12.25 1.75 11.9888 1.75 11.6667V4.08333C1.75 3.76117 2.01117 3.5 2.33333 3.5H5.83333ZM12.25 1.75V6.41667H11.0833L11.0833 3.74092L6.53747 8.28747L5.71252 7.46252L10.2579 2.91667H7.58333V1.75H12.25Z" 
                      fill="currentColor"
                    />
                  </svg>
                  Spark UI
                </>
              )}
            </span>
          )}
          <span className="badgeexecutor">
            <span className="badgeexecutorcount">{notebook.numExecutors}</span>{' '}
            {TEXT_EXECUTORS}
          </span>
          <span className="badgeexecutorcores">
            <span className="badgeexecutorcorescount">
              {notebook.numTotalCores}
            </span>{' '}
            {TEXT_CORES}
          </span>
          <b> {TEXT_JOBS} </b>
          <span className="badges">
            {cell.isStarting ? (
              <span className="badgerunning">
                <span className="badgerunningcount">1</span>{' '}
                {TEXT_STARTING}
              </span>
            ) : (
              ''
            )}
            {cell.isError ? (
              <span className="badgefailed">
                <span className="badgefailedcount">1</span>{' '}
                {TEXT_ERROR}
              </span>
            ) : (
              ''
            )}
            {cell.numActiveJobs ? (
              <span className="badgerunning">
                <span className="badgerunningcount">{cell.numActiveJobs}</span>{' '}
                {TEXT_RUNNING}
              </span>
            ) : (
              ''
            )}
            {cell.numCompletedJobs ? (
              <span className="badgecompleted">
                <span className="badgecompletedcount">
                  {cell.numCompletedJobs}
                </span>{' '}
                {TEXT_COMPLETED}
              </span>
            ) : (
              ''
            )}
            {cell.numFailedJobs ? (
              <span className="badgefailed">
                <span className="badgefailedcount">{cell.numFailedJobs}</span>{' '}
                {TEXT_FAILED}
              </span>
            ) : (
              ''
            )}
          </span>
        </span>
      </div>
      <div className="titleright">
        <div className="tabbuttons">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" id="jobtable"
            className={jobButtonClassNames}
            onClick={() => {
              cell.setView('jobs');
            }}
          >
            <title>{TEXT_JOBS}</title>
            <path d="M4 8H20V5H4V8ZM14 19V10H10V19H14ZM16 19H20V10H16V19ZM8 19V10H4V19H8ZM3 3H21C21.5523 3 22 3.44772 22 4V20C22 20.5523 21.5523 21 21 21H3C2.44772 21 2 20.5523 2 20V4C2 3.44772 2.44772 3 3 3Z"
              fill="var(--jp-inverse-layout-color0)" />
          </svg>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" id="chart"
            className={tasksButtonClassNames}
            onClick={() => {
              cell.setView('taskchart');
            }}
          >
            <title>{TEXT_TASKS}</title>
            <path d="M3 3H21C21.5523 3 22 3.44772 22 4V20C22 20.5523 21.5523 21 21 21H3C2.44772 21 2 20.5523 2 20V4C2 3.44772 2.44772 3 3 3ZM7 13V17H9V13H7ZM11 7V17H13V7H11ZM15 10V17H17V10H15Z"
              fill="var(--jp-inverse-layout-color0)" />
          </svg>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" id="timeline"
            className={timelineButtonClassNames}
            onClick={() => {
              cell.setView('timeline');
            }}
          >
            <title>{TEXT_EVENT_TIMELINE}</title>
            <path d="M3 3C2.44772 3 2 3.44772 2 4V20C2 20.5523 2.44772 21 3 21H21C21.5523 21 22 20.5523 22 20V4C22 3.44772 21.5523 3 21 3H3ZM4 19V5H20V19H4ZM14 7H6V9H14V7ZM18 15V17H10V15H18ZM16 11H8V13H16V11Z"
              fill="var(--jp-inverse-layout-color0)" />
          </svg>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"
            className="closebuttonicon tabbutton"
            onClick={() => {
              cell.toggleHideCellDisplay();
            }}>
            <title>{TEXT_CLOSE_DISPLAY}</title>
            <path d="M11.9997 10.5865L16.9495 5.63672L18.3637 7.05093L13.4139 12.0007L18.3637 16.9504L16.9495 18.3646L11.9997 13.4149L7.04996 18.3646L5.63574 16.9504L10.5855 12.0007L5.63574 7.05093L7.04996 5.63672L11.9997 10.5865Z"
              fill="var(--jp-inverse-layout-color0)" />
          </svg>
        </div>
      </div>
    </div>
  );
});
