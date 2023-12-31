import os
import smbclient
import logging

logger = logging.getLogger(__name__)

class AssasStorageHandler:
    
    def __init__(self, mount_point="/mnt/ASSAS/", archive_dir="/test/", tmp_dir="./tmp/"):
        
        self.mount_point = mount_point
        self.archive_dir = archive_dir
        self.tmp_dir = tmp_dir

        self.path = self.mount_point + self.archive_dir
        
        self.user = 'ke4920'
        self.password = 'R.adio_!1234'
        self.server = 'os.lsdf.kit.edu'
        self.share = 'kit\scc\projects\ASSAS'
        
        self.smbclient_config = self.client_config()
        self.session = self.register_session()
        
    def create_lsdf_archive(self):

        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        else:
            logger.warning("lsdf archive already exists")
            
    def create_dataset_archive(self, path):
        
        if not os.path.isdir(path):
            os.mkdir(path)
        else:
            logger.warning("dataset archive already exists")
            
    def get_path(self):
        
        return self.path
    
    def register_session(self):
        
        try:
            session = smbclient.register_session(self.server, username=self.user, password=self.password)
            logger.info("successfully connected to share")
        except:
            session = None
            logger.error("unable to connect to share")
            
        return session
        
    def client_config(self):
        
        return smbclient.ClientConfig(username=self.user, password=self.password)
    
    @staticmethod
    def reset_connection_cache():
        
        return smbclient.reset_connection_cache()
