import logging
import wmi
from ..maid import ProcessWatchdog

logger = logging.getLogger(__name__)

class RunningWatchdog(ProcessWatchdog):
    def __init__(self, process_name):
        super().__init__(process_name)

    def is_running(self, func):
        self._callbacks['is_running'] = func
        return func

    def check_process_state(self, pids_with_windows):
        try:
            processes = self.c.Win32_Process(name=self.name)
            if processes:
                # Process is running, fire callback every time.
                logger.info(f"'{self.name}' is running. Firing callback.")
                if 'is_running' in self._callbacks:
                    self._callbacks['is_running']()
        except wmi.x_wmi as e:
            logger.error(f"WMI query for '{self.name}' failed: {e}")