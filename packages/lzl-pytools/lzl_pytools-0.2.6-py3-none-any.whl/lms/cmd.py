import os
import sys
import yaml
import argparse
import logging
import traceback
from dataclasses import dataclass, asdict

from lms.lms_client import LmsClient
from lms.lms_req_builder import LmsReqBuilder
from lzl_pytools.multi3.multi_process_mng import defautl_logger_setup
from lzl_pytools.multi3.parallel_config import DataClassArgsTools

logger = logging.getLogger()

@dataclass
class LmsCfg:
    HOST: str = 'http://127.0.0.1:19530'
    store_name: str = 'lms'
    collection_name: str = 'lmstest'
    template_path: str = 'template.yaml'
    timeout: int = 300
    log_level: str = 'WARNING'
    AK: str = ''
    SK: str = ''
    cert: str = ''

    def add_argument(self, parser):
        DataClassArgsTools.add_arguments(self, parser)

    def from_parser(self, args):
        DataClassArgsTools.update_from_args(self, args)

class LmsCmd:
    def __init__(self, cfg: LmsCfg) -> None:
        self.cfg = cfg
        self.lms = LmsClient(cfg.HOST, cfg.AK, cfg.SK, cfg.timeout, cfg.cert)
        self.single_cmd = False
        self.cmd_map = {
            '1': lambda: self.set_cur_store(),
            '2': lambda: self.set_cur_collection(),

            '11': lambda: self.lms.stores_list(),
            '12': lambda: self.lms.stores_create(self.cfg.store_name),
            '13': lambda: self.get_confirm(f'Please confirm whether to delete store({self.cfg.store_name})?',
                                           lambda: self.lms.stores_delete(self.cfg.store_name)),
            '14': lambda: self.get_confirm('Please confirm whether to delete (all collections and all stores)?', 
                                           lambda: self.lms.delete_all_stores()),

            '21': lambda: self.lms.collections_list(self.cfg.store_name),
            '22': lambda: self.lms.collections_describe(self.cfg.store_name, self.cfg.collection_name),
            '23': lambda: self.lms.collections_load(self.cfg.store_name, self.cfg.collection_name),
            '24': lambda: self.lms.collections_release(self.cfg.store_name, self.cfg.collection_name),
            '25': lambda: self.get_confirm(f'Please confirm whether to delete collection({self.cfg.collection_name})?',
                                           lambda: self.lms.collections_delete(self.cfg.store_name, self.cfg.collection_name)),
            '26': lambda: self.lms.print_collection_describe(self.cfg.store_name, self.cfg.collection_name),

            '31': lambda: self.get_confirm(f"Please confirm whether to load (all collections)?",
                                           lambda: self.lms.load_all_collection(self.cfg.store_name)),
            '32': lambda: self.get_confirm(f"Please confirm whether to release (all collections)?",
                                           lambda: self.lms.release_all_collection(self.cfg.store_name)),
            '33': lambda: self.lms.simple_describe_all_collection(self.cfg.store_name),
            '34': lambda: self.get_confirm(f"Please confirm whether to delete (all collections)?",
                                           lambda: self.lms.delete_all_collection(self.cfg.store_name)),

            '51': lambda: self.index_option(self.lms.indexes_describe),
            '52': lambda: self.index_option(self.lms.indexes_get_progress),
            '53': lambda: self.index_option(self.lms.indexes_delete),

            '41': lambda: self.lms.entities_search(LmsReqBuilder(self.cfg.template_path).gen_search_req(self.cfg.store_name, self.cfg.collection_name)),
            '42': lambda: self.lms.entities_insert(LmsReqBuilder(self.cfg.template_path).gen_insert_req(self.cfg.store_name, self.cfg.collection_name)),
            '43': lambda: self.lms.collections_create(LmsReqBuilder(self.cfg.template_path).gen_collection_req(self.cfg.store_name, self.cfg.collection_name)),
            '44': lambda: self.lms.indexes_create(LmsReqBuilder(self.cfg.template_path).gen_index_req(self.cfg.store_name, self.cfg.collection_name)),
            '45': lambda: self.lms.entities_query(LmsReqBuilder(self.cfg.template_path).gen_query_req(self.cfg.store_name, self.cfg.collection_name)),
            '46': lambda: self.lms.entities_delete(LmsReqBuilder(self.cfg.template_path).gen_entity_delete_req(self.cfg.store_name, self.cfg.collection_name)),
        }
    def print_pre_info(self):
        print('\n' + '*'*60)

    def print_end_info(self):
        print('--  '*15)

    def print_cmds(self):
        print(f"*\033[31m    cur cfg: store_name='{self.cfg.store_name}' collection_name='{self.cfg.collection_name}' template_path='{self.cfg.template_path}'\033[0m")
        print("* set cur cfg:  1.store_name    2.collection_name")
        print("*       store: 11.list      12.create        13.delete        14.delete all")
        print("*  collection: 21.list      22.describe      23.load          24.release  25.delete  26.describe2")
        print("*              31.load all  32.release all   33.describe all  34 delete all")
        print("*       index: 51.describe  52.get-progress  53.delete")
        print("*    yaml cmd: 41.search    42.insert        43.create-collection  44.create-index  45.query  46.delete entity")

    def get_confirme(self, info, func):
        if self.single_cmd:  # 如果是执行单条命令，不用确认
            return func()
        while True:
            cmd = input(f"{info} [y/n]: ").strip()
            if cmd.lower() == 'y':
                return func()
            elif cmd.lower() == 'n':
                return 'no opt'

    def index_option(self, func):
        rslt = self.select_index()
        if rslt is None:
            return
        return func(*rslt)

    def select_index(self):
        datas = self.lms.collections_describe(self.cfg.store_name, self.cfg.collection_name)['data']['indexes']
        self.print_pre_info()
        print(f"collection({self.cfg.store_name}:{self.cfg.collection_name}) has indexes:")
        for idx, index in enumerate(datas):
            print(f"  {idx}: field_name={index['field_name']}, index_name={index['index_name']}")
        print('  q: quit')
        self.print_end_info()

        cmd = input('==> Please select a index: ').strip()
        if cmd == 'q':
            return
        try:
            idx = eval(cmd)
            if type(idx) == int and idx >= 0 and idx < len(datas):
                return self.cfg.store_name, self.cfg.collection_name, datas[idx]['index_name'], datas[idx]['field_name']
            else:
                print(f'Error: input should be in [0, {len(datas)})')
        except:
            print('==> Error: input is error! Please retry input!')

    def set_cur_store(self):
        stores = self.lms.list_stores_names()
        stores.sort()

        self.print_pre_info()
        print(f"*\033[31m    cur cfg: store_name='{self.cfg.store_name}' collection_name='{self.cfg.collection_name}' template_path='{self.cfg.template_path}'\033[0m")
        print('all store_names:')
        for idx, store_name in enumerate(stores):
            print(f"   {idx}: {store_name}", end='')
        print('')
        print(' new: create a new store_name')
        print('   q: quit')
        self.print_end_info()

        cmd = input('==> Please select exist store_name or new store_name: ').strip()
        if cmd == 'q':
            return
        elif cmd == 'new':
            new_store_name = input('==> Please input new store_name: ')
            self.cfg.store_name = new_store_name
            print(f'OK: cur store_name={self.cfg.store_name}')
            return
        else:
            try:
                idx = eval(cmd)
                if type(idx) == int and idx >= 0 and idx < len(stores):
                    self.cfg.store_name = stores[idx]
                    print(f'OK: cur store_name={self.cfg.store_name}')
                else:
                    print(f'Error: input should be in [0, {len(stores)})')
            except:
                print('==> Error: input is error! Please retry input!')

    def set_cur_collection(self):
        collections = self.lms.collections_list(self.cfg.store_name)
        collections.sort()

        self.print_pre_info()
        print(f"*\033[31m    cur cfg: store_name='{self.cfg.store_name}' collection_name='{self.cfg.collection_name}' template_path='{self.cfg.template_path}'\033[0m")
        print('all collection_names:')
        for idx, store_name in enumerate(collections):
            print(f"   {idx}: {store_name}", end='')
        print('')
        print(' new: create a new collection_name')
        print('   q: quit')
        self.print_end_info()

        cmd = input('==> Please select exist collection_name or new collection_name: ').strip()
        if cmd == 'q':
            return
        elif cmd == 'new':
            new_collection_name = input('==> Please input new collection_name: ')
            self.cfg.collection_name = new_collection_name
            print(f'OK: cur collection_name={self.cfg.collection_name}')
            return
        else:
            try:
                idx = eval(cmd)
                if type(idx) == int and idx >= 0 and idx < len(collections):
                    self.cfg.collection_name = collections[idx]
                    print(f'OK: cur collection_name={self.cfg.collection_name}')
                else:
                    print(f'Error: input should be in [0, {len(collections)})')
            except:
                print('==> Error: input is error! Please retry input!')

    def get_confirm(self, info, func):
        if self.single_cmd:
            return func()
        while True:
            cmd = input(info + ' [y/n]: ').strip()
            if cmd.lower() == 'y':
                return func()
            elif cmd.lower() == 'n':
                return 'no opt'

    def run_one(self, cmd):
        self.single_cmd = True
        if cmd in self.cmd_map:
            print('\n==> ', self.cmd_map[cmd]())
        else:
            print('==> Error: input is error! Please retry input!')

    def run(self):
        self.single_cmd = False
        while True:
            self.print_pre_info()
            self.print_cmds()
            print("* input q to exit")
            self.print_end_info()
            cmd = input('==> Please input cmd index: ').strip()
            if cmd == 'q':
                return
            try:
                if cmd in self.cmd_map:
                    print('\n==> ', self.cmd_map[cmd]())
                else:
                    print('==> Error: input is error! Please retry input!')
            except:
                traceback.print_exc()

def add_argument():
    dftCfg = LmsCfg()
    parser = argparse.ArgumentParser()
    parser.add_argument('--init_yaml_cfg', action='store_true', default=False, help='')
    parser.add_argument('--single_cmd', type=str, default='', help='only run one command')
    parser.add_argument('-f', '--config', type=str, default='cfg.yaml', help='yaml config path')

    dftCfg.add_argument(parser)
    return parser

def parse_args(parser):
    args = parser.parse_args()
    if args.config != '' and os.path.isfile(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
            obj = yaml.safe_load(f)
            lmscfg = LmsCfg(**obj)
    else:
        print(f'not find config file({args.config}), use default config.')
        lmscfg = LmsCfg()
    lmscfg.from_parser(args)
    raise lmscfg, args

def main():
    parser = add_argument()
    lmscfg, args = parse_args(parser)

    log_level_map = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING, 'error': logging.ERROR}
    log_level = log_level_map.get(lmscfg.log_level.lower(), logging.WARNING)
    defautl_logger_setup(stdout_show_log=True, file_show_log=False, log_level=log_level, log_dir='logs')

    if args.init_yaml_cfg:
        with open('cfg.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(asdict(lmscfg), f)
        with open('template.yaml', 'w', encoding='utf-8') as f:
            f.writelines(template_text)
        print('save config files: cfg.yaml, template.yaml')
        return 0

    if args.single_cmd != '':
        LmsCmd(lmscfg).run_one(args.single_cmd)
        return 0

    try:
        LmsCmd(lmscfg).run()
    except KeyboardInterrupt:
        print('\nCtrl+C stop...')
    return 0

template_text = '''
collection:
  primary_field:
    name: uuid
    type: String
  fields:
    - data_type: FloatVector
      field_name: vector
      element_type_params:
        dim: 1024
    - data_type: Int64
      field_name: group
    - data_type: String
      field_name: url
insert:
  data:
    __template_list_size: 10
    uuid: '__template: uuid.uuid4().hex'
    url: ''
    group: '__template: random.randint(0, 100)'
    vector: '__template: gen_random_vector(1024)'
search:
  top_k: 10
  vector: '__template: gen_random_vector(1024)'
  vector_field: 'vector'
  output_fields: []
  params:
    search_list: 20
index:
  index_params:
    field_name: vector
    index_name: vector_index
    params:
      metric_type: L2
      index_type: HANNS
query:
  top_k: -1
  filter: 'group > 0'
  output_fields: ["count(*)"]
entity_delete:
  filter: 'group > 0'
'''

if __name__ == '__main__':
    main()