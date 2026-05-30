#!/usr/bin/env python3
import tarfile
import logging
from datetime import datetime
from pathlib import Path

# Constants
HOME = Path.home()
SOURCE = HOME / 'test_documents'
BACKUP_DIR = HOME / 'backups'

logging.basicConfig(
    filename=BACKUP_DIR / 'backup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_compressed_backup(source, destination_file):
    """
    Creates a compressed tar.gz backup of the source folder.
    
    Args:
        source: Path to the folder to be backed up (Path object).
        destination_file: Full path to the .tar.gz file (Path object)
        
    Returns:
        bool: True if backup was created sucessfully, FAlse otherwise
    """
    try:
        with tarfile.open(destination_file, 'w:gz') as tar:
            tar.add(source, arcname=source.name)
        logging.info(f'Backup created: {destination_file}')
        print(f'Compressed backup created: {destination_file}')
        return True
    except Exception as e:
        logging.error(f'Error creating backup: {e}')
        print(f'Error creating backup: {e}')
        return False
    

if __name__ == '__main__':
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_file = BACKUP_DIR / f'backup_{timestamp}.tar.gz'
    create_compressed_backup(SOURCE, backup_file)
