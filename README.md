# Backup Script

A Python-based automated backup tool that creates compressed archives of specified directories with professional logging.

## Features

- Recursive folder backup with `tar.gz` compression
- Professional logging to file (`~/backups/backup.log`)
- Unique timestamped backups to avoid overwrites
- Error handling with clear terminal feedback

## Technologies

- Python 3
- `tarfile` (standard library)
- `logging` (standard library)
- `pathlib` (standard library)
- Linux-native `.tar.gz` format

## How to Use

```bash
# Clone the repository
git clone https://github.com/leonardo/backup-script.git
cd backup-script

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Run the script
python3 backup.py
