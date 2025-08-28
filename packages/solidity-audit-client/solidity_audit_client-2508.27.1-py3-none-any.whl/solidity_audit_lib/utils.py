from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import os
import signal

__all__ = ["ViolentPoolExecutor"]


class ViolentPoolExecutor(ProcessPoolExecutor):
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.shutdown(wait=False, cancel_futures=True)
        except:
            pass
        super().__exit__(exc_type, exc_val, exc_tb)
        for p in multiprocessing.active_children():
            try:
                os.kill(p.pid, signal.SIGKILL)
            except:
                pass
            p.join()
