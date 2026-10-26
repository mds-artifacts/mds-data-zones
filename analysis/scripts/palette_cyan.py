"""
Palette: the original greys, plus one blue tint taken from the paper's takeaway box
(LaTeX xcolor: colback=cyan!8 = #EBFFFF).

All four figures share exactly these fills:
  cyan!8 (#EBFFFF)  - emphasis: verified zone / verdict, most-used model class, shared approaches
  #D9D9D9           - light grey: partially verified zone, other circles, Style-only and single-approach ring
  #F2F2F2           - very light grey: unverified zone, Knowledge-only slice
  white             - plain boxes and containers
Thin neutral outlines keep the light cyan shapes visible.
"""
BOX_BG = "#EBFFFF"      # cyan!8 - the takeaway box colour (the only colour used)
DARK = BOX_BG           # emphasis: verified zone, verdict, most-used model class, shared approaches
MID = "#D9D9D9"         # original light grey: partially verified zone (dark text)
LIGHT = "#F2F2F2"       # very light grey: unverified zone (dark text)
TEXT_ON = {}            # no fill needs white text
SOFT = MID              # other circles in the approach x model figure (same grey as partially verified)
CONTAINER = "#FFFFFF"   # data-zones container (white)
PLAIN = "#FFFFFF"       # original white: plain boxes
RULE = "#DCDCDC"        # hairline rules
EDGE = "#C4C4C4"        # thin neutral outline
INK = "#111111"         # dark text
WHITE = "#FFFFFF"
