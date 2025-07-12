i=0
j=0
  for file in "$dir"*.jpg "$dir"*.jpeg; do
    [ -e "$file" ] || continue  # Skip if no matching file
    ext="${file##*.}"          # Get original extension
    mv "$file" "${i}_${j}.${ext}"
    j=$((j + 1))
    if [ "$j" -gt 3 ]; then
        i=$(( i + 1 ))
	j=0
    fi
done
