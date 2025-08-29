from ..api.client import APIClient
from ..api.modules import *
from .forms_res import FormsRes

class FormsQuery():
    """
    An utility class to query the forms dataset.
    """
    
    def __init__(self, client: APIClient) -> None:        
        self.limit = 10
        self.offset = 0
        self.extMode = False
        self.client = client
        self.query_fields = []
        self.module_name = FORMS_MODULE_NAME
        self.ref = None
        self.root = None
        self.call_args = []
        self.func = None
        self.extra = None
                
    def with_root(self, root: str):
        self._add_query_field({
            "field": "root",
            "value": root,
            "onMeta": True
        })
        return self
        
    def with_id(self, id: str):
        self._add_query_field({
            "field": "id",
            "value": id,
            "onMeta": True
        })
        return self
        
    def with_func(self, func: str):
        self.func = func
        return self
    
    def where(self, field: str, value: str, op = "="):
        self._add_query_field({
            "field": field,
            "value": value,
            "op": op
        })
        return self
    
    def with_sub_forms(self, value: bool = True):
        self.extMode = value
        return self
        
    def with_limit(self, limit: int):
        self.limit = limit
        return self
    
    def with_offset(self, offset: int):
        self.offset = offset
        return self    
    
    def with_ref(self, ref: str):
        self.ref = ref
        return self      
    
    def with_extra(self, extra: dict):
        self.extra = extra
        return self
    
    def with_module_name(self, module_name: str):
        self.module_name = module_name
        return self    
    
    def with_args(self, args):
        self.call_args = args
        return self
    
    def _add_query_field(self, qf):
        self.query_fields.append(qf)
        return self
    
    def _create_raw_query(self):
        raw_query ={
                    "extMode": self.extMode,
                    "limit": self.limit,
                    "offset": self.offset,
                    "queryFields": self.query_fields,
                    "ref": self.ref                    
                }  
        return (raw_query | self.extra) if self.extra is not None else raw_query

    def call(self):
        params = self.call_args + [ self._create_raw_query() ]
        if self.func is None:                
            return FormsRes(self.client.call_forms_query(params, self.module_name))        
        else:
            return FormsRes(self.client.call_module(func=self.func, params=params, module_name=self.module_name))

    def call_single(self, id: str):
        return self.client.call_form_query(
            id, self._create_raw_query(), self.module_name)
    
    def __str__(self) -> str:   
        return f'{self.module_name}\n{str(self._create_raw_query())}\n{str(self.call_args)}'
    
    