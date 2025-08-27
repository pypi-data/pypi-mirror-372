from enum import Enum


class LEDColor(str, Enum):
    """LED Bar 색상 정의

    Available colors for LED bar control.
    """

    NONE = "NONE"
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"
    WHITE = "WHITE"
    CYAN = "CYAN"
    MAGENTA = "MAGENTA"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"


class ZReference(str, Enum):
    """Z-axis position reference point

    랩웨어 기준 높이:
    - BOTTOM_JUST: 랩웨어 바닥 표면
    - BOTTOM: 표준 액체 핸들링 높이 (bottom_offset 적용)
    - TOP_JUST: 랩웨어 웰 상단 표면
    - TOP: 안전 이동 높이 (top_offset 적용)

    팁 랙에서의 사용:
    - TOP_JUST: 팁 장착 시작 높이 (팁 상단)
    - BOTTOM_JUST: 팁 장착 완료 높이 (팁 홀더 바닥)
    - BOTTOM: 팁 탈착 높이 (cone_length만큼 덜 들어감)
    - TOP: 안전 이동 높이
    """

    BOTTOM_JUST = "BOTTOM_JUST"  # 랩웨어 바닥 표면
    BOTTOM = "BOTTOM"  # 바닥에서 offset 적용된 높이
    TOP_JUST = "TOP_JUST"  # 랩웨어 상단 표면
    TOP = "TOP"  # 상단에서 offset 적용된 안전 높이


class Axis(str, Enum):
    """Robot axis definitions
    
    Available axes for motion control:
    - X, Y: Horizontal movement axes
    - Z1, Z2: Vertical axes for pipette mounts 1 and 2
    - P1, P2: Plunger axes for pipettes 1 and 2
    """
    X = "x"
    Y = "y"
    Z1 = "z1"
    Z2 = "z2"
    P1 = "p1"
    P2 = "p2"


class PipetteType(str, Enum):
    """Pipette type definitions"""
    SINGLE = "single"
    MULTI = "multi"


class LabwareType(str, Enum):
    """Labware type definitions for configuration"""
    PLATE = "plate"
    RESERVOIR = "reservoir"
    TIP_RACK = "tip_rack"
