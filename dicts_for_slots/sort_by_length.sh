awk -F, '{print length($1),$1,$2}' $1 | sort -t, -k1,1nr | cut -d' ' -f2,3
#awk  '{print length($1),$1,$2}' $1 | sort -t: -k1,1nr | cut -d' ' -f2
