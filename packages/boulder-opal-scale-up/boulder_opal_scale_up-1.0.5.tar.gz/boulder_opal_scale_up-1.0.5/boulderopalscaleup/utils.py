from boulderopalscaleupsdk.common.dtypes import Duration
from boulderopalscaleupsdk.device.common import Component
from boulderopalscaleupsdk.device.processor.common import ComponentParameter
from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass
from rich.columns import Columns
from rich.console import Console
from rich.table import Table


def _split_table_sizes(length: int) -> list[int]:
    # We split the parameters into sets of up to preferred_width columns,
    # each one will be displayed in a separate table.
    # (If there'd be a spare column, we add it to the first table.)
    preferred_width = 4
    if length <= preferred_width + 1:
        return [length]
    set_sizes = [preferred_width] * (length // preferred_width)
    remainder = length - sum(set_sizes)
    if remainder == 1:
        set_sizes[0] += 1
    elif remainder != 0:
        set_sizes.append(remainder)
    return set_sizes


@dataclass
class _DisplayInfo:
    label: str
    unit: str
    scale: float

    def _get_value(self, value: float | Duration | None) -> float | None:
        if isinstance(value, float | int):
            return value * self.scale
        if isinstance(value, Duration):
            return value.to_seconds() * self.scale
        return None

    @property
    def table_header(self) -> str:
        return f"{self.label}\n({self.unit})"

    def get_table_info(self, parameter: ComponentParameter | None) -> tuple[str, str, str]:
        if parameter is None:
            return "None", "None", "None"
        value = self._get_value(parameter.value)
        em = self._get_value(parameter.err_minus)
        ep = self._get_value(parameter.err_plus)
        std = em + ep if em is not None and ep is not None else None
        return str(value), str(std), str(parameter.calibration_status)


def display_element(reference: str, component: Component) -> None:
    console = Console()

    display_info = {
        k: TypeAdapter(_DisplayInfo).validate_python(extra["display"])
        for k, v in type(component).model_fields.items()
        if isinstance(extra := v.json_schema_extra, dict) and "display" in extra
    }
    headers = list(display_info.keys())

    tables = []
    for length in _split_table_sizes(len(display_info)):
        table = Table()
        table.add_column("", justify="right")
        values = ["value"]
        stds = ["std"]
        calibration_statuses = ["calibration status"]
        for _ in range(length):
            header = headers.pop(0)
            display = display_info[header]
            parameter = getattr(component, header)

            table.add_column(display.table_header, justify="center")
            value, std, calibration_status = display.get_table_info(parameter)
            values.append(value)
            stds.append(std)
            calibration_statuses.append(calibration_status)

        table.add_row(*values)
        table.add_row(*stds)
        table.add_row(*calibration_statuses)
        tables.append(table)

    console.print(Columns(tables, title=f"{type(component).__name__} {reference}"))
