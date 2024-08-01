import os
import smbclient
import logging
import shutil
import errno
import pathlib

from typing import List, Tuple, Union
from shutil import copytree, copy2, rmtree

logger = logging.getLogger('assas_app')

class AssasStorageHandler:
    
    def __init__(
        self,
        config: dict
    )-> None:
        
        self.local_archive = config.LOCAL_ARCHIVE
        self.lsdf_archive = config.LSDF_ARCHIVE
        
        self.create_local_archive()
        self.create_lsdf_archive()
    
    @staticmethod
    def get_size_of_archive_in_bytes(
        directory: str
    )-> int:
        
        size_list = []
        for name in os.listdir(directory):
            if os.path.isfile(name):
                size = os.path.getsize(name)
                size_list.append(os.path.getsize(name))
                logger.debug(f'Size of {name} is {size}')
        
        return sum(size_list)
    
    @staticmethod
    def create_lsdf_archive_path(
            lsdf_dest_path,
            lsdf_sub_dir,
            sample: int,
    ) -> Union[pathlib.Path, str]:
            
            lsdf_archive_path = f'{lsdf_dest_path}/sample_{str(sample)}{lsdf_sub_dir}'
            lsdf_archive_path = pathlib.Path(lsdf_archive_path)      
            
            return lsdf_archive_path
    
    @staticmethod    
    def copy2_verbose(
        src: str,
        dst: str
    )-> None:
        
        logger.debug(f'Copying {src}')
        copy2(src, dst)
        
    def store_archive_on_share(
        self,
        system_uuid: str
    ) -> bool:
        
        logger.info(f'copy archive to share (uuid: {system_uuid})')
        
        try:
            copytree(self.local_archive + system_uuid, self.lsdf_archive + system_uuid, copy_function=AssasStorageHandler.copy2_verbose)
        except:    
            logger.warning(f'exception during copy process occured')
            return False                   
        
        logger.info(f'copied archive to share {system_uuid}')
        
        return True
        
    def delete_local_archive(
        self, 
        system_uuid: str
    ) -> bool:
        
        logger.info(f'delete local archive (uuid: {system_uuid})')
        
        try:
            rmtree(self.local_archive + system_uuid)
        except:    
            logger.warning(f'exception during delete process occured')
            return False
            
        logger.info('deleted local archive')
        
        return True
        
    def create_lsdf_archive(
        self
    ) -> None:

        logger.info(f'create lsdf archive {self.lsdf_archive}')
        
        if not os.path.isdir(self.lsdf_archive):
            os.makedirs(self.lsdf_archive)
        else:
            logger.warning('lsdf archive already exists')
            
    def create_local_archive(
        self
    ) -> None:

        logger.info(f'create local archive {self.local_archive}')
        
        if not os.path.isdir(self.local_archive):
            os.makedirs(self.local_archive)
        else:
            logger.warning(f'local archive already exists {self.local_archive}')
            
    def create_dataset_archive(
        self,
        path: str
    )-> None:
        
        logger.info(f'create dataset archive {path}')
        
        if not os.path.isdir(path):
            os.makedirs(path)
        else:
            logger.warning(f'dataset archive already exists {path}')
            
    def get_local_archive_dir(
        self
    )-> str:
        
        return self.local_archive
    
    def get_lsdf_archive_dir(
        self
    )-> str:
        
        return self.lsdf_archive
    
    def get_dataset_archive_dir(
        self,
        uuid: str
    )-> str:
        
        return self.get_lsdf_archive_dir() + uuid
    
