from oConsole import oConsole;

# Colors used in output for various types of information:
NORMAL =            0x0F07; # Light gray
DIM =               0x0F08; # Dark gray
INFO =              0x0F0A; # Bright green
HILITE =            0x0F0F; # Bright white
ERROR =             0x0F04; # Red
ERROR_INFO =        0x0F0C; # Bright red
WARNING =           0x0F06; # Yellow
WARNING_INFO =      0x0F0E; # Bright yellow
UNDERLINE =        0x10000;

oConsole.uDefaultColor = NORMAL;
oConsole.uDefaultBarColor = 0xFF8A; # Light green on Dark gray
oConsole.uDefaultProgressColor = 0xFFA0; # Black on light green
