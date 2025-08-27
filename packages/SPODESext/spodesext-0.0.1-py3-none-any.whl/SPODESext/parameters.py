from DLMS_SPODES.cosem_interface_classes import parameters as prs
from DLMS_SPODES.cosem_interface_classes.parameter import Parameter


CLOSE_ELECTRIC_SEAL = prs.Data(Parameter.parse("0.0.96.51.6.255"))
DEVICE_TYPE = prs.Data(Parameter.parse("0.0.96.1.1.255"))
