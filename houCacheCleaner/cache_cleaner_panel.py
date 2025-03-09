import os
from PySide2 import QtWidgets, QtCore

import hou

class CacheCleanerPanel(QtWidgets.QWidget):
    def __init__(self):
        super(CacheCleanerPanel, self).__init__()

        # Set up the UI
        self.init_ui()

        # Scan for caches
        self.scan_caches()

    def init_ui(self):
        # Layout
        self.layout = QtWidgets.QVBoxLayout()

        # Cache list
        self.cache_list = QtWidgets.QListWidget()
        self.layout.addWidget(self.cache_list)

        # Buttons
        self.delete_all_button = QtWidgets.QPushButton("Delete All Versions")
        self.delete_all_button.clicked.connect(self.delete_all_versions)
        self.layout.addWidget(self.delete_all_button)

        self.open_folder_button = QtWidgets.QPushButton("Open Folder")
        self.open_folder_button.clicked.connect(self.open_folder)
        self.layout.addWidget(self.open_folder_button)

        self.setLayout(self.layout)

    def scan_caches(self):
        # Placeholder for cache scanning logic
        # This should scan the disk and populate self.caches with cache info
        self.caches = {
            "cache1": {"size": "100MB", "versions": ["v1", "v2", "v3"]},
            "cache2": {"size": "200MB", "versions": ["v1", "v2"]},
        }

        # Populate the cache list
        for cache_name, cache_info in self.caches.items():
            item = QtWidgets.QListWidgetItem(cache_name)
            item.setData(QtCore.Qt.UserRole, cache_info)
            self.cache_list.addItem(item)

    def delete_all_versions(self):
        # Placeholder for deleting all versions of the selected cache
        selected_items = self.cache_list.selectedItems()
        if not selected_items:
            return

        cache_name = selected_items[0].text()
        cache_info = selected_items[0].data(QtCore.Qt.UserRole)

        # Delete logic here
        print(f"Deleting all versions of {cache_name}")

    def open_folder(self):
        # Placeholder for opening the folder containing the selected cache
        selected_items = self.cache_list.selectedItems()
        if not selected_items:
            return

        cache_name = selected_items[0].text()
        # Open folder logic here
        print(f"Opening folder for {cache_name}")

# Register the panel with Houdini
def createInterface():
    return CacheCleanerPanel()

# Example usage
panel = CacheCleanerPanel()
panel.show()
