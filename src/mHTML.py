def fsHTMLEncode(sData):
  return sData.replace('&', '&amp;').replace(" ", "&nbsp;").replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;');

sHTMLDetailsTemplate = ("""
<!doctype html>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <style>
      * {
        border: 0;
        margin: 0;
        padding: 0;
        color: black;
        background: white;
        font-weight: normal;
        font-size: 10pt;
        font-family: "Courier New", courier, monospace;
      }
      table {
        cell-padding: 0;
        cell-spacing: 0;
      }
      .Header {
        color: white;
        background: black;
        padding: 5pt 5pt 5pt 10pt;
        margin: 5pt;
      }
      .SubHeader {
        margin: 10pt 10pt 0pt 15pt;
        border-bottom: 1pt solid black;
      }
      .Content {
        margin: 10pt 10pt 10pt 15pt;
      }
      .SecurityImpact {
        color: Red;
      }
      .CDBStdIn {
        font-weight: bold;
      }
      .CDBStdOut {
      }
      .CDBStdErr {
        color: maroon;
      }
      .CDBIgnoredException {
        color: grey;
      }
      .Stack {
        color: grey;
      }
      .StackIgnored {
        color: silver;
      }
      .StackHash {
        font-weight: bold;
      }
      .StackHashIgnored {
        color: silver;
      }
      .StackNoSymbol {
        font-style: italic;
      }
      .StdIOSeparator {
        border: 1pt groove silver;
        margin: 1pt 5pt 1pt 5pt;
      }
    </style>
    <title>%(sId)s</title>
  </head>
  <body>
    <h1 class="Header">Details</h1>
    <div class="Content">
      """ + fsHTMLEncode("Id:               ") + """<b>%(sId)s</b><br/>
      """ + fsHTMLEncode("Description:      ") + """<b>%(sExceptionDescription)s</b><br/>
      """ + fsHTMLEncode("Process binary:   ") + """%(sProcessBinaryName)s<br/>
      """ + fsHTMLEncode("Code:             ") + """%(sCodeDescription)s<br/>
      """ + fsHTMLEncode("Security impact:  ") + """%(sSecurityImpact)s<br/>
    </div>
    
    <h1 class="Header">Stack</h1>
    <div class="Content">
      %(sStack)s
    </div>
    
    <h1 class="Header">Binary information</h1>
    %(sBinaryInformation)s
    
    <h1 class="Header">Debugger IO</h1>
    <div class="Content">
      %(sCdbStdIO)s
    </div>
  </body>
</html>""").strip();

sHTMLBinaryInformationTemplate = """
    <h2 class="SubHeader">%(sName)s</h2>
    <div class="Content">
      %(sInformation)s
    </div>
""".strip();

