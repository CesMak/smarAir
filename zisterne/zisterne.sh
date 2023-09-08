range=$(curl -s http://192.168.178.139/cm?cmnd=STATUS+8 | jq '.StatusSNS.ANALOG.Range')
date=$(curl -s http://192.168.178.139/cm?cmnd=STATUS+8 | jq -r '.StatusSNS.Time')
level=$(printf %.0f "$((range*1436782))e-6")
liter=$(printf %.2f "$((level*314159*125*125))e-9")
perc=$(printf %.2f "$((level*314159*125*125*75472))e-16") # 100% = 13.25m3
echo "Modell                  : Trifix Total "
echo "Date                    : $date "
echo "Tasmota range           : $range "
echo "Water level             : $level mm"
echo "Water(l) level*pi*1.25^2: $liter l"
echo "Percentage %            : $perc  %"
result="$date   $range  $level  $liter  $perc"

# Define the filename
filename='/home/pitwo/zisterne/zisterne.txt'

# Check the new text is empty or not
if [ "$range" != "" ]; then
      # Append the text by using '>>' symbol
      echo $result >> $filename
fi