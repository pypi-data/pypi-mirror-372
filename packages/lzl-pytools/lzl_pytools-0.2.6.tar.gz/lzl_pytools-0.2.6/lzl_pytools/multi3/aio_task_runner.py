import time
import asyncio
import random
import logging
import aiohttp

logger = logging.getLogger()

class AioTaskRunner:
    def __init__(self, max_req_num=-1, sec_task_callback=None, sec_task_data=None) -> None:
        self.max_req_num = max_req_num
        self.task_idx = 0
        self.stop_flag = False
        self.tasks = set()
        self.seconde_task = None

        self.sec_task_callback = sec_task_callback
        self.sec_task_data = sec_task_data
    def stop(self):
        self.stop_flag = True
        if self.seconde_task:
            self.seconde_task.cancel()
            self.seconde_task = None
        for t in self.tasks:
            t.cancel()
    async def _second_task_proc(self, callback, user_data):
        try:
            prev_second = int(time.time())
            while True:
                cur_second = int(time.time())
                if prev_second != cur_second:
                    if callback:
                        callback(user_data)
                    prev_second = cur_second
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.info('counter task canceled')

    async def _task_proc(self, session, task_callback, parallet_id, user_data):
        task_idx = self.task_idx
        self.task_idx += 1
        await task_callback(session, parallet_id, task_idx, user_data)

    async def _parallelRunProc(self, session, task_callback, parallet_id, user_data):
        while True:
            if self.stop_flag:
                break
            if self.max_req_num > 0 and self.task_idx >= self.max_req_num:
                break
            await self._task_proc(session, task_callback, parallet_id, user_data)
    async def parallel_run(self, parallet_num, task_callback, user_data=None):   # fix parallet num, when task over run the next task
        if self.sec_task_callback:
            self.seconde_task = asyncio.create_task(self._second_task_proc(self.sec_task_callback, self.sec_task_data))
        async with aiohttp.ClientSession() as session:
            self.tasks = set([asyncio.create_task(self._parallelRunProc(session, task_callback, i, user_data)) for i in range(0, parallet_num)])
            await asyncio.gather(*self.tasks)
            self.tasks = []
            await asyncio.sleep(1)   # wait second task
    async def run_times_per_second(self, parallet_num, task_callback, user_data=None):  # fix task num per second. do not wait task over.
        if self.sec_task_callback:
            self.seconde_task = asyncio.create_task(self._second_task_proc(self.sec_task_callback, self.sec_task_data))
        async with aiohttp.ClientSession() as session:
            self.tasks = set()
            prev_second = int(time.time())
            while True:
                if self.stop_flag:
                    break
                if self.max_req_num > 0 and self.task_idx >= self.max_req_num:
                    break
                current_second = int(time.time())
                if current_second != prev_second:
                    prev_second = current_second  
                    # create fix number tasks
                    new_tasks = [asyncio.create_task(self._task_proc(session, task_callback, i, user_data)) for i in range(parallet_num)]
                    self.tasks.update(new_tasks)
                    if self.tasks:
                        done_tasks, self.tasks = await asyncio.wait(self.tasks, timeout=0)
                        for task in done_tasks:
                            try:
                                task.result()
                            except:
                                pass
                await asyncio.sleep(0.01)
            await asyncio.gather(*self.tasks)
            self.tasks = []
            await asyncio.sleep(1)   # wait second task

def _test():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s -- %(message)s")
    obj = {'cnt': 0}
    from multi_process_mng import TaskMonitorInfo
    tmi = TaskMonitorInfo()
    async def task_callback(session, parallet_id, task_idx, user_data):
        start_time = time.time()
        tmi.rec_start()
        user_data['cnt'] += 1
        print('==>', user_data['cnt'], parallet_id, task_idx, user_data)
        await asyncio.sleep(random.random() * 2)
        tmi.rec_end('success', time.time() - start_time)
    runner = AioTaskRunner(20, sec_task_callback=lambda para: logger.warning(f'{tmi}'), sec_task_data=logger)
    try:
        asyncio.run(runner.parallel_run(10, task_callback, obj))
    except KeyboardInterrupt:
        runner.stop()

if __name__ == '__main__':
    _test()
