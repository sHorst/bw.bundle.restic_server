#!/bin/sh

folder=$1

last_file=$(ls -tr $folder/index | tail -n 1)
ftime=$(stat -c %Y $folder/index/$last_file)
ctime=$(date +%s)
diff=$(( ctime - ftime ))
diff_days=$(( diff / 86400 ))

count_index=$(ls -tr $folder/index | wc -l)
count_locks=$(ls -tr $folder/locks | wc -l)
count_keys=$(ls -tr $folder/keys | wc -l)
count_snapshots=$(ls -tr $folder/snapshots | wc -l)

# 172800s == 2d; 604800s == 7d
echo "P restic_last_backup age=$diff;172800;604800 The last Restic Backup was $diff_days Days ago"
echo "P restic_count index=$count_index|locks=$count_locks;2;5|keys=$count_keys|snapshots=$count_snapshots The Restic Backup contains $count_index Index Files, $count_locks Locks, $count_keys Keys and $count_snapshots Snapshots"
