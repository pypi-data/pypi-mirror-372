
class GermanUmlaute:
    """ how to convert german special characters from unicode
        to utf-8 and back to unicode
    """
    d_umlaute = {
        '\xc3\xa4': 'ae',  # U+00E4    \xc3\xa4
        '\xc3\xb6': 'oe',  # U+00F6    \xc3\xb6
        '\xc3\xbc': 'ue',  # U+00FC    \xc3\xbc
        '\xc3\x84': 'Ae',  # U+00C4    \xc3\x84
        '\xc3\x96': 'Oe',  # U+00D6    \xc3\x96
        '\xc3\x9c': 'Ue',  # U+00DC    \xc3\x9c
        '\xc3\x9f': 'ss',  # U+00DF    \xc3\x9f
    }

    @classmethod
    def replace(cls, s_unicode):

        for key, value in cls.d_umlaute.items():
            s_utf8 = s_unicode.encode('utf-8').replace(key, value)

        return s_utf8.decode()
