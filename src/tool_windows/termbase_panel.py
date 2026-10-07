from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
	QDialog,
	QDialogButtonBox,
	QFormLayout,
	QHBoxLayout,
	QLineEdit,
	QMenu,
	QMessageBox,
	QPushButton,
	QTableWidget,
	QTableWidgetItem,
	QVBoxLayout,
)


class AddTermDialog(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Add Term")

		layout = QVBoxLayout(self)
		form = QFormLayout()
		self.source_input = QLineEdit()
		self.target_input = QLineEdit()
		form.addRow("Source term:", self.source_input)
		form.addRow("Target term:", self.target_input)
		layout.addLayout(form)

		buttons = QDialogButtonBox(
			QDialogButtonBox.StandardButton.Ok
			| QDialogButtonBox.StandardButton.Cancel
		)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)
		layout.addWidget(buttons)


class TermbasePanel(QDialog):
	def __init__(self, termbase, parent=None):
		super().__init__(parent)
		self.termbase = termbase
		self.setWindowTitle("Termbase")
		self.setWindowFlags(
			Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint
		)
		self.setWindowModality(Qt.WindowModality.NonModal)
		self.resize(480, 320)

		layout = QVBoxLayout(self)
		self.table = QTableWidget(0, 2)
		self.table.setHorizontalHeaderLabels(["Source term", "Target term"])
		self.table.horizontalHeader().setStretchLastSection(True)
		self.table.setSelectionBehavior(
			QTableWidget.SelectionBehavior.SelectRows
		)
		self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
		self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self.table.customContextMenuRequested.connect(self._show_context_menu)
		layout.addWidget(self.table)

		button_layout = QHBoxLayout()
		button_layout.addStretch()
		self.add_button = QPushButton("Add Entry")
		self.add_button.clicked.connect(self._add_entry)
		button_layout.addWidget(self.add_button)
		layout.addLayout(button_layout)

		self._refresh_table()

	def _refresh_table(self):
		entries = self.termbase.termbase_dict.items()
		self.table.setRowCount(len(self.termbase.termbase_dict))
		for row, (source_term, target_term) in enumerate(entries):
			self.table.setItem(row, 0, QTableWidgetItem(source_term))
			self.table.setItem(row, 1, QTableWidgetItem(target_term))

	def _add_entry(self):
		dialog = AddTermDialog(self)
		if dialog.exec() != QDialog.DialogCode.Accepted:
			return

		source_term = dialog.source_input.text().strip()
		target_term = dialog.target_input.text().strip()
		if not source_term or not target_term:
			QMessageBox.warning(self, "Invalid Entry", "Both terms are required.")
			return

		self.termbase.add_entry(source_term, target_term)
		self._refresh_table()

	def _show_context_menu(self, position):
		row = self.table.rowAt(position.y())
		if row < 0:
			return

		self.table.selectRow(row)
		menu = QMenu(self)
		delete_action = menu.addAction("Delete Entry")
		action = menu.exec(self.table.viewport().mapToGlobal(position))
		if action == delete_action:
			source_term = self.table.item(row, 0).text()
			self.termbase.remove_entry(source_term)
			self._refresh_table()
