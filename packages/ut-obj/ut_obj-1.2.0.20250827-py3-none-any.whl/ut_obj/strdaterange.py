from typing import Annotated

from ut_log.log import LogEq
from ut_obj.strdate import StrDate

TyAo2S = Annotated[list[str], 2]
TyStr = str


# class DateRange:
class StrDateRange:
    """
    Manage Date Range (Date Interval)
    """
    @staticmethod
    def sh_arr(strdaterange: TyStr) -> TyAo2S:
        """
        Show array of two date strings
        """
        _ao2s: TyAo2S = strdaterange.split('–')
        match len(_ao2s):
            case 0:
                _ao2s = ['', '']
            case 1:
                _ao2s.append('')
        LogEq.debug("_ao2s", _ao2s)
        return _ao2s

    @classmethod
    def sh_begin(cls, strdaterange: TyStr) -> TyStr:
        """
        Show begin date of date string
        """
        _ao2s: TyAo2S = cls.sh_arr(strdaterange)
        _strdate: TyStr = StrDate.sh_date(_ao2s[0])
        return _strdate

    @classmethod
    def sh_end(cls, strdaterange: TyStr) -> TyStr:
        """
        Show end date of date string
        """
        _ao2s: TyAo2S = cls.sh_arr(strdaterange)
        _strdate: TyStr = StrDate.sh_date(_ao2s[1])
        return _strdate

    @staticmethod
    def sh_dic(strdaterange):
        """
        Show dictioinary of begin and end data strings
        """
        _dic = {}
        _ao2s = strdaterange.split('–')
        match len(_ao2s):
            case 0:
                _dic['start_date'] = ''
                _dic['end_date'] = ''
            case 1:
                _dic['start_date'] = _ao2s[0].strip()
                _dic['end_date'] = ''
            case _:
                _dic['start_date'] = _ao2s[0].strip()
                _dic['end_date'] = _ao2s[1].strip()
        LogEq.debug("_dic", _dic)
        return _dic
