
import os
import re
from typing import List

import hou

from houCacheCleaner.cache_version import CacheVersion
from houCacheCleaner.common import FILE_CACHE_NODE_TYPE_NAME


class Cache:
    """Object defining a cache and all its current versions"""

    def __init__(self, name: str = None, version_paths: List[str] = []):
        """
        :param version_paths: A list of all the versions of this cache
        :param versions: A list of all the versions of this cache
        """
        self.name = name
        self.versions = list()
        self.file_cache_node = None
        self.latest = None
        self.last_three = None
        self.safe_to_delete = None
        self.size_on_disk = 0.0

        self.set_versions(version_paths)
        self.nbr_of_versions = len(self.versions)
        self.set_file_cache_node()
        self.set_disk_size()
        self.set_latest()
        self.set_last_three()
        self.set_safe_to_delete()

    def get_name(self):
        return self.name

    def get_nbr_of_versions(self):
        return self.nbr_of_versions

    def set_versions(self, version_paths=None):
        """Update version list for this cache"""
        self.versions.clear()

        if version_paths is not None:
            for versions_path in version_paths:
                # We'll create a CacheVersion instance for each version
                self.versions.append(CacheVersion(versions_path))

        # Let's sort the versions by version number
        self.versions = sorted(
            self.versions, key=lambda cache_version: cache_version.version_nbr, reverse=True)

    def get_versions(self) -> list[CacheVersion]:
        return self.versions

    def set_file_cache_node(self):
        """This method will try to find a filecache node that corresponds to the current cache"""
        all_file_cache_nodes = hou.sopNodeTypeCategory().nodeType(FILE_CACHE_NODE_TYPE_NAME).instances()
        
        # TODO: compare outputpath or basefolder parms with cache path instead
        candidates = [n for n in all_file_cache_nodes if n.name() == self.name]

        # If no filecache is found, we'll set the attribute to None
        if len(candidates) == 0:
            self.file_cache_node = None

        # If we find only one, we'll set the attribute to this node
        elif len(candidates) == 1:
            self.file_cache_node = candidates[0]

        # If there's more than one corresponding node, we'll display a warning
        # and set the attribute to None
        else:
            self.file_cache_node = None
            text = f"Found {len(candidates)} nodes with name {self.name} at \n"
            for i in candidates:
                text += f"{i.path()}\n"

            title = "Found duplicate filecache nodes"

            hou.ui.displayConfirmation(
                text=text,
                severity=hou.severityType.Warning,
                title=title
            )

    def get_file_cache_node(self):
        """
        :rtype: hou.Node
        """
        return self.file_cache_node
    
    def set_disk_size(self) -> float:
        """Calculate total disk size for this cache"""
        total_size = sum([float(v.get_disk_size()) for v in self.versions])
        total_size = truncate(total_size, 2)
        self.size_on_disk = total_size

    def get_disk_size(self):
        return self.size_on_disk
    
    def set_latest(self):
        """Find the latest version for this cache"""
        versions = self.get_versions()
        if versions:
            latest = versions[0]
            latest.is_latest = True
            self.latest = latest
        else:
            self.latest = None

    def get_latest(self) -> CacheVersion:
        """Get the latest version for this cache"""
        return self.latest

    def set_last_three(self):
        """Find the last three versions for this cache"""
        last_three = [v for v in self.get_versions()[:3]]
        for v in last_three:
            v.isLastThree = True
        self.last_three = last_three

    def get_last_three(self) -> list[CacheVersion]:
        """Get the last three versions for this cache"""
        return self.last_three

    def set_safe_to_delete(self):
        """Find which versions can be safely deleted from disk"""
        versions = self.get_versions()
        # If we can't find a corresponding filecache node, we'll consider all versions as safe to delete
        if self.get_file_cache_node() is None:
            
            for v in versions:
                v.is_safe_to_delete = True

            self.safe_to_delete = versions

        # Check if other conditions are met so that we can safely delete the version
        else:
            self.safe_to_delete = []
            for v in versions:
                if v.get_is_latest() or v.get_is_last_three():
                    v.is_safe_to_delete = False
                
                else:
                    v.is_safe_to_delete = True
                    self.safe_to_delete.append(v)


    def get_safe_to_delete(self) -> list[CacheVersion]:
        """Get the versions that are safe to delete from disk"""
        return self.safe_to_delete
