import { Scheduler } from '@jupyterlab/scheduler';
import { pluginIds } from '../constants';
var PanoramaDataAnalyticsType;
(function (PanoramaDataAnalyticsType) {
    PanoramaDataAnalyticsType["eventDetail"] = "eventDetail";
})(PanoramaDataAnalyticsType || (PanoramaDataAnalyticsType = {}));
const NB_JOBS_PANORAMA_FEATURE = 'NotebookJobs';
const EVENT_MAPPING = {
    'org.jupyter.jupyter-scheduler.notebook-header.create-job': `${NB_JOBS_PANORAMA_FEATURE}-CreateJob-FromNotebookHeader`,
    'org.jupyter.jupyter-scheduler.file-browser.create-job': `${NB_JOBS_PANORAMA_FEATURE}-CreateJob-FromFileBrowser`,
    'org.jupyter.jupyter-scheduler.launcher.show-jobs': `${NB_JOBS_PANORAMA_FEATURE}-JobsList-OpenFromLauncher`,
    'org.jupyter.jupyter-scheduler.create-job.options.package_input_folder.check': `${NB_JOBS_PANORAMA_FEATURE}-CreateJob-InputFolderCheck`,
    'org.jupyter.jupyter-scheduler.create-job.options.package_input_folder.uncheck': `${NB_JOBS_PANORAMA_FEATURE}-CreateJob-InputFolderUncheck`,
    'org.jupyter.jupyter-scheduler.create-job.create-job': `${NB_JOBS_PANORAMA_FEATURE}-CreateJob-Create`,
    'org.jupyter.jupyter-scheduler.create-job.cancel': `${NB_JOBS_PANORAMA_FEATURE}-CreateJob-Cancel`,
    'org.jupyter.jupyter-scheduler.create-job.create-job.success': `${NB_JOBS_PANORAMA_FEATURE}-CreateJob-Success`,
    'org.jupyter.jupyter-scheduler.create-job.create-job.failure': `${NB_JOBS_PANORAMA_FEATURE}-CreateJob-Failure`,
    'org.jupyter.jupyter-scheduler.create-job.create-job-definition': `${NB_JOBS_PANORAMA_FEATURE}-CreateJob-CreateJobDefinition`,
    'org.jupyter.jupyter-scheduler.create-job.create-job-definition.success': `${NB_JOBS_PANORAMA_FEATURE}-CreateJobDefinition-Success`,
    'org.jupyter.jupyter-scheduler.create-job.create-job-definition.failure': `${NB_JOBS_PANORAMA_FEATURE}-CreateJobDefinition-Failure`,
    'org.jupyter.jupyter-scheduler.create-job-from-definition.create-job': `${NB_JOBS_PANORAMA_FEATURE}-CreateJobFromDefinition-Create`,
    'org.jupyter.jupyter-scheduler.create-job-from-definition.create-job.success': `${NB_JOBS_PANORAMA_FEATURE}-CreateJobFromDefinition-Success`,
    'org.jupyter.jupyter-scheduler.create-job-from-definition.create-job.failure': `${NB_JOBS_PANORAMA_FEATURE}-CreateJobFromDefinition-Failure`,
    'org.jupyter.jupyter-scheduler.create-job-from-definition.cancel': `${NB_JOBS_PANORAMA_FEATURE}-CreateJobFromDefinition-Cancel`,
    'org.jupyter.jupyter-scheduler.create-job.job-type.run-now': `${NB_JOBS_PANORAMA_FEATURE}-CreateJobType-RunNow`,
    'org.jupyter.jupyter-scheduler.create-job.job-type.run-on-schedule': `${NB_JOBS_PANORAMA_FEATURE}-CreateJobType-RunOnSchedule`,
    'org.jupyter.jupyter-scheduler.create-job.advanced-options.expand': `${NB_JOBS_PANORAMA_FEATURE}-CreateJob-ExpandAdvancedOptions`,
    'org.jupyter.jupyter-scheduler.create-job.advanced-options.collapse': `${NB_JOBS_PANORAMA_FEATURE}-CreateJob-CollapseAdvancedOptions`,
    'org.jupyter.jupyter-scheduler.jobs-list.reload': `${NB_JOBS_PANORAMA_FEATURE}-JobsList-Reload`,
    'org.jupyter.jupyter-scheduler.jobs-definition-list.reload': `${NB_JOBS_PANORAMA_FEATURE}-JobsDefinitionList-Reload`,
    'org.jupyter.jupyter-scheduler.jobs-list.open-input-file': `${NB_JOBS_PANORAMA_FEATURE}-JobsList-OpenInputFile`,
    'org.jupyter.jupyter-scheduler.jobs-list.open-output-file': `${NB_JOBS_PANORAMA_FEATURE}-JobsList-OpenOutputFile`,
    'org.jupyter.jupyter-scheduler.job-list.stop-confirm': `${NB_JOBS_PANORAMA_FEATURE}-JobsList-StopConfirm`,
    'org.jupyter.jupyter-scheduler.jobs-list.download': `${NB_JOBS_PANORAMA_FEATURE}-JobsList-Download`,
    'org.jupyter.jupyter-scheduler.jobs-list.open-detail': `${NB_JOBS_PANORAMA_FEATURE}-JobsList-OpenDetail`,
    'org.jupyter.jupyter-scheduler.jobs-list.delete': `${NB_JOBS_PANORAMA_FEATURE}-JobsList-Delete`,
    'org.jupyter.jupyter-scheduler.jobs-list.stop': `${NB_JOBS_PANORAMA_FEATURE}-JobsList-Stop`,
    'org.jupyter.jupyter-scheduler.job-definition-list.open-detail': `${NB_JOBS_PANORAMA_FEATURE}-JobsDefinitionList-OpenDetail`,
    'org.jupyter.jupyter-scheduler.job-definition-list.pause': `${NB_JOBS_PANORAMA_FEATURE}-JobsDefinitionList-Pause`,
    'org.jupyter.jupyter-scheduler.job-definition-list.resume': `${NB_JOBS_PANORAMA_FEATURE}-JobsDefinitionList-Resume`,
    'org.jupyter.jupyter-scheduler.job-definition-list.delete': `${NB_JOBS_PANORAMA_FEATURE}-JobsDefinitionList-Delete`,
    'org.jupyter.jupyter-scheduler.job-detail.open-input-file': `${NB_JOBS_PANORAMA_FEATURE}-JobsDefinitionList-OpenInputFile`,
    'org.jupyter.jupyter-scheduler.job-detail.open-output-file': `${NB_JOBS_PANORAMA_FEATURE}-JobsDefinitionList-OpenOutputFile`,
    'org.jupyter.jupyter-scheduler.job-detail.delete': `${NB_JOBS_PANORAMA_FEATURE}-JobDetail-Delete`,
    'org.jupyter.jupyter-scheduler.job-detail.stop': `${NB_JOBS_PANORAMA_FEATURE}-JobDetail-Stop`,
    'org.jupyter.jupyter-scheduler.job-detail.download': `${NB_JOBS_PANORAMA_FEATURE}-JobDetail-Download`,
    'org.jupyter.jupyter-scheduler.job-detail.reload': `${NB_JOBS_PANORAMA_FEATURE}-JobDetail-Reload`,
    'org.jupyter.jupyter-scheduler.job-definition-detail.reload': `${NB_JOBS_PANORAMA_FEATURE}-JobDefinitonDetail-Reload`,
    'org.jupyter.jupyter-scheduler.job-definition-detail.run': `${NB_JOBS_PANORAMA_FEATURE}-JobDefinitonDetail-Run`,
    'org.jupyter.jupyter-scheduler.job-definition-detail.pause': `${NB_JOBS_PANORAMA_FEATURE}-JobDefinitonDetail-Pause`,
    'org.jupyter.jupyter-scheduler.job-definition-detail.resume': `${NB_JOBS_PANORAMA_FEATURE}-JobDefinitonDetail-Resume`,
    'org.jupyter.jupyter-scheduler.job-definition-detail.edit': `${NB_JOBS_PANORAMA_FEATURE}-JobDefinitonDetail-Edit`,
    'org.jupyter.jupyter-scheduler.job-definition-detail.delete': `${NB_JOBS_PANORAMA_FEATURE}-JobDefinitonDetail-Delete`,
    'org.jupyter.jupyter-scheduler.job-definition-edit.save': `${NB_JOBS_PANORAMA_FEATURE}-JobDefinitonDetail-Save`,
    'org.jupyter.jupyter-scheduler.job-definition-edit.cancel': `${NB_JOBS_PANORAMA_FEATURE}-JobDefinitonEdit-Cancel`
};
const schedulerTelemetryHandler = async (eventLog) => {
    var _a;
    let eventDetail;
    const eventMapping = (_a = EVENT_MAPPING[eventLog.body.name]) !== null && _a !== void 0 ? _a : eventLog.body.name;
    if (eventLog.body.detail) {
        eventDetail = JSON.stringify({
            name: eventMapping,
            error: eventLog.body.detail
        });
    }
    else {
        eventDetail = eventMapping;
    }
    if (window && window.panorama) {
        window.panorama('trackCustomEvent', {
            eventType: PanoramaDataAnalyticsType.eventDetail,
            eventDetail: eventDetail,
            eventContext: NB_JOBS_PANORAMA_FEATURE,
            timestamp: eventLog.timestamp.getTime()
        });
    }
};
const SchedulerTelemetryPlugin = {
    id: pluginIds.TelemetryPlugin,
    autoStart: true,
    provides: Scheduler.TelemetryHandler,
    activate: (app) => {
        return schedulerTelemetryHandler;
    }
};
export { SchedulerTelemetryPlugin };
//# sourceMappingURL=SchedulerTelemetryPlugin.js.map