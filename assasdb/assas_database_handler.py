import logging
 
from pymongo import MongoClient
from bson.objectid import ObjectId
from uuid import uuid4
from datetime import datetime

logger = logging.getLogger('assas_app')

class AssasDatabaseHandler:

    def __init__(self, connectionstring):
        
        self.client = MongoClient(connectionstring)

        self.db_handle = self.client['assas']
        self.file_collection = self.db_handle['files']

    def get_db_handle(self):

        return self.db_handle

    def get_file_collection(self):
        
        return self.file_collection
    
    def insert_file_document(self, file):
        
        logger.info('insert %s' % file)
        
        self.file_collection.insert_one(file)

    def drop_file_collection(self):

        self.file_collection.drop()
        
    def get_file_document(self, id):
        
        return self.file_collection.find_one(ObjectId(id))
    
    def get_file_document_uuid(self, uuid):
        
        return self.file_collection.find_one({'system_uuid':str(uuid)})
    
    def delete_file_document(self, id):
        
        return self.file_collection.delete_one({'_id': ObjectId(id)})
    
    def delete_file_document_uuid(self, uuid):
        
        return self.file_collection.delete_one({'system_uuid':str(uuid)})

class AssasDocumentFileStatus:
    UPLOADED = 'Uploaded'
    CONVERTED = 'Converted'
    ARCHIVED = 'Archived'
    FAILED = 'Failed'

class AssasDocumentFile:
    
    def __init__(self) -> None:
        self.document = {}
        
    def get_document(self) -> dict:
        
        return self.document
    
    def set_document(self, document) -> None:
        
        self.document = document
        
    def extend_document(self, add_document) -> None:
        
        temp = self.document.copy()
        temp.update(add_document)
        
        self.document = temp
        
    def set_meta_values(
        self,
        meta_name: str,
        meta_group: str,
        meta_date: str,
        meta_creator: str,
        meta_description: str,

        ) -> None:
        
        self.document['meta_name'] = meta_name
        self.document['meta_group'] = meta_group
        self.document['meta_date'] = meta_date
        self.document['meta_creator'] = meta_creator
        self.document['meta_description'] = meta_description
        
    def set_data_values(
        self,
        ) -> None:
        
        self.document['meta_data_variables'] = "['pressure', 'voidf', 'temp', 'sat_temp']"
        self.document['meta_data_channels'] = '4'
        self.document['meta_data_meshes'] = '16'
        self.document['meta_data_samples'] = '1000'   
        
    def set_value(self, key: str, value: str) -> None:
        
        self.document[key] = value
        
    def get_value(self, key: str) -> None:
        
        return self.document[key]
        
    def delete_key(self, key: str) -> bool:
        
        is_in = False
        if key in self.document:
            is_in = True
            del self.document[key]

        return is_in
        
    def set_system_values(
        self,
        system_uuid: str,
        system_date: str,
        system_path: str,
        system_size: str,
        system_user: str,
        system_download: str,
        system_status: str,

        ) -> None:
        
        self.document['system_uuid'] = system_uuid
        self.document['system_date'] = system_date
        self.document['system_path'] = system_path
        self.document['system_size'] = system_size
        self.document['system_user'] = system_user
        self.document['system_download'] = system_download
        self.document['system_status'] = system_status

    @staticmethod
    def get_test_document_file(
        system_uuid=str(uuid4()),
        system_path='default_path'
        ) -> dict:
 
        document = {
                    "system_uuid": system_uuid,
                    "system_date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    "system_path": system_path,
                    "system_size": "8.4 MB",
                    "system_user": "test user",
                    "system_download": "Download",
                    "system_status": "complete",
                    "meta_name": "Name of Simulation X",
                    "meta_group": "Group or Kind of Simulation",
                    "meta_date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    "meta_creator": "Test User",
                    "meta_description": "'this is a test description!'",
                    "meta_data_variables": "['pressure', 'voidf', 'temp', 'sat_temp']",
                    "meta_data_channels": "4",
                    "meta_data_meshes": "16",
                    "meta_data_samples": "1000"
                }
        
        return document  