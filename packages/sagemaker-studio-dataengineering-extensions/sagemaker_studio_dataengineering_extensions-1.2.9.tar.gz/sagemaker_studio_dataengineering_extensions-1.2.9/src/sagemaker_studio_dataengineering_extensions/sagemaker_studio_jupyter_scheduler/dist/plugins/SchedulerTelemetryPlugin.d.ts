import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import { Scheduler } from '@jupyterlab/scheduler';
declare global {
    export interface Window {
        panorama: (methodName: string, eventData: {
            eventType: string;
            eventDetail: string;
            eventContext: string;
            timestamp: number;
        }) => void;
    }
}
declare const SchedulerTelemetryPlugin: JupyterFrontEndPlugin<Scheduler.TelemetryHandler>;
export { SchedulerTelemetryPlugin };
//# sourceMappingURL=SchedulerTelemetryPlugin.d.ts.map