from datetime import date, datetime

TyDate = date
TyDateTime = datetime
TyStr = str

TnDate = None | TyDate
TnStr = None | str


# class Date:
class StrDate:

    @staticmethod
    def sh(strdate: TnStr, fmt: TyStr) -> TnDate:
        if not strdate:
            return None
        _datetime: TyDateTime = datetime.strptime(strdate, fmt)
        _date: TyDate = _datetime.date()
        return _date

    @staticmethod
    def is_year(year: TyStr) -> bool:
        if year and year.isdigit():
            year_ = int(year)
            if year_ >= 1900 and year_ <= 9999:
                return True
        return False

    @classmethod
    def sh_date(cls, strdate: TnStr) -> TnStr:
        if not strdate:
            return None
        strdate = strdate.strip()
        if strdate.lower() == 'present':
            return strdate
        if cls.is_year(strdate):
            _strdate: TnStr = datetime.strptime(strdate, '%Y').strftime('%Y')
            return _strdate
        try:
            _strdate = datetime.strptime(strdate, '%m %Y').strftime('%Y-%m')
            return _strdate
        except BaseException:
            try:
                _strdate = datetime.strptime(strdate, '%d %m %Y').strftime('%Y-%m-%d')
                return _strdate
            except BaseException:
                return strdate
        return strdate
