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
        font-size: 12pt;
        font-family: "Courier New", courier, monospace;
      }
      html {
        background: #F0F0F0;
      }
      body {
        margin: auto;
        max-width: 80em;
      }
      table {
        border-spacing: 0;
        border-collapse: collapse;
      }
      ul {
        padding-left: 2em;
      }
      a {
        color: inherit;
        text-decoration: none;
        margin-bottom: -1px;
      }
      :link {
        border-bottom: 1px dotted rgba(0,0, 238, 0.25);
      }
      :link:hover, :link:active {
        border-bottom: 1px solid rgba(0,0, 238, 1);
      }
      :visited {
        border-bottom: 1px dotted rgba(85, 26, 139, 0.25);
      }
      :visited:hover, :visited:active {
        border-bottom: 1px solid rgba(85, 26, 139, 1);
      }
      .Block {
        margin: 1em;
        border: 1px solid rgba(0,0,0, 0.2);
        border-radius: 0.5em;
        background-color: white;
        box-shadow: 1em 1em 1em rgba(0,0,0, 0.05);
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
        color: grey;
      }
      .CDBOrApplicationStdOut {
        color: black;
      }
      .CDBStdErr {
        color: maroon;
      }
      .CDBIgnoredException {
        color: grey;
      }
      .Stack {
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
      .StackSource {
        color: grey;
      }
      .DisassemblyAddress {
        color: grey;
      }
      .DisassemblyOpcode {
        color: grey;
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
</html>
""").strip("\r\n");
