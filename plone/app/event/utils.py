def n2rn(s):
    """ Replace unix line endings with dos line endings """
    return s.replace('\n', '\r\n')


def vformat(s):
    """ return string with escaped commas, colons and semicolons """
    return s.strip().replace(',', '\,').replace(':', '\:').replace(';', '\;')


def rfc2445dt(dt):
    """ UTC in RFC2445 format YYYYMMDDTHHMMSSZ for a DateTime object """
    return dt.HTML4().replace('-', '').replace(':', '')


def foldline(s, lineLen=70):
    """ make a string folded per RFC2445 (each line must be less than 75 octets)
    This code is a minor modification of MakeICS.py, available at:
    http://www.zope.org/Members/Feneric/MakeICS/
    """
    workStr = s.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\\n')
    workStr = workStr.strip()
    numLinesToBeProcessed = len(workStr) / lineLen
    startingChar = 0
    res = ''
    while numLinesToBeProcessed >= 1:
        res = '%s%s\n ' % (res, workStr[startingChar:startingChar + lineLen])
        startingChar += lineLen
        numLinesToBeProcessed -= 1
    return '%s%s\n' % (res, workStr[startingChar:])

