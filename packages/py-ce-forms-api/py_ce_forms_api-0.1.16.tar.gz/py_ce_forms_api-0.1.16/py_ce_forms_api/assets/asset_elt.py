class AssetElt():
    """
    Utility class to manage forms asset element
    """
    def __init__(self, data: (bytes|None), block_value) -> None:
        self.data = data
        self.block_value = block_value
    
    def has_data(self) -> bool:
        return self.data is not None
    
    def id(self) -> str:
        return self.block_value["id"]
    
    def mimetype(self) -> str:
        return self.block_value["mimetype"]
    
    def name(self) -> str:
        return self.block_value["name"]
    
    def original_name(self) -> str:
        return self.block_value["originalname"]
    
    def ref(self) -> str:
        return self.block_value["ref"]
    
    def get_bytes(self) -> bytes:
        return self.data
    
    def get_value(self):
        return self.block_value
    