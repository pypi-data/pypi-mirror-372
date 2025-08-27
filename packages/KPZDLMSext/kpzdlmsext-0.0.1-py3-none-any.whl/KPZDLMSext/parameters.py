from DLMS_SPODES.cosem_interface_classes.parameter import Parameter
from DLMS_SPODES.cosem_interface_classes import parameters as prs


CALIBRATE = prs.Register(Parameter.parse("128.0.0.0.0.255"))
AFE_OFFSETS = prs.Data(Parameter.parse("0.128.96.2.2.255"))
