def fsHTMLEncode(sData):
  return sData.replace('&', '&amp;').replace(" ", "&nbsp;").replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;');

sDetailsHTMLTemplate = ("""
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
      a:link, a:visited {
        text-decoration: none;
      }
      a:hover, a:active {
        text-decoration: underline;
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
      .Important {
        background-color: rgba(255,255,0,0.3);
      }
      .SecurityImpact {
        background-color: rgba(255,0,0,0.2);
      }
      .CDBCommand {
        font-weight: bold;
      }
      .CDBStdOut {
        color: #404040;
      }
      .CDBOrApplicationStdOut {
        color: black;
      }
      .CDBStdErr, a.CDBStdErr {
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
        background: rgba(255,255,0,0.2);
      }
      .StackNoSymbol {
        font-style: italic;
      }
      hr {
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
        <table>
          <tr><td>Id:                     &nbsp;</td><td><span class="Important">%(sId)s</span></td></tr>
          <tr><td>Description:            &nbsp;</td><td><span class="Important">%(sBugDescription)s</span></td></tr>
          <tr><td>Location:               &nbsp;</td><td><span class="Important">%(sBugLocation)s</span></td></tr>
          <tr><td>Security&nbsp;impact:   &nbsp;</td><td>%(sSecurityImpact)s</td></tr>
        </table>
      </div>
    </div>
%(sOptionalBlocks)s
    <div class="Block">
      <h1 class="Header">Debugger IO</h1>
      <div class="Content">
        %(sCdbStdIO)s
      </div>
    </div>
  </body>
</html>""").strip();

sBlockHTMLTemplate = """
    <div class="Block">
      <h1 class="Header">%(sName)s</h1>
      <div class="Content">
        %(sContent)s
      </div>
    </div>
""".lstrip();

