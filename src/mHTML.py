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
        background: transparent;
        font-weight: normal;
        font-size: 10pt;
        font-family: "Courier New", courier, monospace;
      }
      html {
        background: silver;
      }
      table {
        cell-padding: 0;
        cell-spacing: 0;
      }
      .Block {
        margin: 10pt;
        border-radius: 0 0 30pt 5pt;
        border: 1pt solid black;
        background: white;
        box-shadow: 5pt 5pt 5pt grey;
      }
      .Header {
        padding: 5pt 10pt 5pt 10pt;
        color: white;
        background: black;
      }
      .SubHeader {
        margin: 0 0 5pt 0;
        border-bottom: 1pt solid black;
      }
      .Content {
        padding: 5pt 10pt 5pt 10pt;
        border-radius: 0 0 30pt 5pt;
      }
      .SubContent {
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
      .StackNoSymbol {
        font-style: italic;
      }
      .StdIOSeparator {
        border: dotted black;
        border-width: 0 0 1pt 0;
      }
    </style>
    <title>%(sId)s</title>
  </head>
  <body>
    <div class="Block">
      <h1 class="Header">Details</h1>
      <div class="Content">
        """ + fsHTMLEncode("Id:               ") + """<b>%(sId)s</b><br/>
        """ + fsHTMLEncode("Description:      ") + """<b>%(sExceptionDescription)s</b><br/>
        """ + fsHTMLEncode("Process binary:   ") + """%(sProcessBinaryName)s<br/>
        """ + fsHTMLEncode("Code:             ") + """%(sCodeDescription)s<br/>
        """ + fsHTMLEncode("Security impact:  ") + """%(sSecurityImpact)s<br/>
      </div>
    </div>
    
    <div class="Block">
      <h1 class="Header">Stack</h1>
      <div class="Content">
        %(sStack)s
      </div>
    </div>
    
    <div class="Block">
      <h1 class="Header">Binary information</h1>
      <div class="Content">
        %(sBinaryInformation)s
      </div>
    </div>
    
    <div class="Block">
      <h1 class="Header">Debugger IO</h1>
      <div class="Content">
        %(sCdbStdIO)s
      </div>
    </div>
  </body>
</html>""").strip();

sHTMLBinaryInformationTemplate = """
    <h2 class="SubHeader">%(sName)s</h2>
    <div class="SubContent">
      %(sInformation)s
    </div>
""".strip();

