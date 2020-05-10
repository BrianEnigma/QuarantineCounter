#!/bin/bash

cd img

for f in digits-large-*.png ; do
	out=`echo $f | sed s/large/small/`
	convert $f -resize 30x45 $out
done

for f in *.png ; do
	out=`echo $f | sed s/png$/bmp/`
	convert $f -type truecolor ../bmp/$out
done

cd ..