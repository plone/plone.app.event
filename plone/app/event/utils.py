def n2rn(s):
    """ Replace unix line endings with dos line endings """
    return s.replace('\n', '\r\n')

def vformat(s):
    """ return string with escaped commas, colons and semicolons """
    return s.strip().replace(',','\,').replace(':','\:').replace(';','\;')

def rfc2445dt(dt):
    """ UTC in RFC2445 format YYYYMMDDTHHMMSSZ for a DateTime object """
    return dt.HTML4().replace('-','').replace(':','')

