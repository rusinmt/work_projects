import os
import paramiko
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import posixpath
from dataclasses import dataclass
import pytz

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SFTPConfig:
    """Configuration for SFTP connection and sync settings."""
    username: str
    password: str
    hours_back: int
    description: str
    synology_subpath: str
    schedule: str

class SynologyUploader:
    def __init__(self, upload_url: str, base_upload_path: str):
        self.upload_url = upload_url
        self.base_upload_path = base_upload_path

    def upload_file(self, file_content: bytes, filename: str, user_config: SFTPConfig, relative_path: str = '') -> bool:
        try:
            upload_path = posixpath.join(
                self.base_upload_path,
                user_config.synology_subpath,
                relative_path
            )

            files = {'file': (filename, file_content)}
            data = {
                'path': upload_path,
                'filename': filename
            }

            response = requests.post(self.upload_url, files=files, data=data)
            response.raise_for_status()

            logger.info(f"Successfully uploaded {filename} to Synology at {upload_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to upload {filename} to Synology: {e}")
            return False

class SFTPSync:
    def __init__(self, hostname: str, config: SFTPConfig, port: int):
        self.hostname = hostname
        self.config = config
        self.port = port
        self.sftp = None
        self.ssh = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self) -> bool:
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            self.ssh.connect(
                hostname=self.hostname,
                username=self.config.username,
                password=self.config.password,
                port=self.port
            )

            self.sftp = self.ssh.open_sftp()
            logger.info(f"Successfully connected to {self.hostname}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to {self.hostname}: {e}")
            return False

    def close(self):
        if self.sftp:
            self.sftp.close()
        if self.ssh:
            self.ssh.close()
        logger.info("Connections closed")

    def check_permissions(self, path: str) -> bool:
        try:
            self.sftp.stat(path)
            logger.info(f"Basic access to {path} confirmed")

            contents = self.sftp.listdir(path)
            logger.info(f"Successfully listed {len(contents)} items in {path}")
            return True

        except Exception as e:
            logger.error(f"Permission error on {path}: {e}")
            return False

    def get_recent_files(self, sftp_base_path: str) -> List[Dict]:
        current_time = datetime.now(pytz.utc)
        interval_start = current_time - timedelta(hours=self.config.hours_back)
        recent_files = []
    
        try:
            def walk_directory(current_path: str):
                try:
                    for entry in self.sftp.listdir_attr(current_path):
                        full_path = posixpath.join(current_path, entry.filename)
                        try:
                            if self.is_directory(entry):
                                walk_directory(full_path)
                            else:
                                try:
                                    file_time = datetime.fromtimestamp(entry.st_ctime, pytz.utc)
                                    time_type = "created"
                                except AttributeError:
                                    file_time = datetime.fromtimestamp(entry.st_mtime, pytz.utc)
                                    time_type = "modified"
    
                                if interval_start <= file_time <= current_time:
                                    file_info = {
                                        'name': entry.filename,
                                        'full_path': full_path,
                                        'modified_time': file_time,
                                        'size': entry.st_size,
                                        'relative_path': posixpath.relpath(full_path, sftp_base_path),
                                        'is_directory': self.is_directory(entry),
                                        'username': self.config.username
                                    }
                                    recent_files.append(file_info)
                                    logger.info(
                                        f"Found recent file (based on {time_type} time): {entry.filename} ({file_time}) for user {self.config.username}"
                                    )
    
                        except Exception as entry_error:
                            logger.error(f"Error processing entry {full_path}: {entry_error}")
    
                except Exception as e:
                    logger.error(f"Error accessing directory {current_path}: {e}")
    
            walk_directory(sftp_base_path)
            return recent_files
    
        except Exception as e:
            logger.error(f"Error finding recent files: {e}")
            return []

    def download_and_upload(self, file_list: List[Dict], synology_uploader: SynologyUploader) -> List[str]:
        uploaded_files = []

        for file_info in file_list:
            try:
                if file_info['is_directory']:
                    continue

                with self.sftp.file(file_info['full_path'], 'rb') as remote_file:
                    file_content = remote_file.read()

                relative_path = os.path.dirname(file_info['relative_path'])
                if synology_uploader.upload_file(
                        file_content=file_content,
                        filename=file_info['name'],
                        user_config=self.config,
                        relative_path=relative_path
                ):
                    uploaded_files.append(file_info['full_path'])

            except Exception as e:
                logger.error(f"Error processing {file_info['name']}: {e}")

        return uploaded_files

    def is_directory(self, entry):
        return entry.st_mode & 0o40000 == 0o40000

def sync_multiple_accounts(
        hostname: str,
        sftp_configs: Dict[str, SFTPConfig],
        sftp_base_path: str,
        synology_upload_url: str,
        synology_upload_path: str,
        port: int
) -> Dict[str, List[str]]:
    results = {}
    synology_uploader = SynologyUploader(synology_upload_url, synology_upload_path)

    utc_now = datetime.now(pytz.utc)
    
    for username, config in sftp_configs.items():
        if config.schedule == 'skipt' or (config.schedule == 'med' and utc_now.hour == 15):
            logger.info(f"Starting sync for user {username} ({config.description})")
            logger.info(f"Looking for files modified in the last {config.hours_back} hours")

            with SFTPSync(hostname, config, port) as sftp_sync:
                if not sftp_sync.check_permissions(sftp_base_path):
                    logger.error(f"Permission check failed for user {username}")
                    results[username] = []
                    continue

                recent_files = sftp_sync.get_recent_files(sftp_base_path)
                if not recent_files:
                    logger.info(f"No recent files found for user {username}")
                    results[username] = []
                    continue

                uploaded_files = sftp_sync.download_and_upload(recent_files, synology_uploader)
                results[username] = uploaded_files
                logger.info(f"Completed sync for user {username}: {len(uploaded_files)} files uploaded")

    return results

if __name__ == '__main__':
    sftp_configs = {
        'user1': SFTPConfig(
            username = 'user1',
            password = pass1,
            hours_back = 1,
            description = 'user1',
            synology_subpath = 'user1',
            schedule = "skipt"
        ),
        'user2': SFTPConfig(
            username = 'user2',
            password = pass2,
            hours_back =24,
            description = 'user2',
            synology_subpath = 'user2',
            schedule = "med"
        )
    }

    config = {
        'hostname': '195.11.1',
        'sftp_configs': sftp_configs,
        'sftp_base_path': '/IN',
        'synology_upload_url':'http://192.11.1:5000/api/synology/upload/file',
        'synology_upload_path': '/drive/SFTP_mirror',
        'port': 22
    }

    results = sync_multiple_accounts(**config)
    for username, uploaded_files in results.items():
        if uploaded_files:
            logger.info(f"User {username}: Successfully uploaded {len(uploaded_files)} files")
        else:
            logger.warning(f"User {username}: No files were uploaded")
