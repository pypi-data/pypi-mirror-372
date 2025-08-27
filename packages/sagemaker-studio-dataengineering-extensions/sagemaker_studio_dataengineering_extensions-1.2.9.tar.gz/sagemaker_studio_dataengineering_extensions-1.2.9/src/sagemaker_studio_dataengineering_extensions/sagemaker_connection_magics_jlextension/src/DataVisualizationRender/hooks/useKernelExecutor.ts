import {useEffect, useMemo, useRef, useState} from "react";

import {NotebookPanel} from '@jupyterlab/notebook';
import {Kernel, KernelMessage} from '@jupyterlab/services';


export const useKernelExecutor = (notebookPanel: NotebookPanel, kernelId?: string, timeoutMs: number = 30000): ((code: string, timeoutMs?: number) => Promise<string>) | undefined => {
  const [kernel, setKernel] = useState<Kernel.IKernelConnection>()
  const [exportExecute, setExportExecute] = useState<(code: string, timeoutMs?: number) => Promise<string>>()
  const newStartKernel = useRef(false);

  useEffect(() => {
    const initializeKernel = async (): Promise<Kernel.IKernelConnection | undefined> => {
      if (!notebookPanel) return;

      await notebookPanel.sessionContext.ready;

      notebookPanel.sessionContext.statusChanged.connect((_, status) => {
        if (status === 'restarting' || status === 'starting') {
          setKernel(undefined);
          newStartKernel.current = true;
        } else if (status === 'idle' && newStartKernel.current) {
          const currentKernel = notebookPanel.sessionContext.session?.kernel;
          if (currentKernel) {
            setKernel(currentKernel);
            newStartKernel.current = false;
          }
        }
      });

      return notebookPanel.sessionContext.session?.kernel ?? undefined;
    };

    initializeKernel().then(kernel => setKernel(kernel));
  }, [notebookPanel])

  const execute = useMemo(() => {
    if (!kernelId || !kernel) return undefined;

    async function execute(code: string, functionTimeoutMs: number = timeoutMs): Promise<string> {

      // @ts-ignore
      const future = kernel.requestExecute({
        code,
        stop_on_error: false,
        silent: true
      });

      const outputPromise = new Promise<string>((resolve, reject) => {
        future.onIOPub = (msg: KernelMessage.IIOPubMessage) => {
          const msgType = msg.header.msg_type;

          switch (msgType) {
            case 'stream': {
              // Response from Spark is stream type.
              const text = (msg as KernelMessage.IStreamMsg).content.text.replace("\n", "");
              if (text) {
                resolve(text);
                return;
              }
              break;
            }
            case 'display_data': {
              const content = (msg as KernelMessage.IDisplayDataMsg).content;
              // Skip Sparkmagic progress bar messages
              // Sparkmagic progress bar always contains application/vnd.jupyter.widget-view+json
              if (!('application/vnd.jupyter.widget-view+json' in content.data)) {
                let text = (content.data['text/plain'] as string)
                  // Replace escaped single quotes
                  .replace(/\\'/g, "'");
                if (text.startsWith("'") && text.endsWith("'")) {
                  // Remove the first and last quote if it's a string
                  text = text.slice(1, -1);
                }
                if (text) {
                  resolve(text);
                  return;
                }
              }
              break;
            }
            case 'status': {
              const content = msg.content as KernelMessage.IStatusMsg['content'];
              if (content.execution_state == "idle") {
                resolve("");
              }
              break;
            }
            case 'error': {
              const content = msg.content as KernelMessage.IErrorMsg['content'];
              reject(new Error(`${content.ename}: ${content.evalue}`));
              break;
            }
          }
        };

        future.onStdin = (msg: KernelMessage.IStdinMessage) => {
          reject(new Error('Kernel requested stdin, which is not supported'));
        };
      });

      try {
        return await Promise.race([
          outputPromise,
          new Promise<never>((_, reject) =>
            setTimeout(() => reject(new Error(`Execution timeout after ${functionTimeoutMs}ms`)), functionTimeoutMs)
          )
        ]);
      } finally {
        // Ensure the future is done
        await future.done;
      }
    }

    return execute;
  }, [kernelId, kernel, timeoutMs])

  useEffect(() => {
    if (!execute) {
      setExportExecute(undefined);
      return;
    }

    // Check if the kernel id matches the display kernel id.
    execute(`from IPython import get_ipython\ndisplay(get_ipython().kernel.ident)`)
      .then((response: string) => {
        if (kernelId && response.includes(kernelId)) {
          setExportExecute(() => execute);
        } else {
          setExportExecute(undefined);
        }
      });
  }, [kernelId, execute])

  return exportExecute;
}
