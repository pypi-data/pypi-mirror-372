#!/bin/bash

TARGET=../static/style/

for file in design/*.xcf; do
    name=$( basename $file .xcf )
    png="design/$name.png"
    if [ $file -nt $png ]; then
	echo "$file -> $png"
	xcf2png $file > $png
    fi
    target=$TARGET
    # if [ "$name" = "add" -o "$name" = "remove" ]; then
    # 	target=static/images/
    # fi
    
    out=$target$name.png
    if [ $png -nt $out ] ; then
	echo "$png -> $out"
	convert -resize 20x20 $png $out
    fi
done

