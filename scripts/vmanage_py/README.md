more template | egrep [a-z]{7}[0-9]rtr[0-9]{3}\-snap | awk '{print $2 " " $8}' | sed '/^\s*$/d'  | sort > list
