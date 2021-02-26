
export taggables="./00_z-jay"
export needtags="./01_noID3tag"
export replacetags="./02_id3v2"

# To use the sort, did not use  -exec id3v2 -l "{}" +
#find /media/pi/ZUKE/MUSIC/ -type f -exec id3v2 -l "{}" + > "$taggables.txt"
find /media/pi/ZUKE/MUSIC/ -type f  | sort > "$taggables.txt"

echo Execute this block if "$taggables.txt" exists and empty
if [ -s "$taggables.txt" ]; then
  echo Now sed the 00_z-jay.txt, so they are  id3v2 -l "{}"
  sed "s/^\(.\+\)$/id3v2 -l \"\1\"/"  "$taggables.txt" > "$taggables.sh"
#  if [ -e "$taggables.sh" ]; then 
#    sh "$taggables.sh" | grep -i "no id3 tag" > "$needtags.txt"
#  fi
fi

if [ -s "$needtags.txt" ]; then
  sed -i "s/: no id3 tag//i" "$needtags.txt"
  echo Assume id3v2 -a \"Zumba Fitness\"  -A ALBUM -t SONG TITLE 
  echo -T TRACK ##/##\(\<-optional\)
  echo -g GENRE \(\<-optional\)
  echo Define ome tag and prepare for some tags
  sed -i '1 i\export ARTIST="Zumba Fitness"' "$needtags.txt"
  sed -i '2 i\export ALBUM=""' "$needtags.txt"
  sed -i '4 i\export TNUM=""' "$needtags.txt"
  sed -i "s|^\(.\+\w\{2\} \([0-9]\{2\}\)/\([0-9]\+\) \- \(.\+\)\..\+\)$|id3v2 -a \"\$ARTIST\" -A \"\$ALBUM \2\" -T \"\3/\$TNUM\" -t \"\4\" \"\1\"|" "$needtags.txt" 
  echo ... Process halts right here for a moment ... Check $needtags.txt
  echo When finalized: mv -i $needtags.txt $needtags.sh
  echo Then run,  $needtags.sh
  echo Afterwards, run  $0  again.
  exit
else
  rm "$needtags.txt"
fi

echo All the mp3s should have tags.

if [ -e "$taggables.sh" ]; then
#  sh "$taggables.sh"  > "$replacetags.old.txt"
  #cp -i "$replacetags.old.txt" "$replacetags.new.json" 
  cp  "$replacetags.old.txt" "$replacetags.new.json" 
fi

echo Editing  $replacetags.new.json  so id3v2 tags are JSON-parsable
echo Ignore all id3v1 tags \(may ignore TPE2 too\)
sed -i '/^Title/d' $replacetags.new.json
sed -i '/^Album/d' $replacetags.new.json
sed -i '/^Comment/d' $replacetags.new.json
echo Ignore '^id3v1' line, 'No ID3v1 tag$' line
sed -i '/^id3v1 tag info for.*$/d' $replacetags.new.json
sed -i '/^.*No ID3v1 tag$/d' $replacetags.new.json
echo Ignore '^TXXX' line, '^COMM' line
sed -i '/^TXXX.*$/d' $replacetags.new.json
sed -i '/^COMM.*$/d' $replacetags.new.json

echo Purge empty lines
sed -i '/^$/d' $replacetags.new.json
echo Escape characters
sed -i 's/"/\\"/g' $replacetags.new.json
echo Create key for each DICT
sed -ri '1   s/^id3v2 tag info for\s*(.+)\s*:\s*$/    "\1":{/' $replacetags.new.json
sed -ri '2,$ s/^id3v2 tag info for\s*(.+)\s*:\s*$/  },"\1":{/' $replacetags.new.json
sed -ri 's/^(\w{4})\s*\(.+\)\s*:\s*(.+)$/    "\1" : "\2",/' $replacetags.new.json
echo Purge GENRE numbers
sed -ri 's/\s*\([[:digit:]]+\)\s*//g' $replacetags.new.json
echo Capture TPE1, TALB, TRCK, TIT2, TCON
echo Capture TCOM, may add TCOM=Zumba Fitness
echo Capture TPOS, may add TPOS=1/1
echo Capture TYER, preserve
sed -i '$ a\  }' $replacetags.new.json
perl -i -0pe 's/,(\n\s+\})/\1/g' $replacetags.new.json
sed -i '1 i\{' $replacetags.new.json 
sed -i '$ a\}' $replacetags.new.json

python -c 'import json;J=json.load(open("$replacetags.new.json"));print str(len(J))+" records";'

python -c 'import json;J=json.load(open("$replacetags.new.json"));for j in J: print j;'

