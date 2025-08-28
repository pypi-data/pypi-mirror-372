from someip_py.codec import *


class IdtSimTrfcData(SomeIpPayload):

    _include_struct_len = True

    SimNo: Uint8

    SimTxbytecount: Uint64

    SimRxbytecount: Uint64

    def __init__(self):

        self.SimNo = Uint8()

        self.SimTxbytecount = Uint64()

        self.SimRxbytecount = Uint64()


class IdtAllTrfcData(SomeIpPayload):

    IdtAllTrfcData: SomeIpDynamicSizeArray[IdtSimTrfcData]

    def __init__(self):

        self.IdtAllTrfcData = SomeIpDynamicSizeArray(IdtSimTrfcData)
