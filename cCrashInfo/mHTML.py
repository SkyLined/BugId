sHTMLDetailsTemplate = """
<!doctype html>
<html>
  <head>
    <style>
      * {
        font-family: Courier New, courier, monospace;
      }
      body {
        margin: 5pt;
      }
      div {
        color: white;
        background: black;
        padding: 5pt;
        padding-left: 10pt;
        margin-top: 10pt;
        margin-bottom: 10pt;
      }
      code {
        margin-left: 10pt;
        display: block;
      }
      table, tbody, tr, td {
        cell-padding: 0;
        cell-spacing: 0;
        border: 0;
        padding: 0;
        margin: 0;
      }
      s {
        color: silver;
        text-decoration: line-through;
      }
    </style>
    <title>%(sId)s</title>
  </head>
  <body>
    <div>Details</div>
    <code>
      <table>
        <tbody>
          <tr><td>Id:               </td><td><b>%(sId)s</b></td></tr>
          <tr><td>Description:      </td><td><b>%(sExceptionDescription)s</b></td></tr>
          <tr><td>Process binary:   </td><td>%(sProcessBinaryName)s</td></tr>
          <tr><td>Location:         </td><td>%(sLocationDescription)s</td></tr>
          <tr><td>Security impact:  </td><td>%(sSecurityImpact)s</td></tr>
        </table>
      </tbody>
    </code>
    <div>Stack</div>
    <code>%(sStack)s</code>
    %(sAdditionalInformation)s
    <div>Debugger input/output</div>
    <code>%(sCdbIO)s</code>
  </body>
</html>""".strip();

sHTMLAdditionalInformationTemplate = """
    <div>%(sName)s</div>
    <code>%(sDetails)s</code>
""".strip();

def fsHTMLEncode(sData):
  return sData.replace('&', '&amp;').replace(" ", "&nbsp;").replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;');
