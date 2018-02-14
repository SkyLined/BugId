from dxConfig import dxConfig;
from oConsole import oConsole;

asBugIdLogo = [s.rstrip() for s in """
                          __                     _____________                  
                    _,siSP**YSis,_        ,-~-._/             |                 
                  ,SP*'`    . `'*YS,     |     |`-O    BugId  |                 
                 dS'  _    |    _ 'Sb   ,'      \_____________|   ,,,           
    ,,,         dP     \,-` `-<` `  Y; _&/                       :O()           
   :O()        ,S`  \+' \      \    `Sis|ssssssssssssssssss,      ```    ,,,    
    ```  ,,,   (S   (   | --====)    SSS|SSSSSSSSSSSSSSSSSSD             ()O:   
        :O()   'S,  /+, /      /    ,S?*/******************'             ```    
         ```    Yb    _/'-_ _-<._.  dP `                                        
  ______________ YS,       |      ,SP ________________________________________  
                  `Sbs,_    ' _,sdS`                                            
                    `'*YSissiSY*'`                   https://bugid.skylined.nl  
                          ``                                                    """.split("""
""")];

# We can now add color to console output, so let's create a second version of
# the above logo, but with color information (" " = default terminal color, hex
# digit = color number.
asBugIdLogoColors = [s.rstrip() for s in """
                          77                     AAAAAAAAAAAAA                  
                    77777777777777        AAAAAAA             A                 
                  777888    8 888877     A     AAAA    AAAAA  A                 
                 788  8    8    8 887   AA      AAAAAAAAAAAAAAA   888           
    888         78     8CCC CCC8 8  87 AAA                       7CCC           
   7CCC        788  87C 4      C    8877A7777777777777777777      888    888    
    888  888   78   C   4 444444C    888A8888888888888888888             CCC7   
        7CCC   888  87C 4      C    8888A8888888888888888888             888    
         888    88    88CCC CCC888  88 A                                        
  87777777777778 887       8      788 8777777777777777777777777777777777777778  
                  887777    8 777788                                            
                    88877777777888                   AAAAAAAAAAAAAAAAAAAAAAAAA  
                          88                                                    """.split("""
""")];

BORDER = 0x04;
TEXT = 0x0C;
HILITE = 0x0F;
aasLicenseAndDonationInfoPrintArguments = [
  [" ", BORDER, u"\u250C", u"\u2500" * 76, u"\u2510"],
  [" ", BORDER, u"\u2502 ", TEXT, " This version of BugId is provided free of charge for non-commercial use  ", BORDER, u" \u2502"],
  [" ", BORDER, u"\u2502 ", TEXT, "  only. If you find it useful and would like to make a donation, you can  ", BORDER, u" \u2502"],
  [" ", BORDER, u"\u2502 ", TEXT, "           send bitcoin to ", HILITE, "183yyxa9s1s1f7JBpPHPmzQ346y91Rx5DX", TEXT, ".            ", BORDER, u" \u2502"],
  [" ", BORDER, u"\u2502 ", TEXT, "    If you wish to use BugId commercially, please contact the author to   ", BORDER, u" \u2502"],
  [" ", BORDER, u"\u2502 ", TEXT, "    request a quote. Contact and licensing information can be found at:   ", BORDER, u" \u2502"],
  [" ", BORDER, u"\u2502 ", TEXT, "                ", HILITE, "https://github.com/SkyLined/BugId#license", TEXT, ".                ", BORDER, u" \u2502"],
  [" ", BORDER, u"\u2514", u"\u2500" * 76, u"\u2518"],
];

def fPrintLogo():
  # We will use the above ASCII and color data to create a list of arguments
  # that can be passed to oConsole.fPrint in order to output the logo in color:
  oConsole.fLock();
  try:
    for uLineIndex in xrange(len(asBugIdLogo)):
      iLastColor = -1;
      asBugIdLogoPrintArguments = [""];
      sCharsLine = asBugIdLogo[uLineIndex];
      sColorsLine = asBugIdLogoColors[uLineIndex];
      for uColumnIndex in xrange(len(sCharsLine)):
        sColor = sColorsLine[uColumnIndex];
        iColor = sColor == " " and -1 or int("F0" + sColor, 16);
        if iColor != iLastColor:
          asBugIdLogoPrintArguments.extend([iColor, ""]);
          iColor = iLastColor;
        sChar = sCharsLine[uColumnIndex];
        asBugIdLogoPrintArguments[-1] += sChar;
      oConsole.fPrint(*asBugIdLogoPrintArguments);
    if dxConfig["bShowLicenseAndDonationInfo"]:
      oConsole.fPrint();
      for asLicenseAndDonationInfoPrintArguments in aasLicenseAndDonationInfoPrintArguments:
        oConsole.fPrint(*asLicenseAndDonationInfoPrintArguments);
      oConsole.fPrint();
  finally:
    oConsole.fUnlock();
