from typing import Literal, Mapping, Optional
from matplotlib.figure import Figure
from enum import Enum
import matplotlib.pyplot as plt


class Preset(Enum):
    ACS = "ACS"
    Elsevier = "Elsevier"
    ICIW = "ICIW"


class Layout(Enum):
    SINGLE_COLUMN = "single_column"
    THREEHALF_COLUMN = "threehalf_column"
    DOUBLE_COLUMN = "double_column"


class Unit(Enum):
    mm = "mm"
    cm = "cm"
    inch = "in"


SIZES = {
    Preset.ACS: {
        Layout.SINGLE_COLUMN: {
            Unit.mm: 82.55,
            Unit.inch: 3.25,
            Unit.cm: 8.255,
        },
        Layout.DOUBLE_COLUMN: {
            Unit.mm: 177.8,
            Unit.inch: 7,
            Unit.cm: 17.78,
        },
    },
    Preset.Elsevier: {
        Layout.SINGLE_COLUMN: {
            Unit.mm: 90,
            Unit.inch: 3.54,
            Unit.cm: 9,
        },
        Layout.THREEHALF_COLUMN: {
            Unit.mm: 140,
            Unit.inch: 5.51,
            Unit.cm: 14,
        },
        Layout.DOUBLE_COLUMN: {
            Unit.mm: 190,
            Unit.inch: 7.48,
            Unit.cm: 19,
        },
    },
    Preset.ICIW: {
        Layout.SINGLE_COLUMN: {
            Unit.mm: 75,
            Unit.inch: 2.95,
            Unit.cm: 7.5,
        },
        Layout.DOUBLE_COLUMN: {
            Unit.mm: 160,
            Unit.inch: 6.3,
            Unit.cm: 16,
        },
        Layout.THREEHALF_COLUMN: {
            Unit.mm: 120,
            Unit.inch: 4.72,
            Unit.cm: 12,
        },
    },
}


def size(
    preset: str | Preset,
    layout: str | Layout,
    unit: str | Unit,
) -> float:
    if not isinstance(preset, Preset):
        try:
            preset = Preset(preset)
        except ValueError:
            raise ValueError(
                f"Invalid Preset {preset}. Has to be one of {[preset for preset in Preset]}"
            )
    if not isinstance(layout, Layout):
        try:
            layout = Layout(layout)
        except ValueError:
            raise ValueError(
                f"Invalid Layout {layout}. Has to be one of {[layout for layout in Layout]}"
            )
    if not isinstance(unit, Unit):
        try:
            unit = Unit(unit)
        except:
            raise ValueError(
                f"Invalid Unit {unit}. Has to be one of {[unit for unit in Unit]}"
            )
    return SIZES[preset][layout][unit]


def figure(
    preset: str | Preset = Preset.ICIW,
    layout: str | Layout = Layout.SINGLE_COLUMN,
    height: Optional[float] = None,
    **kwargs,
) -> Figure:
    width = size(preset, layout, Unit.inch)
    if height is None:
        height = size(preset, Layout.SINGLE_COLUMN, Unit.inch)
    figsize = (width, height)
    fig = plt.figure(figsize=figsize, **kwargs)
    return fig


if __name__ == "__main__":
    print(size("ACS", "single_column", "mm"))
    print(size(Preset.Elsevier, Layout.DOUBLE_COLUMN, Unit.cm))
