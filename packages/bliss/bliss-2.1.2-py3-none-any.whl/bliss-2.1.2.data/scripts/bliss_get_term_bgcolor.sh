#!/usr/bin/env bash
#
# query terminal to get current background color
#

if [ -z "$COLORFGBG" ]; then
  stty -echo
  echo -ne '\e]10;?\a\e]11;?\a'
  IFS=: read -t 1 -d $'\a' x fg
  IFS=: read -t 1 -d $'\a' x bg
  stty echo
  RGB=(${bg//// }) # replace / with space then split in RGB array
  r=$((16#${RGB[0]} % 256))
  g=$((16#${RGB[1]} % 256))
  b=$((16#${RGB[2]} % 256))
  y=$((($r+$r+$r+$b+$g+$g+$g+$g)>>3)) # calculate luminance
  if [ $y -lt 127 ]; then
	  echo "15;0" >&2 # mimic value of COLORFGBG for "dark"
  else
	  echo "0;15" >&2
  fi
  unset x fg bg r g b y
else
  echo $COLORFGBG >&2
fi

