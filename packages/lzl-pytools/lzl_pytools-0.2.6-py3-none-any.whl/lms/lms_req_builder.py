from lzl_pytools.obj_template import ObjTemplate, readYaml

class LmsReqBuilder:
    def __init__(self, filepath) -> None:
        self.obj = readYaml(filepath)
        self.collection = ObjTemplate(self.obj.get('collection', {}))
        self.insert = ObjTemplate(self.obj.get('insert', {}))
        self.search = ObjTemplate(self.obj.get('search', {}))
        self.query = ObjTemplate(self.obj.get('query', {}))
        self.index = ObjTemplate(self.obj.get('index', {}))
        self.entity_delete = ObjTemplate(self.obj.get('entity_delete', {}))
    
    def _update_names(self, data, store_name=None, collection_name=None):
        if store_name:
            data['store_name'] = store_name
        if collection_name:
            data['collection_name'] = collection_name
        return data

    def gen_collection_req(self, store_name=None, collection_name=None):
        return self._update_names(self.collection.render(), store_name, collection_name)

    def gen_insert_req(self, store_name=None, collection_name=None):
        return self._update_names(self.insert.render(), store_name, collection_name)

    def gen_search_req(self, store_name=None, collection_name=None):
        return self._update_names(self.search.render(), store_name, collection_name)

    def gen_query_req(self, store_name=None, collection_name=None):
        return self._update_names(self.query.render(), store_name, collection_name)

    def gen_index_req(self, store_name=None, collection_name=None):
        return self._update_names(self.index.render(), store_name, collection_name)

    def gen_entity_delete_req(self, store_name=None, collection_name=None):
        return self._update_names(self.entity_delete.render(), store_name, collection_name)
