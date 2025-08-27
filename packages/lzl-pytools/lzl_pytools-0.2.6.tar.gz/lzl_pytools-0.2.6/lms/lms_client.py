import logging
import json
import requests
import urllib3
import traceback
from lzl_pytools.apig_sdk import signer

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger()

def sign(url, headers, body, AK='', SK='', method='POST'):
    if AK is None or AK == '':
        return url, headers, body
    sig = signer.Signer()
    sig.Key = AK
    sig.Secret = SK
    req = signer.HttpRequest(method, url)
    req.headers = headers
    req.body = body
    sig.Sign(req)
    out_url = req.scheme + '://' + req.host + req.uri
    return out_url, req.headers, req.body

class LmsHttpPath:
    STORES_LIST = '/v1/stores/list'
    STORES_CREATE = '/v1/stores/create'
    STORES_DELETE = '/v1/stores/delete'

    COLLECTIONS_LIST = '/v1/collections/list'
    COLLECTIONS_CREATE = '/v1/collections/create'
    COLLECTIONS_DESCRIBE = '/v1/collections/describe'
    COLLECTIONS_DELETE = '/v1/collections/delete'
    COLLECTIONS_LOAD = '/v1/collections/load'
    COLLECTIONS_RELEASE = '/v1/collections/release'

    ENTITIES_INSERT = '/v1/entities/insert'
    ENTITIES_DELETE = '/v1/entities/delete'
    ENTITIES_QUERY = '/v1/entities/query'
    ENTITIES_SEARCH = '/v1/entities/search'
    ENTITIES_UPSERT = '/v1/entities/upsert'
    ENTITIES_HYBRID_SEARCH = '/v1/entities/hybrid-search'

    INDEXES_CREATE = '/v1/indexes/create'
    INDEXES_DELETE = '/v1/indexes/delete'
    INDEXES_DESCRIBE = '/v1/indexes/describe'
    INDEXES_GET_PROGRESS = '/v1/indexes/get-progress'

class LmsClient:
    def __init__(self, host, AK='', SK='', timeout=300, cert=None, log_error=True) -> None:
        self.host = host.rstrip('/')
        self.AK = AK
        self.SK = SK
        self.cert = cert
        self.timeout = timeout
        self.log_error = log_error
        self.session = requests.session()
    
    def post(self, url, data, headers=None):
        url = self.host + url
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        else:
            headers['Content-Type'] = 'application/json'
        body = json.dumps(data)
        url, headers, body = sign(url, headers, body, self.AK, self.SK, method='POST')
        logger.info(f"---->> {url}, {body}, {headers}")
        if self.cert is None or self.cert == '':
            rsp = self.session.post(url, headers=headers, data=body, timeout=self.timeout, verify=False)
        else:
            rsp = self.session.post(url, headers=headers, data=body, timeout=self.timeout, cert=self.cert)
        logger.info(f"<<---- {rsp.status_code}, {rsp.text}, {rsp.headers}")
        if self.log_error and rsp.status_code >= 400:
            logger.warning(f"---->> {url}, {body}, {headers}")
            logger.warning(f"<<---- {rsp.status_code}, {rsp.text}, {rsp.headers}")
            raise Exception(f"post error: {rsp.status_code}, {rsp.text}, {rsp.headers}")
        data = json.loads(rsp.text)
        if self.log_error and data['code'] != 'LMS.00000000':
            logger.warning(f"---->> {url}, {body}, {headers}")
            logger.warning(f"<<---- {rsp.status_code}, {rsp.text}, {rsp.headers}")
            raise Exception(f"post code error: {rsp.status_code}, {rsp.text}, {rsp.headers}")
        return data

    def stores_list(self):
        rsp = self.post(LmsHttpPath.STORES_LIST, {})
        return rsp['data']['stores']

    def list_stores_names(self):
        stores = self.stores_list()
        if len(stores) == 0:
            return []
        store_names = []
        for s in stores:
            if type(s) == str:
                store_names.append(s)
            else:
                store_names.append(s['store_name'])
        return store_names

    def stores_create(self, store_name):
        data = {'store_name': store_name}
        return self.post(LmsHttpPath.STORES_CREATE, data)

    def stores_delete(self, store_name):
        data = {'store_name': store_name}
        return self.post(LmsHttpPath.STORES_DELETE, data)

    def collections_list(self, store_name):
        data = {'store_name': store_name}
        rsp = self.post(LmsHttpPath.COLLECTIONS_LIST, data)
        return rsp['data']['collections']

    def collections_create(self, data):
        return self.post(LmsHttpPath.COLLECTIONS_CREATE, data)

    def collections_describe(self, store_name, collection_name):
        data = {'store_name': store_name, 'collection_name': collection_name}
        return self.post(LmsHttpPath.COLLECTIONS_DESCRIBE, data)

    def collections_delete(self, store_name, collection_name):
        data = {'store_name': store_name, 'collection_name': collection_name}
        return self.post(LmsHttpPath.COLLECTIONS_DELETE, data)

    def collections_load(self, store_name, collection_name):
        data = {'store_name': store_name, 'collection_name': collection_name}
        return self.post(LmsHttpPath.COLLECTIONS_LOAD, data)

    def collections_release(self, store_name, collection_name):
        data = {'store_name': store_name, 'collection_name': collection_name}
        return self.post(LmsHttpPath.COLLECTIONS_RELEASE, data)

    def entities_insert(self, data):
        return self.post(LmsHttpPath.ENTITIES_INSERT, data)

    def entities_delete(self, data):
        return self.post(LmsHttpPath.ENTITIES_DELETE, data)

    def entities_query(self, data):
        return self.post(LmsHttpPath.ENTITIES_QUERY, data)

    def entities_search(self, data):
        return self.post(LmsHttpPath.ENTITIES_SEARCH, data)

    def entities_upsert(self, data):
        return self.post(LmsHttpPath.ENTITIES_UPSERT, data)

    def entities_hybrid_search(self, data):
        return self.post(LmsHttpPath.ENTITIES_HYBRID_SEARCH, data)

    def indexes_create(self, data):
        return self.post(LmsHttpPath.INDEXES_CREATE, data)

    def indexes_delete(self, store_name, collection_name, index_name, field_name):
        data = {'store_name': store_name, 'collection_name': collection_name, 
                'index_name': index_name, 'field_name': field_name}
        return self.post(LmsHttpPath.INDEXES_DELETE, data)

    def indexes_describe(self, store_name, collection_name, index_name, field_name):
        data = {'store_name': store_name, 'collection_name': collection_name, 
                'index_name': index_name, 'field_name': field_name}
        return self.post(LmsHttpPath.INDEXES_DESCRIBE, data)

    def indexes_get_progress(self, store_name, collection_name, index_name, field_name):
        data = {'store_name': store_name, 'collection_name': collection_name, 
                'index_name': index_name, 'field_name': field_name}
        return self.post(LmsHttpPath.INDEXES_GET_PROGRESS, data)

    def release_all_collection(self, store_name):
        collections = self.collections_list(store_name)
        collections.sort()
        for c in collections:
            rsp = self.collections_release(store_name, c)
            logger.warning(f"==> release: {c}, {rsp}")

    def load_all_collection(self, store_name):
        collections = self.collections_list(store_name)
        collections.sort()
        for c in collections:
            rsp = self.collections_load(store_name, c)
            logger.warning(f"==> load: {c}, {rsp}")

    def delete_all_collection(self, store_name):
        collections = self.collections_list(store_name)
        collections.sort()
        for c in collections:
            rsp = self.collections_delete(store_name, c)
            logger.warning(f"==> delete collection: {c}, {rsp}")
    
    def delete_all_stores(self):
        stores = self.list_stores_names()
        for s in stores:
            self.delete_all_collection(s)
            if s == 'default':
                continue
            rsp = self.stores_delete(s)
            logger.warning(f"==> delete store: {s}, {rsp}")
    
    def simple_describe_all_collection(self, store_name):
        collections = self.collections_list(store_name)
        collections.sort()
        datas = []
        for c in collections:
            try:
                rsp = self.collections_describe(store_name, c)
                datas.append([c, rsp['data']['entity_num'], rsp['data']['load_state']])
            except Exception as e:
                logger.error(f"describe error: {store_name}, {c}, {traceback.format_exc()}")
        for d in datas:
            print('==>', d)
    
    def print_collection_describe(self, store_name, collection_name):
        rsp = self.collections_describe(store_name, collection_name)
        for k,v in rsp['data'].items():
            if k in ['fields', 'indexes']:
                print(f'{k}:')
                for d in v:
                    print(f'  {d}')
            else:
                print(f'{k}: {v}')
        print('end')
        

