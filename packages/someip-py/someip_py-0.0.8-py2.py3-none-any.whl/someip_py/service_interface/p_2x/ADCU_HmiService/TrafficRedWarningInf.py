from someip_py.codec import *


class VehiclePoint(SomeIpPayload):

    PositionXSeN: Int32

    PositionYSeN: Int32

    def __init__(self):

        self.PositionXSeN = Int32()

        self.PositionYSeN = Int32()


class TrafficRedWarningSeN(SomeIpPayload):

    TrafficRedWarningID: Uint64

    TrafficRedWarningPointSeN: VehiclePoint

    def __init__(self):

        self.TrafficRedWarningID = Uint64()

        self.TrafficRedWarningPointSeN = VehiclePoint()


class TrafficRedWarningInfo(SomeIpPayload):

    TrafficRedWarningInfo: SomeIpDynamicSizeArray[TrafficRedWarningSeN]

    def __init__(self):

        self.TrafficRedWarningInfo = SomeIpDynamicSizeArray(TrafficRedWarningSeN)
