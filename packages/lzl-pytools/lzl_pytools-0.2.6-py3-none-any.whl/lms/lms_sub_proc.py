import aiohttp
import asyncio
import json
import time
import traceback
import multiprocessing
import queue

from lzl_pytools.multi3.multi_process_mng import ProcessProc, AioHttpRunProc, split_range
from .lms_req_builder import LmsReqBuilder
from .lms_client import sign

class InsertReqBuildProc(ProcessProc):
    def pre_start(self):
        self.info(f'{self.p_idx} producer start.')
        self.lms_cfg = self.user_data.get('data').get('lms_cfg')
        self.builder = LmsReqBuilder(self.lms_cfg['template_path'])

    def gen_data(self, lms_cfg):
        url = f"{lms_cfg['HOST']}/v1/entities/insert"
        req = self.builder.gen_insert_req(lms_cfg['store_name'], lms_cfg['collection_name'])
        return url, req

    def step_run(self):
        try:
            lms_cfg = self.lms_cfg
            headers = {'Content-Type': 'application/json'}
            url, req = self.gen_data(lms_cfg)
            url, headers, body = sign(url, headers, json.dumps(req), lms_cfg['AK'], lms_cfg['SK'])
            self.put_data([url, headers, body])
            return 'success', False
        except:
            self.error(f'excet: {traceback.format_exc()}')
            time.sleep(0.1)
            return 'except', False

class UpsertReqBuildProc(InsertReqBuildProc):
    def gen_data(self, lms_cfg):
        url = f"{lms_cfg['HOST']}/v1/entities/upsert"
        req = self.builder.gen_insert_req(lms_cfg['store_name'], lms_cfg['collection_name'])
        return url, req

class SearchReqBuildProc(InsertReqBuildProc):
    def gen_data(self, lms_cfg):
        url = f"{lms_cfg['HOST']}/v1/entities/search"
        req = self.builder.gen_search_req(lms_cfg['store_name'], lms_cfg['collection_name'])
        return url, req

class QueryReqBuildProc(InsertReqBuildProc):
    def gen_data(self, lms_cfg):
        url = f"{lms_cfg['HOST']}/v1/entities/query"
        req = self.builder.gen_query_req(lms_cfg['store_name'], lms_cfg['collection_name'])
        return url, req

class InsertReqBuildProcReplaceInt(InsertReqBuildProc):
    @staticmethod
    def init_queue(start, end, group_num):
        group_queue = multiprocessing.Queue()
        gs = split_range(start, end, group_num)
        for idx, group in enumerate(gs):
            group_queue.put([idx, group])
        return group_queue

    def pre_start(self):
        super().pre_start()
        self.group_queue = self.user_data.get('data').get('group_queue')
        self.replace_field_name = self.user_data.get('data').get('replace_field_name', 'index')

    def gen_data(self, lms_cfg):
        url = f"{lms_cfg['HOST']}/v1/entities/insert"
        req = self.builder.gen_insert_req(lms_cfg['store_name'], lms_cfg['collection_name'])
        return url, req

    def step_run(self):
        lms_cfg = self.lms_cfg
        while True:
            try:
                group_idx, group = self.group_queue.get_nowait()
                break
            except queue.Empty:
                time.sleep(3)
                return 'norun', False
        self.info(f"start group_idx={group_idx}, {group}")
        try:
            start, end = group
            for idx in range(start, end):
                url, req = self.gen_data(lms_cfg)
                one_msg_entities_num = len(req['data'])
                for i in range(0, one_msg_entities_num):
                    req['data'][i][self.replace_field_name] = idx * one_msg_entities_num + i

                headers = {'Content-Type': 'application/json'}
                out_url, out_headers, out_body = sign(url, headers, json.dumps(req), lms_cfg['AK'], lms_cfg['SK'])
                self.put_data([out_url, out_headers, out_body])
            return 'success', False
        except:
            self.error(f'excet: {group_idx}, {group}, {traceback.format_exc()}')
            time.sleep(0.1)
            return 'except', False

class UpsertReqBuildProcReplaceInt(InsertReqBuildProcReplaceInt):
    def gen_data(self, lms_cfg):
        url = f"{lms_cfg['HOST']}/v1/entities/upsert"
        req = self.builder.gen_insert_req(lms_cfg['store_name'], lms_cfg['collection_name'])
        return url, req

class AioHttpSendProc(AioHttpRunProc):
    async def _req(self, session: aiohttp.ClientSession, req_data):
        try:
            rsp = await session.post(url=req_data[0], headers=req_data[1], data=req_data[2], timeout=self.parallel_cfg.aio_timeout, ssl=False)
            text = await rsp.text()
            if rsp.status != 200:
                self.error(f"rsp err: {rsp.status}, {text}")
                return 'fail'
            data = json.loads(text)
            if data['code'] != 'LMS.00000000':
                self.error(f"rsp err2: {rsp.status}, {data}")
                return 'fail'
            return 'success'
        except Exception as e:
            self.error(f'send excet: {traceback.format_exc()}')
            await asyncio.sleep(0.01)
            return 'except'
