import os
import re
import hou
import time
import logging

from houCacheCleaner.cache import Cache

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] : %(message)s')
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


def truncate(f: float, n: int) -> str:
    """Truncates / pads a float f to n decimal places without rounding"""
    s = "{}".format(f)
    if "e" in s or "E" in s:
        return "{0:.{1}f}".format(f, n)
    i, p, d = s.partition(".")
    return ".".join([i, (d+"0"*n)[:n]])

def get_dir_size(path: str) -> float:
    """Recursively calculates the size of a directory
    TODO python 3 : Optimize this function
    """
    start_time = time.time()

    total = 0
    for p in os.listdir(path):
        full_path = os.path.join(path, p)
        if os.path.isfile(full_path):
            total += os.path.getsize(full_path)
        elif os.path.isdir(full_path):
            total += get_dir_size(full_path)

    log.info(f"get_dir_size() took {time.time() - start_time} seconds to finish")
    total = float(total) / 1024 / 1024 / 1024 # Convert to GB
    total = truncate(total, 2)
    return total


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
        cache_instances_to_create.append(match.group('name'))

    # 3. Let's remove duplicates
    cache_instances_to_create = set(cache_instances_to_create)

    for instance_to_create in cache_instances_to_create:
        versions = [i for i in cache_versions_paths if os.path.basename(
            i).startswith(instance_to_create)
        ]
        caches.append(Cache(name=instance_to_create, version_paths=versions))

    return caches

