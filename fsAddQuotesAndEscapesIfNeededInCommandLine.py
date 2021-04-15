import re;

# Command line arguments that contain only alphanumeric chars, underscores and a select set of other chars do not need quotes.
rArgumentThatDoesNotRequireQuotesAndEscapesInCommandLine = re.compile(
  r"^[\w!#\$\+,\-\.\/:=@\[\\\]\{\}~`]+$", 
);

def fsAddQuotesAndEscapesIfNeededInCommandLine(sString):
  # Arguments with spaces and/or special characters will need to be quoted and some
  # special chars need to be 'escaped'. It's not technically escaping but they do need
  # to be replaced with a set of chars to make sure they will be interpretted correctly.
  if rArgumentThatDoesNotRequireQuotesAndEscapesInCommandLine.match(sString):
    return sString;
  return '"%s"' % (sString
    .replace('"', '""') # double up quotes inside quotes to escape them
    .replace('%', '"%"') # move '%' out of the quotes to avoid environment variable expansion.
    .replace('"%""%"', '%') # '%%' was modified to '"%""%"', now turn it back into '%'.
    .replace(r'\\', r'"\\"'), # move '\\' out of the quotes AND double up to avoid it being interpreted as an escape char.
  );
