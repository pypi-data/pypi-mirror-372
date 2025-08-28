from someip_py.codec import Int32, SomeIpPayload


class VehiclePoint(SomeIpPayload):
    PositionXSeN: Int32
    PositionYSeN: Int32

    def __init__(self):
        self.PositionXSeN = Int32(0)
        self.PositionYSeN = Int32(0)
