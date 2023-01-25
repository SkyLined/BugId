# COMMONLY USED COLOR NAMES
COLOR_DIM                               = 0x0F08; # Dark gray
COLOR_NORMAL                            = 0x0F07; # Light gray
COLOR_HILITE                            = 0x0F0F; # White

COLOR_INFO                              = 0x0F0A; # Bright green
COLOR_LIST                              = 0x0F0A; # Bright green

COLOR_BUSY                              = 0x0F03; # Cyan
COLOR_OK                                = 0x0F02; # Green
COLOR_WARNING                           = 0x0F06; # Brown
COLOR_ERROR                             = 0x0F04; # Red

COLOR_SELECT_YES                        = 0x0F0A; # Bright green
COLOR_SELECT_MAYBE                      = 0x0F02; # Dark green
COLOR_SELECT_NO                         = 0x0F02; # Dark green

COLOR_INPUT                             = 0x0F0B; #
COLOR_OUTPUT                            = 0x0F07; #

COLOR_ADD                               = 0x0F0A; # Bright green
COLOR_MODIFY                            = 0x0F0B; # Bright cyan
COLOR_REMOVE                            = 0x0F0C; # Bright red

COLOR_PROGRESS_BAR                      = 0xFF82; # Dark green on Dark gray
COLOR_PROGRESS_BAR_HILITE               = 0xFF28; # Dark grey on dark green
COLOR_PROGRESS_BAR_SUBPROGRESS          = 0xFFA0; # Black on bright green

CONSOLE_UNDERLINE                       = 0x10000;

# COMMONLY USED CHARS
CHAR_INFO                               = "→";
CHAR_LIST                               = "•";

CHAR_BUSY                               = "»";
CHAR_OK                                 = "√";
CHAR_WARNING                            = "▲";
CHAR_ERROR                              = "×";

CHAR_SELECT_YES                         = "●";
CHAR_SELECT_MAYBE                       = "•";
CHAR_SELECT_NO                          = "·";

CHAR_INPUT                              = "◄";
CHAR_OUTPUT                             = "►";

CHAR_ADD                                = "+";
CHAR_MODIFY                             = "±";
CHAR_REMOVE                             = "-";
CHAR_IGNORE                             = "·";

# DEFAULTS
from foConsoleLoader import foConsoleLoader;
oConsole = foConsoleLoader();
oConsole.uDefaultColor = COLOR_NORMAL;
oConsole.uDefaultBarColor = COLOR_PROGRESS_BAR;
oConsole.uDefaultProgressColor = COLOR_PROGRESS_BAR_HILITE;
oConsole.uDefaultSubProgressColor = COLOR_PROGRESS_BAR_SUBPROGRESS;

