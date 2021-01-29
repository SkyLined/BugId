from ddxAdobeAcrobatReaderSettings_by_sKeyword import ddxAdobeAcrobatReaderSettings_by_sKeyword;
from ddxAdobeAcrobatReaderDCSettings_by_sKeyword import ddxAdobeAcrobatReaderDCSettings_by_sKeyword;
from ddxFoxitReaderSettings_by_sKeyword import ddxFoxitReaderSettings_by_sKeyword;
from ddxGoogleChromeSettings_by_sKeyword import ddxGoogleChromeSettings_by_sKeyword;
from ddxMicrosoftEdgeSettings_by_sKeyword import ddxMicrosoftEdgeSettings_by_sKeyword;
from ddxMozillaFirefoxSettings_by_sKeyword import ddxMozillaFirefoxSettings_by_sKeyword;
from ddxOracleJavaSettings_by_sKeyword import ddxOracleJavaSettings_by_sKeyword;
from ddxMicrosoftInternetExplorerSettings_by_sKeyword import ddxMicrosoftInternetExplorerSettings_by_sKeyword;
ddxApplicationSettings_by_sKeyword = {};
# There may be multiple keywords for a single application (e.g. ISA specific keywords).
for ddxApplicationSpecificSettings_by_sKeyword in [
  ddxAdobeAcrobatReaderSettings_by_sKeyword,
  ddxAdobeAcrobatReaderDCSettings_by_sKeyword,
  ddxFoxitReaderSettings_by_sKeyword,
  ddxGoogleChromeSettings_by_sKeyword,
  ddxMicrosoftEdgeSettings_by_sKeyword,
  ddxMozillaFirefoxSettings_by_sKeyword,
  ddxOracleJavaSettings_by_sKeyword,
  ddxMicrosoftInternetExplorerSettings_by_sKeyword,
]:
  for (sKeyword, dxSettings) in ddxApplicationSpecificSettings_by_sKeyword.items():
    # There cannot be multiple settings for a keyword.
    assert sKeyword not in ddxApplicationSettings_by_sKeyword, \
        "You cannot defined settings for keyword %s twice!" % sKeyword;
    ddxApplicationSettings_by_sKeyword[sKeyword] = dxSettings;

__all__ = [
  "ddxApplicationSettings_by_sKeyword",
];

