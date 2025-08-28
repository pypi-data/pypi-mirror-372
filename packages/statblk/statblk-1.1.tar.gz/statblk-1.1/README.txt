usage: statblk.py [-h] [-j] [-b] [-H] [-F] [-M] [-B] [--show_zero_size_devices] [-V]

Gather disk and partition info for block devices.

options:
  -h, --help            show this help message and exit
  -j, --json            Produce JSON output
  -b, --bytes           Print the SIZE column in bytes rather than in a human-readable format
  -H, --si              Use powers of 1000 not 1024 for SIZE column
  -F, -fo, --formated_only
                        Show only formated filesystems
  -M, -mo, --mounted_only
                        Show only mounted filesystems
  -B, -bo, --best_only  Show only best mount for each device
  --show_zero_size_devices
                        Show devices with zero size
  -V, --version         show program's version number and exit


Install:
sudo pip install statblk