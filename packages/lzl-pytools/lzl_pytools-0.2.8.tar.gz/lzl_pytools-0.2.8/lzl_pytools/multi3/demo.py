import aiohttp
import asyncio
import json
import random
import time
import uuid
import traceback

from .multi_process_mng import (defautl_logger_setup, start_multi_task, 
                                run_aio_parallel_task, AioHttpRunProc, ProcessProc)
from .parallel_config import ParallelConfig, AioParallelConfig

class DemoProducerProc(ProcessProc):
    def pre_start(self):
        self.critical(f'{self.p_idx} producer start.')
        self.idx = 0
    def step_run(self):
        self.idx += 1
        if self.idx > 10:
            self.warning(f'{self.p_idx} put over 10.')
            return 'norun', True
        try:
            for i in range(3):
                import random
                time.sleep(random.randint(1, 100)/100)
                self.put_data({'data': uuid.uuid4().hex, 'p_idx': self.p_idx})
            return 'success', False
        except:
            self.error(f'excet: {traceback.format_exc()}')
            return 'except', False

class DemoConsumerProc(ProcessProc):
    def pre_start(self):
        self.critical(f'{self.p_idx} consumer start.')
    def step_run(self):
        data = self.get_data()
        if data is None:
            time.sleep(0.01)
            return 'norun', False
        try:
            import random
            time.sleep(random.randint(1, 100)/100)
        except:
            self.error(f'excet: {traceback.format_exc()}')
            return 'except', False
        return 'success', False

class DemoReqDataBuildProc(ProcessProc):
    def pre_start(self):
        self.host = self.user_data['data'].get('host', 'http://127.0.0.1:8080')
    def step_run(self):
        url = f'{self.host}/search'
        header = {'Content-Type': 'application/json'}
        body = json.dumps({'test': 123})
        time.sleep(random.random())
        self.queue.put([url, header, body])
        return 'success', False

class DemoAioHttpRunProc(AioHttpRunProc):
    async def _req(self, session: aiohttp.ClientSession, req_data):
        try:
            await asyncio.sleep(random.random() * 2)
        except:
            await asyncio.sleep(0.01)
            return 'except'
        return 'success'

def _test():
    start_multi_task(ParallelConfig(run_time_len=10), DemoProducerProc, DemoConsumerProc)

def _test2():
    run_aio_parallel_task(AioParallelConfig(), DemoReqDataBuildProc, DemoAioHttpRunProc)

if __name__ == '__main__':
    defautl_logger_setup(file_show_log=False, stdout_show_log=True)
    _test()