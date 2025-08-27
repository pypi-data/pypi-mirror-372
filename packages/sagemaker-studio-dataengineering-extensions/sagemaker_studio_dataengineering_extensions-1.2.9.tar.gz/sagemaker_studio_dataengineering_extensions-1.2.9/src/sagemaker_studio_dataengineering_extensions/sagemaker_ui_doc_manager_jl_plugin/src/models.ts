import { Contents } from "@jupyterlab/services";

export type DocManagerFileEventPayload = {
  path: string;
  content?: string
  type?: string;
  ext?: string;
  format?: Contents.FileFormat
};

export type DocManagerFileEvent = {
  type: string;
  payload: DocManagerFileEventPayload;
};
