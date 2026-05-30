#!/usr/bin/env python3
import shutil
from datetime import datetime
from pathlib import Path

# Constants
HOME = Path.home()
SOURCE = HOME / 'test_documents'
BACKUP_DIR = HOME / 'backups'

def create_backup(source, destination):
    """
    Copies the source folder to the destination folder.
    
    Args:
        source: Path to the folder to be backed up (Path object)
        destination: Path to the destination folder (Path object)
    
    Returns:
        bool: True if backup was created successfully, False otherwise
    """
    try:
        shutil.copytree(source, destination)
        print(f'✓ Backup completed: {destination}')
        return True
    except FileExistsError:
        print(f'✗ Destination folder already exists: {destination}')
        return False
    except Exception as e:
        print(f'✗ Error: {e}')
        return False

if __name__ == '__main__':
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_folder = BACKUP_DIR / f'backup_{timestamp}'
    create_backup(SOURCE, backup_folder)
