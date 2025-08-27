import { OPTIONS_TYPE, fetchApiResponse } from './FetchApiService';
import { SMUS_STARTUP_NOTIFICATIONS_ENDPOINT } from '../constants';
import { Notification } from '@jupyterlab/apputils';
import { NotificationStatus, PostStartupStatus } from '../types/startup-notifications';

const DEFAULT_POLLING_DURATION = 1000 * 60 * 5; // 5 minutes
const DEFAULT_POLLING_INTERVAL = 1000 * 2; // 2 seconds
const DEFAULT_SUCCESS_NOTIFICATION_VISIBLE_TIME = 1000 * 5; // 5 seconds

export class PostStartupNotificationsService {
  inProgressNotificationId: string | undefined;
  
  constructor() {
    this.inProgressNotificationId = undefined;
  }

  // Simple method to check if user has seen a notification
  private hasUserSeen(notificationId: string): boolean {
    return localStorage.getItem(`notification_seen_${notificationId}`) === 'true';
  }

  // Simple method to mark notification as seen
  private markAsSeen(notificationId: string): void {
    localStorage.setItem(`notification_seen_${notificationId}`, 'true');
  }
  public async initialize() {
    const postStartupStatus = await this.getPostStartupStatus();

    if (postStartupStatus?.status && postStartupStatus.status !== 'success') {
      this.dispatchNotification(postStartupStatus);
      if (!this.isTerminalStatus(postStartupStatus.status)) this.pollStartupStatus();
    }

    // Show custom notification if user hasn't seen it
    this.showCustomNotificationIfNeeded();
  }

  // Show Q CLI notification if user hasn't seen it before
  private showCustomNotificationIfNeeded(): void {
    const customNotificationId = 'smus_q_cli_notification';
    const message = 'The Amazon Q Command Line Interface (CLI) is installed. You can now access AI-powered assistance in your terminal.';
    const link = 'https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/q-actions.html';
    const linkLabel = 'Learn More';
    
    if (!this.hasUserSeen(customNotificationId)) {
      // Create action with link
      const actions = [{
        label: linkLabel,
        callback: () => {
          this.markAsSeen(customNotificationId);
          window.open(link, '_blank');
        }
      }];

      // Show notification
      Notification.emit(message, NotificationStatus.INFO, {
        actions,
        autoClose: false
      });
      
      // Mark as seen when notification is dismissed (clicked X)
      setTimeout(() => this.markAsSeen(customNotificationId), 100);
    }
  }

  private async getPostStartupStatus(): Promise<PostStartupStatus | undefined> {
    try {
      const response = await fetchApiResponse(SMUS_STARTUP_NOTIFICATIONS_ENDPOINT, OPTIONS_TYPE.GET);
      return (await response.json()) as PostStartupStatus;
    } catch {
      this.dispatchNotification({
        status: NotificationStatus.ERROR,
        message: 'Failed to fetch post-startup status.',
      });
      return;
    }
  }

  pollStartupStatus(duration = DEFAULT_POLLING_DURATION, interval = DEFAULT_POLLING_INTERVAL) {
    const pollInterval = setInterval(async () => {
      const postStartupStatus = await this.getPostStartupStatus();

      if (postStartupStatus?.status && this.isTerminalStatus(postStartupStatus?.status)) {
        this.dispatchNotification(postStartupStatus);
        clearInterval(pollInterval);
        clearTimeout(timeoutId);
      }
    }, interval);

    const timeoutId = setTimeout(() => {
      clearInterval(pollInterval);
      this.clearInProgressNotification();
      this.dispatchNotification({
        status: NotificationStatus.INFO,
        message:
          // message longer than 140 characters is truncated
          'IDE configuration is still running. Refresh the page to retry and contact your administrator if configuration fails to complete.',
      });
    }, duration);
  }

  private dispatchNotification(postStartupStatus: PostStartupStatus): void {
    const { message, status, link, label } = postStartupStatus;
    // clear in-progress notification when terminal state is reached.
    if (this.isTerminalStatus(status) && this.inProgressNotificationId) {
      this.clearInProgressNotification();
    }

    const notificationId = Notification.emit(message, status, {
      actions: postStartupStatus.link
        ? [{ label: label ?? 'Learn more', callback: () => window.open(link, '_blank') }]
        : undefined,
      autoClose: status === NotificationStatus.SUCCESS ? DEFAULT_SUCCESS_NOTIFICATION_VISIBLE_TIME : false,
    });

    if (status === NotificationStatus.IN_PROGRESS) {
      this.inProgressNotificationId = notificationId;
    }
  }

  private clearInProgressNotification(): void {
    Notification.dismiss(this.inProgressNotificationId);
  }

  private isTerminalStatus(notificationType: NotificationStatus) {
    return [NotificationStatus.SUCCESS, NotificationStatus.ERROR].includes(notificationType);
  }
}
