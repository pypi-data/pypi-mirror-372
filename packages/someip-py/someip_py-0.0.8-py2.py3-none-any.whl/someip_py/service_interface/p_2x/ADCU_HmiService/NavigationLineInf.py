from someip_py.codec import *


class CoordinateSys(SomeIpPayload):

    CoordinateXSeN: Int32

    CoordinateYSeN: Int32

    CoordinateZSeN: Int32

    def __init__(self):

        self.CoordinateXSeN = Int32()

        self.CoordinateYSeN = Int32()

        self.CoordinateZSeN = Int32()


class IdtNavigationLineKls(SomeIpPayload):
    _has_dynamic_size = True

    NavigationLineIdSeN: Uint32

    GeometryPointsSeN: SomeIpDynamicSizeArray[CoordinateSys]

    DestinationSlotIdSeN: Uint32

    def __init__(self):

        self.NavigationLineIdSeN = Uint32()

        self.GeometryPointsSeN = SomeIpDynamicSizeArray(CoordinateSys)

        self.DestinationSlotIdSeN = Uint32()


class IdtNavigationLine(SomeIpPayload):

    IdtNavigationLine: IdtNavigationLineKls

    def __init__(self):

        self.IdtNavigationLine = IdtNavigationLineKls()
