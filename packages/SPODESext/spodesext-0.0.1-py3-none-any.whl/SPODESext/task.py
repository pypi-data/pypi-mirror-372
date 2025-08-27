from dataclasses import dataclass
from DLMS_SPODES.pardata import ParValues
from StructResult import result
from DLMS_SPODES_client.client import Client
from DLMS_SPODES_client import task
from . import parameters as par


@dataclass
class CloseSeal(task.OK):
    msg: str = "Обжатие пломбы"

    async def exchange(self, c: Client) -> result.Ok | result.Error:
        if isinstance((res := await task.WriteParValue(
            ParValues(par.CLOSE_ELECTRIC_SEAL.VALUE, "0"),
            msg="Запись пломбы").exchange(c)
        ), result.Error):
            return res
        return result.OK
