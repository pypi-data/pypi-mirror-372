from collections import OrderedDict

from dcaspt2_input_generator.components.data import colors, table_data
from dcaspt2_input_generator.components.table_summary import TableSummary
from dcaspt2_input_generator.components.table_widget import TableWidget
from dcaspt2_input_generator.utils.dir_info import dir_info


class WidgetController:
    def __init__(self, table_summary: TableSummary, table_widget: TableWidget):
        self.table_summary = table_summary
        self.table_widget = table_widget

        # change_background_color is a slot
        self.table_widget.color_changed.connect(self.onTableWidgetColorChanged)

    def onTableWidgetColorChanged(self):
        def get_max_mem_str(estimated_max_mem: int) -> str:
            kb = 1024
            mb = kb**2
            gb = kb**3
            if estimated_max_mem < kb:  # byte
                return f"{estimated_max_mem} byte"
            elif estimated_max_mem < mb:  # KB
                mem = float(estimated_max_mem) / kb
                return f"{mem:.3f} KB"
            elif estimated_max_mem < gb:  # MB
                mem = float(estimated_max_mem) / mb
                return f"{mem:.3f} MB"
            else:
                mem = float(estimated_max_mem) / gb
                return f"{mem:.3f} GB"

        color_count = {"inactive": 0, "ras1": 0, "active, ras2": 0, "ras3": 0, "secondary": 0}
        row_count = self.table_widget.rowCount()
        for row in range(row_count):
            color = self.table_widget.item(row, 0).background()
            sym_str = self.table_widget.item(row, 0).text()
            mo_num = int(self.table_widget.item(row, 1).text())
            table_data.header_info.moltra_info[sym_str][mo_num] = False if color == colors.not_used.color else True

            if color == colors.inactive.color:
                color_count["inactive"] += 2
            elif color == colors.ras1.color:
                color_count["ras1"] += 2
            elif color == colors.active.color:
                color_count["active, ras2"] += 2
            elif color == colors.ras3.color:
                color_count["ras3"] += 2
            elif color == colors.secondary.color:
                color_count["secondary"] += 2

        # Update summary information
        self.table_summary.spinor_summary.inactive_label.setText(f"inactive: {color_count['inactive']}")
        self.table_summary.spinor_summary.ras1_label.setText(f"ras1: {color_count['ras1']}")
        self.table_summary.spinor_summary.active_label.setText(f"active, ras2: {color_count['active, ras2']}")
        self.table_summary.spinor_summary.ras3_label.setText(f"ras3: {color_count['ras3']}")
        self.table_summary.spinor_summary.secondary_label.setText(f"secondary: {color_count['secondary']}")

        # Update the maximum number of holes and electrons
        self.table_summary.user_input.ras1_max_hole_number.set_top(color_count["ras1"])
        self.table_summary.user_input.ras3_max_electron_number.set_top(color_count["ras3"])
        res = ""
        for k, d in table_data.header_info.moltra_info.items():
            res += f"\n {k}"
            range_str = ""
            start = True
            prev_mo_num = 0
            range_start_num = 0
            search_end = False
            sorted_d = OrderedDict(sorted(d.items()))
            for mo_num, is_used in sorted_d.items():
                search_end = True
                if not is_used:
                    continue
                if start:
                    # First used MO
                    range_str += f" {mo_num}"
                    range_start_num = mo_num
                    start = False
                elif mo_num != prev_mo_num + 1:
                    if range_start_num == prev_mo_num:
                        # Prev MO is alone, already added to range_str
                        range_str += f" {mo_num}"
                        range_start_num = mo_num
                    else:
                        # Prev MO is not alone, not added to range_str yet
                        range_str += f"..{prev_mo_num} {mo_num}"
                        range_start_num = mo_num
                prev_mo_num = mo_num
            if search_end and range_start_num != prev_mo_num:
                # prev_mo_num is not added to range_str
                range_str += f"..{prev_mo_num}"
            res += range_str

        self.table_summary.recommended_moltra.setText(f"Recommended MOLTRA setting: {res}")
        if table_data.header_info.point_group is not None:
            inact = color_count["inactive"]
            act = color_count["ras1"] + color_count["active, ras2"] + color_count["ras3"]
            sec = color_count["secondary"]
            inttwo = (
                8 * ((inact + act) ** 4) * (2 if table_data.header_info.point_group == "C1" else 1)
            )  # inttwr, inttwi # noqa E501
            inttwo_f1_f2 = (
                8 * (sec**2 * (inact + act) ** 2) * (4 if table_data.header_info.point_group == "C1" else 2)
            )  # inttwr_f1, inttwi_f1, inttwr_f2, inttwi_f2 # noqa E501
            indkl = (8 * (inact + act + sec) ** 2) * 2  # indk, indl
            rkl = (8 * (inact + act + sec) ** 2) * (
                2 if table_data.header_info.point_group == "C1" else 1
            )  # rklr, rkli # noqa E501
            estimated_max_mem = inttwo + inttwo_f1_f2 + indkl + rkl
            if estimated_max_mem < 0:
                estimated_max_mem = 0
            mem_str = get_max_mem_str(estimated_max_mem)

            txt = f"Point Group: {table_data.header_info.point_group}, estimated max memory size: {mem_str}"
            self.table_summary.point_group.setText(txt)
        else:
            txt = "Point Group: could not be obtained, cannot detect the maximum memory size of the dirac_caspt2 calcluation."  # noqa E501
            self.table_summary.point_group.setText(txt)

        # Reload the input
        self.table_summary.update()
