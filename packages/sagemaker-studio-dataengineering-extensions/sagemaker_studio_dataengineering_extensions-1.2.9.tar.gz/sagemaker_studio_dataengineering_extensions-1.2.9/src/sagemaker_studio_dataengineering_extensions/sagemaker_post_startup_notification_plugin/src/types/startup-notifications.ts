import { Notification } from '@jupyterlab/apputils';

enum NotificationStatus {
  INFO = 'info',
  IN_PROGRESS = 'in-progress',
  SUCCESS = 'success',
  WARNING = 'warning',
  ERROR = 'error',
  DEFAULT = 'default',
}

type JupyterLabNotification = {
  type: NotificationStatus;
  /**
   * The message to be presented to the user in the IDE
   * toast notification.
   */
  message: string;
  /**
   * Surfaces a clickable link to users, either directing
   * them to an external link or triggering a callback function.
   */
  actions?: Notification.IAction[];
};

type PostStartupStatus = {
  status: NotificationStatus;
  message: string;
  link?: string;
  label?: string;
};

export { JupyterLabNotification, PostStartupStatus, NotificationStatus };
