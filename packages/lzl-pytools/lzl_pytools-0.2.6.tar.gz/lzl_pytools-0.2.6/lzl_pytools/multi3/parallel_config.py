from dataclasses import dataclass, asdict
import argparse

class DataClassArgsTools:
    @staticmethod
    def add_arguments(dataclass_obj, parser: argparse.ArgumentParser):
        obj = asdict(dataclass_obj)
        for k,v in obj.items():
            parser.add_argument(f"--{k}", type=type(v), default=argparse.SUPPRESS, help=f'default={v}')

    @staticmethod
    def update_from_args(dataclass_obj, args):
        obj = asdict(dataclass_obj)
        for k in obj.keys():
            if k in args:
                setattr(dataclass_obj, k, getattr(args, k))

@dataclass
class ParallelConfig:
    producer_num : int = 5
    consumer_num : int = 2
    queue_size : int = 100
    queue_num : int = 1
    run_time_len : int = -1
    max_task_num : int = -1

    def add_argument(self, parser):
        DataClassArgsTools.add_arguments(self, parser)

    def from_parser(self, args):
        DataClassArgsTools.update_from_args(self, args)

@dataclass
class AioParallelConfig(ParallelConfig):
    aio_parallel_num : int = 5
    one_parallel_task_num : int = -1
    no_wait : bool = False
    aio_timeout : int = 300

@dataclass
class TaskMonitorInfo:
    begin : int = 0
    end : int = 0
    success_cnt : int = 0
    fail_cnt : int = 0
    except_cnt : int = 0
    time : float = 0
    msg : int = 0

    def rec_start(self):
        self.begin += 1
    def rec_end(self, rslt, cost_time):
        self.end += 1
        if rslt in ['success', 'fail', 'except']:
            setattr(self, rslt + '_cnt', getattr(self, rslt + '_cnt') + 1)
        self.time += cost_time
    def reverse_start(self):
        self.begin -= 1
    def rec_msg(self):
        self.msg += 1
    def clear(self):
        self.begin = 0
        self.end = 0
        self.success_cnt = 0
        self.fail_cnt = 0
        self.except_cnt = 0
        self.time = 0
        self.msg = 0
    def __str__(self):
        avg_time = self.time / self.success_cnt if self.success_cnt > 0 else 0
        return f"msg/start/stop={self.msg}/{self.begin}/{self.end},s/f/e={self.success_cnt}/{self.fail_cnt}/{self.except_cnt},avg_time={avg_time:.4f}"
    def add_one_json(self, task_monitor_info):
        for k,v in task_monitor_info.items():
            setattr(self, k, getattr(self, k) + v)
    def to_json(self):
        return asdict(self)
    def get_json_and_clear(self):
        obj =  self.to_json()
        self.clear()
        return obj
