import os
import yaml
import random
import uuid
import string
import time
import datetime

try:
    import  numpy as np
    from sklearn import preprocessing
    from faker import Faker
    fake = Faker()
except:
    pass

def readYaml(path):
    with open(path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def gen_random_vector(dim):
    return preprocessing.normalize([np.array([random.random() for i in range(dim)])])[0].tolist()

callback_map = {}
def add_callback(key, func):
    global callback_map
    callback_map[key] = func

class OBJTYPE:
    value = 0
    list = 1
    obj = 2
    template_list = 3

class ObjTemplate:
    def __init__(self, obj) -> None:
        self.compiler = None
        self.obj = obj
    def _compile(self, obj):
        if type(obj) == type([]):
            rs = []
            for item in obj:
                rs.append(self._compile(item))
            return rs, OBJTYPE.list, 0
        elif type(obj) == type({}):
            rslt = {}
            for k,v in obj.items():
                if k == '__template_list_size':
                    continue
                rslt[k] = self._compile(v)
            if '__template_list_size' in obj:
                size = obj['__template_list_size']
                return rslt, OBJTYPE.template_list, size
            return rslt, OBJTYPE.obj, 0
        elif type(obj) == type(''):
            if obj.startswith('__template:'):
                func = eval('lambda :' + obj[11:])
                return func, 'func', 0
        return obj, OBJTYPE.value, 0
    def _reander(self, compile_rslt):
        # print('----', compile_rslt)
        value, t, size = compile_rslt[0], compile_rslt[1], compile_rslt[2]
        if t == OBJTYPE.value:
            return value
        elif t == 'func':
            return value()
        elif t == OBJTYPE.list:
            rslts = []
            for item in value:
                rslts.append(self._reander(item))
            return rslts
        elif t == OBJTYPE.obj:
            rslts = {}
            for k, v in value.items():
                rslts[k] = self._reander(v)
            return rslts
        elif t == OBJTYPE.template_list:
            rslts = []
            for _ in range(size):
                rslts.append(self._reander((value, OBJTYPE.obj, 0)))
            return rslts
        raise Exception('reander error')
        
    def render(self):
        if self.compiler == None:
            self.compiler = self._compile(self.obj)
        return self._reander(self.compiler)

def test():
    root = os.path.dirname(__file__)
    obj = readYaml(os.path.join(root, 'template.yaml'))
    print('====>', obj)
    r1 = ObjTemplate(obj['insert'])
    r2 = ObjTemplate(obj['collection'])
    print('====>', r1.render())
    print('====>', r2.render())

if __name__ == '__main__':
    test()
