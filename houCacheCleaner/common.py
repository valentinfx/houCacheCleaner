import os
import re
import hou
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import stat

from houCacheCleaner.cache import Cache

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] : %(message)s")
log = logging.getLogger(__name__)

FILE_CACHE_NODE_TYPE_NAME = "filecache" # WATCHME: handle HDA version 
CACHES_ROOT = "$HIP/geo"
VERSION_PATTERN = re.compile(
    r"(?P<name>\S+)(?P<version>_v\d{3})(?P<tail>\.bgeo\.sc)")
BGEO_FILE_PATTERN = re.compile(
    r"(?P<name>\S+)(?P<version>_v\d{3})(?P<frameNumber>\.\d{4})(?P<filetype>\.bgeo\.sc)")


"""TODO
- Define self.isLatest
- Defini self.isLastThree
- Defin self.isSafeToDelete
"""

# =====================


def get_dir_size_fast(path) -> float:
    """Calculate directory size using multiple optimizations:
    - Uses scandir instead of listdir for better performance
    - Minimizes stat calls by using DirEntry object properties
    - Uses threading for parallel processing of subdirectories
    - Uses pathlib for more efficient path handling
    - Maintains running total instead of recursive sum
    
    Args:
        path: String path to directory
    Returns:
        Float size in gigabytes
    """
    def scan_directory(path):
        total = 0
        subdirs = []
        
        # Use scandir instead of listdir for better performance
        with os.scandir(path) as scanner:
            for entry in scanner:
                try:
                    # Get entry's stat info without additional system calls
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False):
                        subdirs.append(entry.path)
                except (PermissionError, FileNotFoundError):
                    continue
                    
        return total, subdirs

    def process_directory(path):
        total = 0
        dirs_to_scan = [path]
        
        while dirs_to_scan:
            current_dirs = dirs_to_scan[:100]  # Process in batches
            dirs_to_scan = dirs_to_scan[100:]
            
            # Use ThreadPoolExecutor for parallel directory scanning
            with ThreadPoolExecutor(max_workers=min(len(current_dirs), 20)) as executor:
                results = executor.map(scan_directory, current_dirs)
                
                for size, new_subdirs in results:
                    total += size
                    dirs_to_scan.extend(new_subdirs)
                    
        return total

    try:
        total_bytes = process_directory(path)
        return float(total_bytes) / (1024 ** 3)  # Convert to GB
    except Exception as e:
        log.error(f"Error calculating directory size: {e}")
        return 0


def get_caches_list() -> list[Cache]:
    """Main function of this script, which will create the list of caches
    :return: A list containing Cache instances, themselves containing CacheVersion instances
    """
    caches = []
    caches_root = hou.expandString(CACHES_ROOT)

    # 1. Scan the caches root folder 
    cache_versions_paths = []
    for p in os.listdir(caches_root):
        cache_path = os.path.join(caches_root, p)

        # Let's first check if the path is a directory and if it matches the cache pattern
        if os.path.isdir(cache_path) and VERSION_PATTERN.match(os.path.basename(cache_path)) is not None:
            cache_versions_paths.append(cache_path)

    # 2. Then for each pat let's create a Cache instance
    cache_instances_to_create = []
    for version_path in cache_versions_paths:
        match = VERSION_PATTERN.match(os.path.basename(version_path))
        cache_instances_to_create.append(match.group("name"))

    # 3. Let's remove duplicates
    cache_instances_to_create = set(cache_instances_to_create)

    for instance_to_create in cache_instances_to_create:
        versions = [i for i in cache_versions_paths if os.path.basename(
            i).startswith(instance_to_create)
        ]
        caches.append(Cache(name=instance_to_create, version_paths=versions))

    return caches

