import time

TyStr = str
TyStructTime = time.struct_time


# Date
class StructTime:
    """ Manage Date
    """
    @staticmethod
    def to_string_xls(structtime: TyStructTime) -> TyStr:
        if structtime is None:
            return 'N/A'
        return time.strftime("%b-%y", structtime)
