from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict, List, Union
from typing import OrderedDict as ODict

from PySide6.QtGui import QColor, QIcon, QPixmap


@dataclass
class MOData:
    mo_number: int = 0
    mo_symmetry: str = ""
    energy: float = 0.0
    ao_type: List[str] = field(default_factory=list)
    percentage: List[float] = field(default_factory=list)
    ao_len: int = 0

    def update_mo_data(
        self, mo_number: int, mo_symmetry: str, energy: float, ao_type: List[str], percentage: List[float], ao_len: int
    ) -> None:
        self.mo_number = mo_number
        self.mo_symmetry = mo_symmetry
        self.energy = energy
        self.ao_type = ao_type
        self.percentage = percentage
        self.ao_len = ao_len

    def create_mo_data(self, row: List[str]) -> None:
        mo_symmetry = row[0]
        mo_number_dirac = int(row[1])
        mo_energy = float(row[2])
        ao_type = [row[i] for i in range(3, len(row), 2)]
        ao_percentage = [float(row[i]) for i in range(4, len(row), 2)]
        self.update_mo_data(mo_number_dirac, mo_symmetry, mo_energy, ao_type, ao_percentage, len(ao_type))


@dataclass
class SpinorNumber:
    closed_shell: int = 0
    open_shell: int = 0
    virtual_orbitals: int = 0
    sum_of_orbitals: int = 0

    def __add__(self, other: "SpinorNumber") -> "SpinorNumber":
        if not isinstance(other, SpinorNumber):
            msg = f"unsupported operand type(s) for +: {type(self)} and {type(other)}"
            raise TypeError(msg)
        return SpinorNumber(
            self.closed_shell + other.closed_shell,
            self.open_shell + other.open_shell,
            self.virtual_orbitals + other.virtual_orbitals,
            self.sum_of_orbitals + other.sum_of_orbitals,
        )


class MoltraInfo(Dict[str, ODict[int, bool]]):
    pass


class SpinorNumInfo(Dict[str, SpinorNumber]):
    pass


@dataclass
class HeaderInfo:
    spinor_num_info: SpinorNumInfo = field(default_factory=SpinorNumInfo)
    moltra_info: MoltraInfo = field(default_factory=MoltraInfo)
    point_group: str = ""
    moltra_scheme: Union[int, None] = None
    electron_number: int = 0

    def read_spinor_num_info(self, row: List[str]) -> None:
        # spinor_num info is following the format:
        # spinor_num_type1 closed int open int virtual int ...
        # (e.g.) E1g closed 6 open 0 virtual 30 E1u closed 10 open 0 virtual 40 point_group C2v
        # => self.spinor_num_info = {"E1g": SpinorNumber(6, 0, 30, 36),
        #                                              "E1u": SpinorNumber(10, 0, 40, 50)}
        if len(row) < 7:
            msg = f"spinor_num info is not correct: {row},\
spinor_num_type1 closed int open int virtual int spinor_num_type2 closed int open int virtual int ... point_group str\n\
is the correct format"
            raise ValueError(msg)
        idx = 0
        while idx + 7 <= len(row):
            spinor_num_type = row[idx]
            closed_shell = int(row[idx + 2])
            open_shell = int(row[idx + 4])
            virtual_orbitals = int(row[idx + 6])
            sum_of_orbitals = closed_shell + open_shell + virtual_orbitals
            self.spinor_num_info[spinor_num_type] = SpinorNumber(
                closed_shell, open_shell, virtual_orbitals, sum_of_orbitals
            )
            idx += 7

    def read_moltra_info(self, row: List[str]) -> None:
        idx = 0
        while idx + 2 <= len(row):
            moltra_type = row[idx]
            moltra_range_str = row[idx + 1]
            moltra_range: ODict[int, bool] = OrderedDict()
            for elem in moltra_range_str.split(","):
                moltra_range_elem = elem.strip()
                if ".." in moltra_range_elem:
                    moltra_range_start_str, moltra_range_end_str = moltra_range_elem.split("..")
                    moltra_range_start = int(moltra_range_start_str)
                    moltra_range_end = int(moltra_range_end_str)
                    for i in range(moltra_range_start, moltra_range_end + 1):
                        moltra_range[i] = True
                else:
                    key_elem = int(moltra_range_elem)
                    moltra_range[key_elem] = True
            self.moltra_info[moltra_type] = moltra_range
            idx += 2
        for key in self.moltra_info.keys():
            self.moltra_info[key] = OrderedDict(sorted(self.moltra_info[key].items()))

    def update_electron_number(self, number: int) -> None:
        self.electron_number = number

    def update_point_group(self, value: str) -> None:
        self.point_group = value

    def update_moltra_scheme(self, value: str) -> None:
        if value == "default":
            self.moltra_scheme = None
        else:
            self.moltra_scheme = int(value)


class OrbitalSpaceData:
    found: bool
    first: int
    last: int

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.found = False
        self.first = -1
        self.last = -1


class TableIdxInfo:
    """This class stores the first and last indexes for inactive and secondary
    to determine if the context menu (right-click menu) should be displayed.
    """

    inactive: OrbitalSpaceData
    secondary: OrbitalSpaceData

    def __init__(self):
        self.inactive = OrbitalSpaceData()
        self.secondary = OrbitalSpaceData()

    def reset(self) -> None:
        self.inactive.reset()
        self.secondary.reset()

    def update_idx_info(self, row_idx: int, color_name: str) -> None:
        if color_name not in ("inactive", "secondary"):
            # active, ras1, ras3 are not included because their context menu (right click menu) is always shown
            # and they are not needed to store the index information
            # therefore, skip them
            return
        elif color_name == "inactive":
            if not self.inactive.found:
                # First time to find inactive
                self.inactive.found = True
                self.inactive.first = row_idx
            # Always update the last idx
            self.inactive.last = row_idx
        else:  # secondary
            if not self.secondary.found:
                # First time to find secondary
                self.secondary.found = True
                self.secondary.first = row_idx
            # Always update the last idx
            self.secondary.last = row_idx

    def should_show_inactive_action_menu(self, top_row: int) -> bool:
        if self.secondary.found and top_row > self.secondary.first:
            # secondary starts from the row before top_row.
            # All inactive are before secondary, so it is guaranteed that there are no inactive in the selection range.
            return False
        return True

    def should_show_secondary_action_menu(self, bottom_row: int) -> bool:
        if self.inactive.found and bottom_row < self.inactive.last:
            # inactive ends on the row after bottom_row.
            # All inactive are before secondary, so it is guaranteed that there are no secondary in the selection range.
            return False
        return True


class TableData:
    mo_data: List[MOData]
    column_max_len: int
    header_info: HeaderInfo
    idx_info: TableIdxInfo

    def __init__(self):
        self.reset()

    def reset(self):
        self.mo_data = []
        self.column_max_len = 0
        self.header_info = HeaderInfo()
        self.idx_info = TableIdxInfo()

    def add_mo_data(self, row: List[str]) -> None:
        """Add a MOData to self.mo_data"""
        new_mo = MOData()
        new_mo.create_mo_data(row)
        self.mo_data.append(new_mo)

    def validate(self) -> None:
        """Check TableData values consistency.
        In addition, decrease header_info.electron_number
        by the number of electrons that are not included in the sum_dirac_dfcoef output.

        Raises:
            KeyError: _description_
            KeyError: _description_
        """

        # Check whether header_info.moltra_info and header_info.spinor_num_info have same keys or not.
        if self.header_info.spinor_num_info.keys() != self.header_info.moltra_info.keys():
            msg = "Keys of spinor_num_info.keys() and moltra_info.keys() are not same."
            raise KeyError(msg)

        # Get the minimum mo_number index per mo_symmetry
        keys = self.header_info.spinor_num_info.keys()
        max_int = 10**10
        min_idx = {key: max_int for key in keys}
        for mo in self.mo_data:
            key = mo.mo_symmetry
            if key not in keys:
                msg = f"mo_symmetry {key} is not found in the eigenvalues data"
                raise KeyError(msg)
            min_idx[key] = min(min_idx[key], mo.mo_number)

        # Decrease the 2*(min_idx[key]-1) from header_info.electron_number
        # Because min_idx[key] stores the first orbitals mo_number included in the output,
        # we need to decrease the electron number that is not included in the output.
        table_data.header_info.electron_number -= sum(first_mo_idx - 1 for first_mo_idx in min_idx.values()) * 2


table_data = TableData()


@dataclass
class ColorPopupInfo:
    color: QColor
    name: str
    message: str
    icon: QIcon


class Color:
    def __init__(self):
        # Default color
        self.color_type = "default"
        self.change_color_templates(self.color_type)

    def __eq__(self, __value: object):
        if not isinstance(__value, Color):
            return NotImplemented
        # Compare all colors
        if self.inactive != __value.inactive:
            return False
        elif self.ras1 != __value.ras1:
            return False
        elif self.active != __value.active:
            return False
        elif self.ras3 != __value.ras3:
            return False
        elif self.secondary != __value.secondary:
            return False
        else:
            return True

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    def deep_copy(self):
        new_color = Color()
        new_color.color_type = self.color_type
        new_color.colormap = self.colormap.copy()

        for key, value in self.__dict__.items():
            if isinstance(value, ColorPopupInfo):
                setattr(new_color, key, value)

        new_color.not_used.icon = self.create_icon(new_color.not_used.color)
        new_color.inactive.icon = self.create_icon(new_color.inactive.color)
        new_color.ras1.icon = self.create_icon(new_color.ras1.color)
        new_color.active.icon = self.create_icon(new_color.active.color)
        new_color.ras3.icon = self.create_icon(new_color.ras3.color)
        new_color.secondary.icon = self.create_icon(new_color.secondary.color)

        return new_color

    def get_color_info(self, q_color: QColor):
        if q_color.name() in self.colormap:
            return self.colormap[q_color.name()]
        else:
            msg = f"Cannot find the corresponding color. q_color: {q_color.name()}, {q_color.getRgb()}"
            raise ValueError(msg)

    def create_icon(self, color: QColor, size=64):
        pixmap = QPixmap(size, size)
        pixmap.fill(color)
        icon = QIcon(pixmap)
        return icon

    def change_color_templates(self, color_type: str):
        if color_type == "default":
            # Default color
            color_not_used, msg_not_used, msg_color_not_used = (
                QColor("#FFFFFF"),
                "not used in CASPT2",
                "not used in CASPT2(White)",
            )
            color_inactive, msg_inactive, msg_color_inactive = QColor("#D5ECD4"), "inactive", "inactive(Pale Green)"
            color_ras1, msg_ras1, msg_color_ras1 = QColor("#BBA0CB"), "ras1", "ras1(Pale Purple)"
            color_active, msg_active, msg_color_active = QColor("#F4D9D9"), "active", "active, ras2(Pale Pink)"
            color_ras3, msg_ras3, msg_color_ras3 = QColor("#FFB7C5"), "ras3", "ras3(Pastel Pink)"
            color_secondary, msg_secondary, msg_color_secondary = (
                QColor("#FDF4CD"),
                "secondary",
                "secondary(Pale Yellow)",
            )
            self.not_used = ColorPopupInfo(
                color_not_used, msg_not_used, msg_color_not_used, self.create_icon(color_not_used)
            )
            self.inactive = ColorPopupInfo(
                color_inactive, msg_inactive, msg_color_inactive, self.create_icon(color_inactive)
            )
            self.ras1 = ColorPopupInfo(color_ras1, msg_ras1, msg_color_ras1, self.create_icon(color_ras1))
            self.active = ColorPopupInfo(color_active, msg_active, msg_color_active, self.create_icon(color_active))
            self.ras3 = ColorPopupInfo(color_ras3, msg_ras3, msg_color_ras3, self.create_icon(color_ras3))
            self.secondary = ColorPopupInfo(
                color_secondary, msg_secondary, msg_color_secondary, self.create_icon(color_secondary)
            )
        elif color_type == "Color type 1":
            # Color type 1
            not_used, msg_not_used, msg_color_not_used = (
                QColor("#FFFFFF"),
                "not used in CASPT2",
                "not used in CASPT2(White)",
            )
            color_inactive, msg_inactive, msg_color_inactive = QColor("#FFA07A"), "inactive", "inactive(Light salmon)"
            color_ras1, msg_ras1, msg_color_ras1 = QColor("#32CD32"), "ras1", "ras1(Lime green)"
            color_active, msg_active, msg_color_active = QColor("#ADFF2F"), "active", "active, ras2(Green yellow)"
            color_ras3, msg_ras3, msg_color_ras3 = QColor("#FFFF00"), "ras3", "ras3(Yellow)"
            color_secondary, msg_secondary, msg_color_secondary = (
                QColor("#DA70D6"),
                "secondary",
                "secondary(Orchid)",
            )
            self.not_used = ColorPopupInfo(not_used, msg_not_used, msg_color_not_used, self.create_icon(not_used))
            self.inactive = ColorPopupInfo(
                color_inactive, msg_inactive, msg_color_inactive, self.create_icon(color_inactive)
            )
            self.ras1 = ColorPopupInfo(color_ras1, msg_ras1, msg_color_ras1, self.create_icon(color_ras1))
            self.active = ColorPopupInfo(color_active, msg_active, msg_color_active, self.create_icon(color_active))
            self.ras3 = ColorPopupInfo(color_ras3, msg_ras3, msg_color_ras3, self.create_icon(color_ras3))
            self.secondary = ColorPopupInfo(
                color_secondary, msg_secondary, msg_color_secondary, self.create_icon(color_secondary)
            )
        elif color_type == "Color type 2":
            # Color type 2
            not_used, msg_not_used, msg_color_not_used = (
                QColor("#FFFFFF"),
                "not used in CASPT2",
                "not used in CASPT2(White)",
            )
            color_inactive, msg_inactive, msg_color_inactive = QColor("#FFA07A"), "inactive", "inactive(Light salmon)"
            color_ras1, msg_ras1, msg_color_ras1 = QColor("#FFD700"), "ras1", "ras1(Gold)"
            color_active, msg_active, msg_color_active = QColor("#FF1493"), "active", "active, ras2(Deep pink)"
            color_ras3, msg_ras3, msg_color_ras3 = QColor("#4682B4"), "ras3", "ras3(Steel blue)"
            color_secondary, msg_secondary, msg_color_secondary = (
                QColor("#6A5ACD"),
                "secondary",
                "secondary(Slate blue)",
            )
            self.not_used = ColorPopupInfo(not_used, msg_not_used, msg_color_not_used, self.create_icon(not_used))
            self.inactive = ColorPopupInfo(
                color_inactive, msg_inactive, msg_color_inactive, self.create_icon(color_inactive)
            )
            self.ras1 = ColorPopupInfo(color_ras1, msg_ras1, msg_color_ras1, self.create_icon(color_ras1))
            self.active = ColorPopupInfo(color_active, msg_active, msg_color_active, self.create_icon(color_active))
            self.ras3 = ColorPopupInfo(color_ras3, msg_ras3, msg_color_ras3, self.create_icon(color_ras3))
            self.secondary = ColorPopupInfo(
                color_secondary, msg_secondary, msg_color_secondary, self.create_icon(color_secondary)
            )
        else:
            msg = f"Invalid color type: {color_type}"
            raise ValueError(msg)
        self.color_type = color_type

        # colormap is a dictionary that maps QColor.name() to ColorPopupInfo
        # QColor is not hashable, so I use QColor.name() instead of QColor for dictionary keys.
        self.colormap = {
            self.not_used.color.name(): self.not_used,
            self.inactive.color.name(): self.inactive,
            self.ras1.color.name(): self.ras1,
            self.active.color.name(): self.active,
            self.ras3.color.name(): self.ras3,
            self.secondary.color.name(): self.secondary,
        }


colors = Color()
