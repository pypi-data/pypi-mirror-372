import os
import time
import sys
import logging
from lzl_pytools.multi3.multi_process_mng import defautl_logger_setup

GROUP_DIR_NAME = 'group_logs'
FINISH_MIN_ENTITY_COUNT = 20000

def group_by_sizes(start, end, func, group_sizes, data={}):
    if len(group_sizes) == 0:
        raise Exception(f'group_sizes({group_sizes}) para error.')
    group_size = group_sizes[0]
    group_num = int((end - start + group_size - 1) / group_size)
    next_group_size = group_sizes[1:]
    for idx in range(group_num):
        group_start = start + group_size * idx
        group_end = min(group_start + group_size, end)
        group_data = data.copy()
        is_finish = func(group_start, group_end, group_size, group_num, idx, group_data)
        if not is_finish:
            group_by_sizes(group_start, group_end, func, next_group_size, group_data)

# gidx = 0
# def query_data(start, end):
#     global gidx
#     gidx += 1
#     # paras = [0, 100, 20000]
#     paras = [30000, 20000]
#     return paras[gidx % len(paras)]

def group_to_logs_by_times(start, end, query_func, group_sizes=[24*60*60*1000, 60*60*1000, 60*1000, 1000, 10, 1]):
    # query_func(start, end) -> find_count : 
    errors = []
    def check_finish(group_start, group_end, group_size, group_num, idx, data):
        if 'logger' not in data:
            name = f"{group_start}.{group_end}.log"
            data['logger'] = logging.getLogger(name)
            defautl_logger_setup(data['logger'], name, log_dir=GROUP_DIR_NAME, file_delay=True)
        # data['logger'].error(f">{group_start}.{group_end}.{group_size}.{group_num}, {idx}")
        cnt = query_func(group_start, group_end)
        if cnt == 0:
            return True
        if cnt <= FINISH_MIN_ENTITY_COUNT:
            data['logger'].error(f">{group_start}.{group_end}.{group_size}.{cnt}")
            return True
        if group_size == group_sizes[-1]:
            errors.append(f">{group_start}.{group_end}.{group_size}.{cnt}")
            return True
        return False
    group_by_sizes(start, end, check_finish, group_sizes)
    # print('========> errors', errors)
    return errors

# start = int(time.time()*1000)
# start = 0
# end = 60*1000 + 1000
# # end = start + 3*24*60*60*1000 + 3563
# group_by_times(start, end)
