def fsCreateFileName(sBase):
  dsMap = {'"': "''", "<": "[", ">": "]", "\\": "#", "/": "#", "?": "#", "*": "#", ":": ".", "|": "#"};
  return "".join([dsMap.get(sChar, sChar) for sChar in sBase]);
