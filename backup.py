#!/usr/bin/env python3
import tarfile
import logging
import hashlib
import json
import time
from notify import send_webhook, send_rich_notification
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

def calculate_hash(file_path):
    """
    Calculates the SHA256 hash of a file.
    Reads the file in 8 KB chuncks to avoid memory issus with large files.
    
    Args:
        file_path: Path to the file (Path object)
        
    Returns:
        str: 64-character hexadecimal hash, or None if error
    """

    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(8192) # Read 8 KB at time
                if not chunk:        # End of file
                    break
                hasher.update(chunk)
            return hasher.hexdigest()
    except Exception as e:
            logging.error(f'Error calculating hash for {file_path}: {e}')
            return None

def generate_manifest(folder):
    """
    
    Recursively walks through a folder and generates a dictionary
    mapping each file's relative path to its SHA256 hash.
    
    Args:
        folder: Path to the folder to analyze (Path object)
        
    Returns:
        dict: {'relative/path.txt': 'sha256_hash', ...}
    """

    manifest={}
    for file_path in folder.rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(folder)
            file_hash = calculate_hash(file_path)
            if file_hash:
                manifest[str(relative_path)] = file_hash
                logging.info(f'Hash calculated: {relative_path} -> {file_hash[:16]}...')
            else:
                logging.warning(f'Could not calculate hash for: {relative_path}')
    return manifest


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
    # Ensure backup directory exists
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Start timer
    start_time = time.time()

    # Generate unique timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Step 1: Generate manifest BEFORE backup
    print('Calculating file hashes...')
    manifest = generate_manifest(SOURCE)
    manifest_path = BACKUP_DIR / f'manifest_{timestamp}.json'

    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    logging.info(f'Manifest saved: {manifest_path}')
    print(f'Manifest saved: {manifest_path}')
    print(f'Files processed: {len(manifest)}')

    # Step 2: Create compressed backup
    print('Creating compressed backup...')
    backup_file = BACKUP_DIR / f'backup_{timestamp}.tar.gz'
    success = create_compressed_backup(SOURCE, backup_file)

    # Step 3: Calculate duration
    duration = time.time() - start_time


    # Step 4: Generate summary report
    if success:
        size_bytes = backup_file.stat().st_size
        if size_bytes < 1024 * 1024:  # Less than 1 MB
                size_display = f'{size_bytes / 1024:.2f} KB'
        else:
                size_display = f'{size_bytes / (1024 * 1024):.2f} MB'

        # Terminal output
        print(f'\n Backup completed sucessfully!')
        print(f'Archive: {backup_file.name}')
        print(f'   Size: {size_display}')
        print(f'   Files: {len(manifest)}')
        print(f'   Duration: {duration:.4f} seconds')
        print(f'Manifest: {manifest_path.name}')

        # Save JSON summary report
        report= {
            'status': 'success',
            'timestamp': timestamp,
            'source': str(SOURCE),
            'archive': str(backup_file.name),
            'size': size_display,
            'size_bytes': size_bytes,
            'files_count': len(manifest),
            'duration_seconds': round(duration, 4),
            'manifest': str(manifest_path.name)
        }
        
        report_path = BACKUP_DIR / f'report_{timestamp}.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        logging.info(f'Report sabed: {report_path}')

        # Send rich notification to Discord
        send_rich_notification(
            title='✅ Backup Completed Successfully',
            fields={
                'Archive': backup_file.name,
                'Size': size_display,
                'Files': len(manifest),
                'Duration': f'{duration:.4f}s'
            },
            color=65280
        )
    else:
        # Terminal output
        print(f'\n Backup failed. Check log: {BACKUP_DIR / "backup.log"}')

        # Save failure report
        report = {
            'status': 'failure',
            'timestamp': timestamp,
            'source': str(SOURCE),
            'duration_seconds': round(duration, 2),
            'error': 'See backup.log for details'
        }
        report_path = BACKUP_DIR / f'report_{timestamp}.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Send failure notification
        send_rich_notification(
            title='Backup failed',
            fields={
                'Source': str(SOURCE),
                'Timestamp': timestamp,
                'Duration': f'{duration:.2f}s'
            },
            color=16711680 # Red
        )