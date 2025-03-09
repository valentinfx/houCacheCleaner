
import os
import re

import hou

from houCacheCleaner.common import VERSION_PATTERN, get_dir_size

class CacheVersion:
    """Objet definissant une version d'un cache"""

    def __init__(self, path: str = None):
        self.path = path
        self.name = ""
        self.files = []
        self.version_nbr = 0

        """Attributes is_latest, is_last_three and is_safe_to_delete are set by the parent Cache instance.
        For this reason we don't have setters here, only getters
        """
        self.is_latest = False
        self.is_last_three = False
        self.is_safe_to_delete = False

        self.set_files()

        self.nbr_of_files = len(self.files)

        self.set_version_nbr()

        self.start_frame = 0
        self.end_frame = 0
        self.frame_range = (self.start_frame, self.end_frame)

        self.size_on_disk = 0
        # self.set_size_on_disk() # WATCHME : Too slow :(
        self.set_name()

    def set_size_on_disk(self):
        """Set disk size attribute for this version"""
        self.size_on_disk = get_dir_size(self.path)

    def get_size_on_disk(self):
        return self.size_on_disk

    def set_files(self) -> list[str]:
        """Update files list for this version"""
        self.files.clear()

        for p in os.listdir(self.path):
            filePath = os.path.join(self.path, p)
            self.files.append(filePath)

    def get_files(self):
        return self.files

    def set_version_nbr(self):
        match = VERSION_PATTERN.match(os.path.basename(self.path))
        versionNbrStr = match.group('version')
        self.version_nbr = int(re.findall("\d+", versionNbrStr)[0])

    def get_version_nbr(self):
        return self.version_nbr

    def get_frame_range(self):
        return self.frame_range

    def set_name(self):
        match = VERSION_PATTERN.match(os.path.basename(self.path))
        name = match.group('name').replace('filecache', '')
        self.name = name

    def get_name(self):
        return self.name
    
    def get_is_latest(self):
        return self.is_latest

    def get_is_last_three(self):
        return self.is_last_three

    def get_is_safe_to_delete(self):
        return self.is_safe_to_delete
