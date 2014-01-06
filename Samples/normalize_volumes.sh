#!/bin/bash
i=0
while ((i <= 300))
do
	b=$(echo "scale=6; $i/100"|bc)
	c=$(echo "scale=6; $b/3"|bc)
	echo "$b => $c"
	((i += 1))
	if [ -f ExcessiveSCSetNormed.tap ]
	then
		echo "Il existe"
		sed -i -e "s/volume=\"$b\"/volume=\"$c\"/g" ExcessiveSCSetNormed.tap
	else
		echo "Il existe pas"
		sed -e "s/volume=\"$b\"/volume=\"$c\"/g" ExcessiveSCSet.tap > ExcessiveSCSetNormed.tap
	fi
done
	
#	sed -e "s/volume=\"3.000000\"/volume=\"\"/g" ExcessiveSCSet.tap > ExcessiveSCSet.tap
