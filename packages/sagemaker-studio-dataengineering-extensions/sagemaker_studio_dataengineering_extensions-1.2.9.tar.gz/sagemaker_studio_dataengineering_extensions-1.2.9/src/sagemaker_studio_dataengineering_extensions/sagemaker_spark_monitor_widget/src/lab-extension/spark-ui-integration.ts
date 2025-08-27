/**
 * Spark UI Integration using Session Info
 * 
 * This module provides integration between the Spark Monitor Widget and the 
 * DebuggingJLPlugin compute handlers using session info from WebSocket messages.
 */

import { SessionInfo } from '../store/session-info';
import { LINK_TYPE_SPARK_UI } from './debugging-plugin/constants';
import { getConnectionDetails } from './debugging-plugin/utils/jupyter_api_client';
import { handleGlueDebuggingLinksClicked } from './debugging-plugin/computes/glue';
import { handleEMRonEc2DebuggingLinksClicked } from './debugging-plugin/computes/emr_ec2';
import { handleEMRServerlessDebuggingLinksClicked } from './debugging-plugin/computes/emr_serverless';

/**
 * Triggers Spark UI using session info and DebuggingJLPlugin compute handlers directly
 * 
 * @param sessionInfo - Session information from WebSocket messages
 * @param timeoutMs - Timeout in milliseconds (default: 30000)
 * @returns Promise that resolves when Spark UI is opened or rejects on error
 */
export async function triggerSparkUiWithSessionInfo(
  sessionInfo: SessionInfo, 
  timeoutMs: number = 30000
): Promise<void> {
  console.log(`[Spark UI] Opening UI for ${sessionInfo.connection_type}`);

  try {
    // Validate session info first
    if (!validateSessionInfoForSparkUI(sessionInfo)) {
      throw new Error('Invalid session info - missing required fields');
    }

    // Create timeout promise
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => {
        reject(new Error(`Operation timed out after ${timeoutMs}ms`));
      }, timeoutMs);
    });

    // Create the main operation promise
    const operationPromise = performSparkUIOperation(sessionInfo);

    // Race between operation and timeout
    await Promise.race([operationPromise, timeoutPromise]);
    
    console.log(`[Spark UI] Successfully opened for ${sessionInfo.connection_type}`);
  } catch (error) {
    console.error(`[Spark UI] Failed to open: ${error instanceof Error ? error.message : String(error)}`);
    throw error;
  }
}

/**
 * Performs the actual Spark UI operation by calling compute handlers directly
 * 
 * @param sessionInfo - Validated session information
 * @returns Promise that resolves when operation completes
 */
async function performSparkUIOperation(sessionInfo: SessionInfo): Promise<void> {
  try {
    const applicationId = getApplicationIdFromSessionInfo(sessionInfo);
    const connectionDetail = await getConnectionDetails(sessionInfo.connection_name);
    
    // Call the appropriate compute handler directly based on connection type
    switch (sessionInfo.connection_type) {
      case 'SPARK_GLUE':
        await handleGlueDebuggingLinksClicked(connectionDetail, applicationId, LINK_TYPE_SPARK_UI, '');
        break;
        
      case 'SPARK_EMR_EC2':
        await handleEMRonEc2DebuggingLinksClicked(connectionDetail, applicationId, LINK_TYPE_SPARK_UI, '');
        break;
        
      case 'SPARK_EMR_SERVERLESS':
        await handleEMRServerlessDebuggingLinksClicked(connectionDetail, applicationId, LINK_TYPE_SPARK_UI);
        break;
        
      default:
        throw new Error(`Unsupported connection type: ${sessionInfo.connection_type}`);
    }
  } catch (error) {
    throw new Error(`Compute handler failed: ${error instanceof Error ? error.message : String(error)}`);
  }
}

/**
 * Determines the appropriate application/session ID based on connection type
 * 
 * @param sessionInfo - Session information
 * @returns Application or session ID for the compute type
 * @throws SparkUIError if no valid ID is found
 */
export function getApplicationIdFromSessionInfo(sessionInfo: SessionInfo): string {
  // Future: Use consolidated field if available
  if (sessionInfo.spark_execution_id) {
    return sessionInfo.spark_execution_id;
  }
  
  // Current: Use compute-specific fields
  let applicationId: string;
  
  switch (sessionInfo.connection_type) {
    case 'SPARK_GLUE':
      // Glue uses session_id (e.g., 'dd7pqpq8i209e8-e8c354bc-c6cc-40f0-a950-0190e8cce7e7')
      applicationId = sessionInfo.session_id !== undefined && sessionInfo.session_id !== null 
        ? String(sessionInfo.session_id) 
        : '';
      break;
    case 'SPARK_EMR_SERVERLESS':
      // EMR Serverless: session_id is expected to be 0, use application_id for Job Run ID
      // (e.g., '00ftv7na4881kh0m')
      applicationId = sessionInfo.application_id !== undefined && sessionInfo.application_id !== null 
        ? String(sessionInfo.application_id) 
        : '';
      break;
    case 'SPARK_EMR_EC2':
      // EMR EC2 uses application_id (e.g., 'application_1752107075835_0001')
      applicationId = sessionInfo.application_id !== undefined && sessionInfo.application_id !== null 
        ? String(sessionInfo.application_id) 
        : '';
      break;
    default:
      // Fallback: try session_id first, then application_id
      if (sessionInfo.session_id !== undefined && sessionInfo.session_id !== null) {
        applicationId = String(sessionInfo.session_id);
      } else if (sessionInfo.application_id !== undefined && sessionInfo.application_id !== null) {
        applicationId = String(sessionInfo.application_id);
      } else {
        applicationId = '';
      }
      break;
  }
  
  if (!applicationId) {
    throw new Error(`No application/session ID found for ${sessionInfo.connection_type}`);
  }
  
  return applicationId;
}

/**
 * Validates that session info contains required fields for Spark UI
 * 
 * @param sessionInfo - Session information to validate
 * @returns true if valid, false otherwise
 */
export function validateSessionInfoForSparkUI(sessionInfo: SessionInfo | undefined): sessionInfo is SessionInfo {
  if (!sessionInfo?.connection_type || !sessionInfo?.connection_name) {
    return false;
  }

  try {
    getApplicationIdFromSessionInfo(sessionInfo);
    return true;
  } catch {
    return false;
  }
}
