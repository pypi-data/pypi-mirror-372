export enum TelemetryEventContext {
  JL_CONNECTION = 'jl-connection',
}

export enum TelemetryEventType {
  CLICK = 'click',
  CHANGE = 'change',
}

export enum RecordType {
  // BI
  RECORD_BI_EVENT = 'RECORD_BI_EVENT',

  // Operational
  RECORD_CUSTOM_EVENT = 'RECORD_CUSTOM_EVENT',
  RECORD_INFO = 'RECORD_INFO',
  RECORD_ERROR = 'RECORD_ERROR',
  RECORD_WARN = 'RECORD_WARN',
}

export interface TelemetryRecordBIEventPayload {
  // The type of the event like CLICK, SCROLL, HOVER
  eventType: string;
  // Context of the event
  eventContext: string;
  // Free-form text field in which to assign values, can be used to add stringified JSON
  eventDetail?: string;
  // A value to apply to the event.
  eventValue?: string;
  // The funnel to filter the event
  funnel?: string;
  // Task ID of the funnel if needed
  taskId?: string;
  // The timestamp for the event. Recommended `Date.now()`
  timestamp?: number;
}

export interface TelemetryRecordCustomEventPayload {
  eventType: string;
  eventData: object;
}

export type TelemetryRecordErrorPayload = ErrorEvent | Error | string;
export type PrimitiveJson = string | number | boolean | object;
export type TelemetryRecordWarnPayload = string;

export const useTelemetryJL = () => {
  const sendMessage = (recordType: RecordType, payload: unknown) => {
    let targetOrigin = window.location !== window.parent.location ? document.referrer : document.location.href;
    targetOrigin = targetOrigin ? new URL(targetOrigin).origin : '';
    window.parent.postMessage(
      {
        messageType: 'JL_user_metrics',
        recordType,
        payload,
      },
      targetOrigin
    );
  };

  const recordBIEvent = (payload: TelemetryRecordBIEventPayload) => {
    sendMessage(RecordType.RECORD_BI_EVENT, payload);
  };

  const recordCustomEvent = (payload: TelemetryRecordCustomEventPayload) => {
    sendMessage(RecordType.RECORD_CUSTOM_EVENT, payload);
  };

  const recordError = (payload: TelemetryRecordErrorPayload) => {
    sendMessage(RecordType.RECORD_ERROR, payload);
  };

  const recordInfo = (payload: PrimitiveJson) => {
    sendMessage(RecordType.RECORD_INFO, payload);
  };

  const recordWarn = (payload: TelemetryRecordWarnPayload) => {
    sendMessage(RecordType.RECORD_WARN, payload);
  };

  return { recordBIEvent, recordCustomEvent, recordError, recordInfo, recordWarn };
};
