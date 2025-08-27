import { Terminal } from '@jupyterlab/services';
import { ReadonlyJSONValue } from '@lumino/coreutils';

enum CommandStatus {
  RUNNING,
  SUCCESS,
  FAILURE,
}

const PRINT_EXIT_CODE_COMMAND = 'echo "EXIT_CODE: $?"';
const PRINT_EXIT_CODE = 'EXIT_CODE:';
const PRINT_EXIT_CODE_ZERO = 'EXIT_CODE: 0';

export function createCommandPromise(terminal: Terminal.ITerminalConnection, commands: string[]) {
  let status = CommandStatus.RUNNING;
  let executingCommands = commands.length;

  function terminalMonitor(terminal: Terminal.ITerminalConnection, message: Terminal.IMessage) {
    if (message.type === 'stdout' && message.content) {
      message.content.forEach(content => {
        if (status == CommandStatus.RUNNING && typeof content == 'string') {
          if (!content.includes(PRINT_EXIT_CODE_COMMAND) && content.includes(PRINT_EXIT_CODE)) {
            if (content.includes(PRINT_EXIT_CODE_ZERO)) {
              executingCommands--;
              if (!executingCommands) {
                status = CommandStatus.SUCCESS;
              }
            } else {
              // If any command returns non 0 exit code, stop monitoring and set the status to FAILED
              status = CommandStatus.FAILURE;
              terminal.messageReceived.disconnect(terminalMonitor);
            }
          }
        }
      });
    }
  }
  terminal.messageReceived.connect(terminalMonitor);

  let command = commands.join(`;${PRINT_EXIT_CODE_COMMAND};`);

  command += `;${PRINT_EXIT_CODE_COMMAND}\n;`;
  terminal.send({ type: 'stdin', content: [command] });

  return new Promise<ReadonlyJSONValue>((resolve, reject) => {
    setInterval(() => {
      if (status == CommandStatus.SUCCESS) {
        resolve({});
        terminal.messageReceived.disconnect(terminalMonitor);
        terminal.shutdown();
      } else if (status == CommandStatus.FAILURE) {
        reject();
        terminal.messageReceived.disconnect(terminalMonitor);
      }
    }, 1000);
  });
}
