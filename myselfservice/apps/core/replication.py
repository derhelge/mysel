class ReplicationRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tables = []
        return cls._instance
    
    def register_table(self, table_name):
        if table_name not in self._tables:
            self._tables.append(table_name)
    
    def get_tables(self):
        return self._tables

replication_registry = ReplicationRegistry()