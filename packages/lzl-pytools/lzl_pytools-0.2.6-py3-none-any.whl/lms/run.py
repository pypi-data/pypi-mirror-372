import os
import sys
import argparse
import logging
import yaml
from dataclasses import asdict

from lzl_pytools.multi3.parallel_config import AioParallelConfig
from lzl_pytools.multi3.multi_process_mng import defautl_logger_setup, run_aio_parallel_task
from lms.lms_sub_proc import (InsertReqBuildProc, UpsertReqBuildProc, SearchReqBuildProc, QueryReqBuildProc, 
                              InsertReqBuildProcReplaceInt, UpsertReqBuildProcReplaceInt, AioHttpSendProc)
from lms.cmd import LmsCfg

logger = logging.getLogger()

class LmsRun:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        self.parallel_cfg = AioParallelConfig()
        self.dftCfg = LmsCfg()
        self.lmscfg = None
        self.task_type = 'insert'
        self.args = None

    def add_argument(self):
        self.parser.add_argument('-t', '--task_type', type=str, default='insert', help='')
        self.parser.add_argument('-f', '--config', type=str, default='cfg.yaml', help='')
        self.parser.add_argument('--replace_field_name', type=str, default='', help='')
        self.parser.add_argument('--start', type=int, default=0, help='')
        self.parser.add_argument('--end', type=int, default=1000, help='')
        self.parser.add_argument('--group_num', type=int, default=100, help='')

        self.dftCfg.add_argument(self.parser)
        self.parallel_cfg.add_argument(self.parser)

    def parse_args(self):
        args = self.parser.parse_args()
        self.args = args
        if args.config != '' and os.path.isfile(args.config):
            with open(args.config, 'r', encoding='utf-8') as f:
                obj = yaml.safe_load(f)
                self.lmscfg = LmsCfg(**obj)
        else:
            print(f'not find config file({args.config}), use default config.')
            self.lmscfg = LmsCfg()
        self.lmscfg.from_parser(args)
        self.parallel_cfg.from_parser(args)
        self.task_type = args.task_type

    def _start(self):
        args = self.args
        data = {'lms_cfg': asdict(self.lmscfg), 'task_type': self.task_type}
        build_class = None
        if args.replace_field_name != '':
            data['group_queue'] = InsertReqBuildProcReplaceInt.init_queue(args.start, args.end, args.group_num)
            data['replace_field_name'] = args.replace_field_name
            if self.task_type == 'insert':
                build_class = InsertReqBuildProcReplaceInt
            elif self.task_type == 'upsert': 
                build_class = UpsertReqBuildProcReplaceInt
        else:
            if self.task_type == 'insert':
                build_class = InsertReqBuildProc
            elif self.task_type == 'upsert': 
                build_class = UpsertReqBuildProc
            elif self.task_type == 'search': 
                build_class = SearchReqBuildProc
            elif self.task_type == 'query': 
                build_class = QueryReqBuildProc

        if build_class is None:
            raise Exception(f'task_type is error: {self.task_type}')
        run_aio_parallel_task(self.parallel_cfg, build_class, AioHttpSendProc, data)

    def run(self):
        self.add_argument()
        self.parse_args()

        defautl_logger_setup(log_dir='logs', stdout_show_log=True)
        logger.warning(f'task_type={self.task_type}, {self.lmscfg}, {self.parallel_cfg}')
        self._start()

def main():
    LmsRun().run()
    return 0

if __name__ == '__main__':
    sys.exit(main())