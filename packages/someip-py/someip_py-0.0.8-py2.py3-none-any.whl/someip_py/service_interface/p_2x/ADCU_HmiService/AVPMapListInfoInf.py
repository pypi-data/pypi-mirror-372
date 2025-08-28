from someip_py.codec import *


class CoordinateSys(SomeIpPayload):

    CoordinateXSeN: Int32

    CoordinateYSeN: Int32

    CoordinateZSeN: Int32

    def __init__(self):

        self.CoordinateXSeN = Int32()

        self.CoordinateYSeN = Int32()

        self.CoordinateZSeN = Int32()


class AVPCollectedDestination(SomeIpPayload):

    CollectedDestinationType: Uint8

    CollectedDestinationSlotId: Uint32

    CollectedDestinationPoint: CoordinateSys

    CollectedDestinationFloorLevel: Int8

    CollectedDestinationLineId: Uint32

    CollectedDestinationPriority: Uint8

    CollectedParkMapId: Uint32

    CollectedDestinationName: SomeIpDynamicSizeString

    CollectedDestinationLabel: SomeIpDynamicSizeString

    DestinationType: Uint8

    DestinationEditType: Uint8

    def __init__(self):

        self.CollectedDestinationType = Uint8()

        self.CollectedDestinationSlotId = Uint32()

        self.CollectedDestinationPoint = CoordinateSys()

        self.CollectedDestinationFloorLevel = Int8()

        self.CollectedDestinationLineId = Uint32()

        self.CollectedDestinationPriority = Uint8()

        self.CollectedParkMapId = Uint32()

        self.CollectedDestinationName = SomeIpDynamicSizeString()

        self.CollectedDestinationLabel = SomeIpDynamicSizeString()

        self.DestinationType = Uint8()

        self.DestinationEditType = Uint8()


class AVPCollectedMap(SomeIpPayload):
    _has_dynamic_size = True

    MapId: Uint32

    MapName: SomeIpDynamicSizeString

    DestinationNum: Uint32

    DestinationList: SomeIpDynamicSizeArray[AVPCollectedDestination]

    MapLearningTime: Uint64

    MapType: Uint8

    MapCollectPin: Uint8

    def __init__(self):

        self.MapId = Uint32()

        self.MapName = SomeIpDynamicSizeString()

        self.DestinationNum = Uint32()

        self.DestinationList = SomeIpDynamicSizeArray(AVPCollectedDestination)

        self.MapLearningTime = Uint64()

        self.MapType = Uint8()

        self.MapCollectPin = Uint8()


class IdtAVPMapListInfoKls(SomeIpPayload):
    _has_dynamic_size = True

    MapNumSeN: Uint32

    MapListSeN: SomeIpDynamicSizeArray[AVPCollectedMap]

    LocateMapIdSeN: Uint32

    DestinationListSeN: SomeIpDynamicSizeArray[AVPCollectedDestination]

    MaplistType: Uint8

    def __init__(self):

        self.MapNumSeN = Uint32()

        self.MapListSeN = SomeIpDynamicSizeArray(AVPCollectedMap)

        self.LocateMapIdSeN = Uint32()

        self.DestinationListSeN = SomeIpDynamicSizeArray(AVPCollectedDestination)

        self.MaplistType = Uint8()


class IdtAVPMapListInfo(SomeIpPayload):

    IdtAVPMapListInfo: IdtAVPMapListInfoKls

    def __init__(self):

        self.IdtAVPMapListInfo = IdtAVPMapListInfoKls()
