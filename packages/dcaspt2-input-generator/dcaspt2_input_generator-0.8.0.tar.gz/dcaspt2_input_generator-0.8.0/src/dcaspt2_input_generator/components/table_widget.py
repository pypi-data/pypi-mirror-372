from pathlib import Path
from typing import List

from dcaspt2_input_generator.components.data import Color, colors, table_data
from dcaspt2_input_generator.utils.utils import debug_print
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QColor
from PySide6.QtWidgets import QMenu, QTableWidget, QTableWidgetItem, QCommonStyle


# TableWidget is the widget that displays the output data
# It is a extended class of QTableWidget
# It has the following features:
# 1. Load the output data from the file "data.out"
# 2. Reload the output data
# 3. Show the context menu when right click
# 4. Change the background color of the selected cells
# 5. Emit the color_changed signal when the background color is changed
# Display the output data like the following:
# irrep              no. of spinor    energy (a.u.)    percentage 1    AO type 1    percentage 2    AO type 2    ...
# E1u                1                -9.631           33.333          B3uArpx      33.333          B2uArpy      ...
# E1u                2                -9.546           50.000          B3uArpx      50.000          B2uArpy      ...
# ...
class TableWidget(QTableWidget):
    color_changed = Signal()

    def __init__(self):
        debug_print("TableWidget init")
        super().__init__()
        self.setStyle(QCommonStyle())
        self.setStyleSheet("QTableWidget{color:black}")
        # Set the context menu policy to custom context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # QTableWidget.ContiguousSelection: Multiple ranges selection is impossible.
        # https://doc.qt.io/qt-6/qabstractitemview.html#SelectionMode-enum
        self.setSelectionMode(QTableWidget.SelectionMode.ContiguousSelection)

    def reload(self, output_file_path: Path):
        debug_print("TableWidget reload")
        self.load_output(output_file_path)

    def update_index_info(self):
        # Reset information
        table_data.idx_info.reset()

        # Update information
        for row in range(self.rowCount()):
            row_color = self.item(row, 0).background().color()
            color_info = colors.get_color_info(row_color)
            table_data.idx_info.update_idx_info(row, color_info.name)

    def create_table(self):
        debug_print("TableWidget create_table")
        self.clear()
        rows = table_data.mo_data
        rows.sort(key=lambda x: (x.energy))
        self.setRowCount(len(rows))
        self.setColumnCount(table_data.column_max_len)

        rem_electrons = table_data.header_info.electron_number
        active_cnt = 0

        for row_idx, row in enumerate(rows):
            # Default CAS configuration is CAS(4,8) (4electrons, 8spinors)
            key = row.mo_symmetry
            moltra_info = table_data.header_info.moltra_info[key]
            if not moltra_info.get(row.mo_number, False):
                color_info = colors.not_used  # not in MOLTRA
            elif rem_electrons > 4:
                color_info = colors.inactive
            elif active_cnt < 8:
                active_cnt += 2
                color_info = colors.active
            else:
                color_info = colors.secondary

            rem_electrons -= 2
            color = color_info.color
            self.setItem(row_idx, 0, QTableWidgetItem(row.mo_symmetry))
            self.setItem(row_idx, 1, QTableWidgetItem(str(row.mo_number)))
            self.setItem(row_idx, 2, QTableWidgetItem(str(row.energy)))
            # percentage, ao_type
            column_before_ao_percentage = 3
            for idx in range(table_data.column_max_len - column_before_ao_percentage):
                try:
                    ao_type = QTableWidgetItem(row.ao_type[idx])
                    ao_percentage = QTableWidgetItem(str(row.percentage[idx]))
                except IndexError:
                    ao_type = QTableWidgetItem("")
                    ao_percentage = QTableWidgetItem("")
                ao_type.setBackground(color)
                ao_percentage.setBackground(color)
                ao_type_column = column_before_ao_percentage + 2 * idx
                ao_percentage_column = ao_type_column + 1
                self.setItem(row_idx, ao_type_column, ao_type)
                self.setItem(row_idx, ao_percentage_column, ao_percentage)

            for idx in range(table_data.column_max_len):
                self.item(row_idx, idx).setBackground(color)
        self.update_index_info()

    def set_column_header_items(self):
        header_data = ["irrep", "no. of spinor", "energy (a.u.)"]
        init_header_len = len(header_data)
        additional_header = []
        for idx in range(init_header_len, table_data.column_max_len):
            if idx % 2 == 0:
                additional_header.append(f"percentage {(idx-init_header_len)//2 + 1}")
            else:
                additional_header.append(f"AO type {(idx-init_header_len)//2 + 1}")

        header_data.extend(additional_header)
        self.setHorizontalHeaderLabels(header_data)

    def resize_columns(self):
        self.resizeColumnsToContents()
        for idx in range(table_data.column_max_len):
            if idx == 0:  # irrep
                self.setColumnWidth(idx, self.columnWidth(idx) + 20)
            elif idx == 1 or idx % 2 == 0:  # no. of spinor, percentage
                self.setColumnWidth(idx, self.columnWidth(idx) + 10)
            else:  # energy, AO type
                self.setColumnWidth(idx, self.columnWidth(idx) + 5)

    def load_output(self, file_path: Path):
        def set_table_data(rows: List[List[str]]):
            try:
                header = True
                for row in rows:
                    if header:
                        if len(row) <= 1:  # Empty line, end of header
                            header = False
                    else:
                        if len(row) == 0:
                            continue
                        table_data.add_mo_data(row)
                        table_data.column_max_len = max(table_data.column_max_len, len(row))
            except ValueError as e:
                msg = "The output file is not correct, ValueError"
                raise ValueError(msg) from e
            except IndexError as e:
                msg = "The output file is not correct, IndexError"
                raise IndexError(msg) from e

        def read_header(rows: List[List[str]]):
            try:
                for idx, row in enumerate(rows):
                    if len(row) <= 1:  # Empty line, end of header
                        break
                    elif idx == 0:
                        # 1st line: Read key-value info
                        # (e.g.) electron_num 18 point_group D2h moltra_scheme default
                        if len(row) % 2 != 0:
                            msg = f"1st header line must be even elements because this line is for key-value info.\
len(1st header)={len(row)}"
                            raise IndexError(msg)

                        for key_idx in range(0, len(row), 2):  # loop only key
                            key = row[key_idx]
                            value = row[key_idx + 1]
                            if key == "electron_num":
                                table_data.header_info.update_electron_number(int(value))
                            elif key == "point_group":
                                table_data.header_info.update_point_group(value)
                            elif key == "moltra_scheme":
                                table_data.header_info.update_moltra_scheme(value)
                    elif idx == 1:
                        # 2nd line: MOLTRA range
                        # (e.g.) E1g 16..85 E1u 11..91
                        table_data.header_info.read_moltra_info(row)
                    elif idx == 2:
                        # 3rd line: Eigenvalue info
                        # (e.g.) E1g closed 6 open 0 virtual 30 E1u closed 10 open 0 virtual 40
                        # => table_data.header_info.spinor_num_info = {"E1g": SpinorNumber(6, 0, 30, 36),
                        #                                              "E1u": SpinorNumber(10, 0, 40, 50)}
                        table_data.header_info.read_spinor_num_info(row)
                    else:
                        # Skip unknown header info line
                        continue
            except ValueError as e:
                msg = "The output file is not correct, ValueError"
                raise ValueError(msg) from e
            except IndexError as e:
                msg = "The output file is not correct, IndexError"
                raise IndexError(msg) from e

        table_data.reset()
        rows = [line.split() for line in open(file_path).readlines()]
        # output is space separated file
        read_header(rows)
        set_table_data(rows)
        table_data.validate()
        self.create_table()
        self.set_column_header_items()
        self.resize_columns()
        self.color_changed.emit()

    def show_context_menu(self, position):
        menu = QMenu()
        ranges = self.selectedRanges()
        selected_rows: List[int] = []
        for r in ranges:
            selected_rows.extend(range(r.topRow(), r.bottomRow() + 1))

        top_row = selected_rows[0]
        bottom_row = selected_rows[-1]

        # Show the inactive action
        if table_data.idx_info.should_show_inactive_action_menu(top_row):
            inactive_action = QAction(colors.inactive.icon, colors.inactive.message)
            inactive_action.triggered.connect(lambda: self.change_background_color(colors.inactive.color))
            menu.addAction(inactive_action)

        # Show the secondary action
        if table_data.idx_info.should_show_secondary_action_menu(bottom_row):
            secondary_action = QAction(colors.secondary.icon, colors.secondary.message)
            secondary_action.triggered.connect(lambda: self.change_background_color(colors.secondary.color))
            menu.addAction(secondary_action)

        # Show the active action
        ras1_action = QAction(colors.ras1.icon, colors.ras1.message)
        ras1_action.triggered.connect(lambda: self.change_background_color(colors.ras1.color))
        menu.addAction(ras1_action)

        active_action = QAction(colors.active.icon, colors.active.message)
        active_action.triggered.connect(lambda: self.change_background_color(colors.active.color))
        menu.addAction(active_action)

        ras3_action = QAction(colors.ras3.icon, colors.ras3.message)
        ras3_action.triggered.connect(lambda: self.change_background_color(colors.ras3.color))
        menu.addAction(ras3_action)

        not_used_action = QAction(colors.not_used.icon, colors.not_used.message)
        not_used_action.triggered.connect(lambda: self.change_background_color(colors.not_used.color))
        menu.addAction(not_used_action)

        menu.exec_(self.viewport().mapToGlobal(position))

    def change_selected_rows_background_color(self, row, color: QColor):
        for column in range(self.columnCount()):
            item = self.item(row, column)
            if item is not None:
                item.setBackground(color)

    def change_background_color(self, color):
        indexes = self.selectedIndexes()
        rows = {index.row() for index in indexes}
        for row in rows:
            self.change_selected_rows_background_color(row, color)
        self.update_index_info()
        self.color_changed.emit()

    def update_color(self, prev_color: Color):
        debug_print("update_color")
        color_mappping = {
            prev_color.inactive.color.name(): colors.inactive.color,
            prev_color.ras1.color.name(): colors.ras1.color,
            prev_color.active.color.name(): colors.active.color,
            prev_color.ras3.color.name(): colors.ras3.color,
            prev_color.secondary.color.name(): colors.secondary.color,
        }

        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item is None:
                continue
            color = item.background().color()
            new_color = color_mappping.get(color.name())
            if new_color:
                self.change_selected_rows_background_color(row, new_color)
        self.color_changed.emit()
