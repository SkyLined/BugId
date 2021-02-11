dsInvalidPathCharacterAsciiTranslationMap = {
  # Translates characters that are not valid in file/folder names to a visually similar unicode character.
  u'"':   u"''",     # Double APOSTROPHY
  u"<":   u"[",      # LEFT SQUARE BRACKET
  u">":   u"]",      # RIGHT SQUARE BRACKET
  u"\\":  u" ",      # SPACE
  u"/":   u" ",      # SPACE
  u"?":   u"!",      # EXCLAMATION MARK
  u"*":   u"x",      # LATIN SMALL LETTER X
  u":":   u".",      # FULL STOP
  u"|":   u"!",      # EXCLAMATION MARK
};
dsInvalidPathCharacterUnicodeTranslationMap = {
  # Translates characters that are not valid in file/folder names to a visually similar unicode character.
  u'"':   u"\u2033", # DOUBLE PRIME
  u"<":   u"\u3008", # LEFT ANGLE BRACKET
  u">":   u"\u3009", # RIGHT ANGLE BRACKET
  u"\\":  u"\u29F9", # BIG REVERSE SOLIDUS
  u"/":   u"\u29F8", # BIG SOLIDUS
  u"?":   u"\u2753", # BLACK QUESTION MARK ORNAMENT
  u"*":   u"\u204E", # LOWER ASTERISK
  u":":   u"\u0589", # ARMENIAN FULL STOP
  u"|":   u"\u01C0", # LATIN LETTER DENTAL CLICK
};
for uCharCode in xrange(0, 0x20):
  # Translate control codes
  dsInvalidPathCharacterAsciiTranslationMap[unichr(uCharCode)] = u"."; # FULL STOP
  dsInvalidPathCharacterUnicodeTranslationMap[unichr(uCharCode)] = u"\uFFFD"; # REPLACEMENT CHARACTER

def fsGetValidName(sName, bUnicode = True):
  dsInvalidPathCharacterTranslationMap = dsInvalidPathCharacterUnicodeTranslationMap if bUnicode else \
                                         dsInvalidPathCharacterAsciiTranslationMap;
  return u"".join([
    (bUnicode or ord(sChar) < 0x100) and dsInvalidPathCharacterTranslationMap.get(sChar, sChar) or "."
    for sChar in unicode(sName)
  ]);
