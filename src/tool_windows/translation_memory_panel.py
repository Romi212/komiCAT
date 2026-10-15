from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class TranslationMemoryPanel(QDialog):
    def __init__(self, tm_db, parent=None):
        super().__init__(parent)
        self.tm_db = tm_db
        self.setWindowTitle("Translation Memory")
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.resize(600, 360)

        layout = QVBoxLayout(self)

        # Table setup with 3 columns (Source, Target, Context)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Source Text", "Target Text", "Context"])
        
        # Configure column resizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)

        self.refresh_table()

    def refresh_table(self):
        """Fetches all records from the DB and populates the table."""
        entries = self.tm_db.fetch_all_segments()
        self.table.setRowCount(len(entries))
        
        for row, (source_text, target_text, context) in enumerate(entries):
            self.table.setItem(row, 0, QTableWidgetItem(source_text or ""))
            self.table.setItem(row, 1, QTableWidgetItem(target_text or ""))
            self.table.setItem(row, 2, QTableWidgetItem(context or ""))