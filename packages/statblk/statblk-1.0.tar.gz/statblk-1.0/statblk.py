#!/usr/bin/env python3
# requires-python = ">=3.6"
# -*- coding: utf-8 -*-



import os
import re
import stat
from collections import defaultdict
import argparse
import shutil
import subprocess

version = '1.0'
VERSION = version
__version__ = version
COMMIT_DATE = '2025-08-26'


SMARTCTL_PATH = shutil.which("smartctl")

def read_text(path):
	try:
		with open(path, "r", encoding="utf-8", errors="ignore") as f:
			return f.read().strip()
	except Exception:
		return None


def read_int(path):
	s = read_text(path)
	if s is None:
		return None
	try:
		return int(s)
	except Exception:
		return None


def build_symlink_map(dir_path):
	"""
	Build map: devname -> token (uuid or label string) using symlinks under
	/dev/disk/by-uuid or /dev/disk/by-label.
	"""
	mapping = {}
	if not os.path.isdir(dir_path):
		return mapping
	try:
		for entry in os.listdir(dir_path):
			p = os.path.join(dir_path, entry)
			try:
				if os.path.islink(p):
					tgt = os.path.realpath(p)
					devname = os.path.basename(tgt)
					mapping.setdefault(devname, entry)
			except Exception:
				continue
	except Exception:
		pass
	return mapping


def parse_mountinfo_enhanced(uuid_rev, label_rev):
	"""
	Parse /proc/self/mountinfo.

	Returns:
	- by_majmin: dict "major:minor" -> list of mounts
	- by_devname: dict devname -> list of mounts (resolved from source)
	- all_mounts: list of mount dicts

	Each mount dict: {mountpoint, fstype, source, majmin}
	"""
	by_majmin = defaultdict(list)
	by_devname = defaultdict(list)
	all_mounts = []

	def resolve_source_to_devnames(src):
		# Returns list of candidate devnames for a given source string
		if not src:
			return []
		cands = []
		try:
			if src.startswith("/dev/"):
				real = os.path.realpath(src)
				dn = os.path.basename(real)
				if dn:
					cands.append(dn)
			elif src.startswith("UUID="):
				u = src[5:]
				dn = uuid_rev.get(u)
				if dn:
					cands.append(dn)
			elif src.startswith("LABEL="):
				l = src[6:]
				dn = label_rev.get(l)
				if dn:
					cands.append(dn)
		except Exception:
			pass
		return cands

	try:
		with open("/proc/self/mountinfo", "r", encoding="utf-8") as f:
			for line in f:
				line = line.strip()
				if not line:
					continue
				parts = line.split()
				try:
					majmin = parts[2]
					mnt_point = parts[4]
					dash_idx = parts.index("-")
					fstype = parts[dash_idx + 1]
					source = parts[dash_idx + 2] if len(parts) > dash_idx + 2 else ""
					rec = {
						"MOUNTPOINT": mnt_point,
						"FSTYPE": fstype,
						"SOURCE": source,
						"MAJMIN": majmin,
					}
					all_mounts.append(rec)
					by_majmin[majmin].append(rec)
					# Build secondary index by devname from source
					for dn in resolve_source_to_devnames(source):
						by_devname[dn].append(rec)
				except Exception:
					continue
	except Exception:
		pass

	return by_majmin, by_devname, all_mounts


def get_statvfs_use_percent(mountpoint):
	try:
		st = os.statvfs(mountpoint)
		if st.f_blocks == 0:
			return None
		used_pct = 100.0 * (1.0 - (st.f_bavail / float(st.f_blocks)))
		return int(round(used_pct))
	except Exception:
		return None


def read_discard_support(sys_block_path):
	if not sys_block_path or not os.path.isdir(sys_block_path):
		return False
	dmbytes = read_int(os.path.join(sys_block_path, "queue", "discard_max_bytes"))
	dgran = read_int(os.path.join(sys_block_path, "queue", "discard_granularity"))
	try:
		return (dmbytes or 0) > 0 or (dgran or 0) > 0
	except Exception:
		return False


def get_parent_device_sysfs(block_sysfs_path):
	"""
	Return the sysfs 'device' directory for this block node (resolves partition
	to its parent device as well).
	"""
	dev_link = os.path.join(block_sysfs_path, "device")
	try:
		return os.path.realpath(dev_link)
	except Exception:
		return dev_link


def read_model_and_serial(block_sysfs_path):
	if not block_sysfs_path or not os.path.isdir(block_sysfs_path):
		return None, None
	device_path = get_parent_device_sysfs(block_sysfs_path)
	model = read_text(os.path.join(device_path, "model"))
	serial = read_text(os.path.join(device_path, "serial"))
	if serial is None:
		serial = read_text(os.path.join(device_path, "wwid"))
	if model:
		model = " ".join(model.split())
	if serial:
		serial = " ".join(serial.split())
	return model, serial


def get_udev_props(major, minor):
	"""
	Read udev properties for a block device from /run/udev/data/bMAJ:MIN
	Returns keys like ID_FS_TYPE, ID_FS_LABEL, ID_FS_UUID when available.
	"""
	props = {}
	path = f"/run/udev/data/b{major}:{minor}"
	try:
		with open(path, "r", encoding="utf-8", errors="ignore") as f:
			for line in f:
				line = line.strip()
				if not line or "=" not in line or line.startswith("#"):
					continue
				k, v = line.split("=", 1)
				props[k] = v
	except Exception:
		pass
	return props


def choose_mount_for_dev(devname, mounts):
	"""
	Choose the most relevant mount for a device:
	- Prefer mounts whose source resolves to /dev/<devname>.
	- If multiple, prefer '/' then shortest mountpoint path.
	- Otherwise return the first entry.
	"""
	if not mounts:
		return None

	def score(m):
		mp = m.get("MOUNTPOINT") or "~"
		s = m.get("SOURCE") or ""
		exact = 1 if (s.startswith("/dev/") and os.path.basename(os.path.realpath(s)) == devname) else 0
		root = 1 if mp == "/" else 0
		return (exact, root, -len(mp))

	best = sorted(mounts, key=score, reverse=True)[0]
	return best


def is_block_device(devpath):
	try:
		st_mode = os.stat(devpath).st_mode
		return stat.S_ISBLK(st_mode)
	except Exception:
		return False


def pretty_format_table(data, delimiter="\t", header=None):
	version = 1.11
	_ = version
	if not data:
		return ""
	if isinstance(data, str):
		data = data.strip("\n").split("\n")
		data = [line.split(delimiter) for line in data]
	elif isinstance(data, dict):
		if isinstance(next(iter(data.values())), dict):
			tempData = [["key"] + list(next(iter(data.values())).keys())]
			tempData.extend(
				[[key] + list(value.values()) for key, value in data.items()]
			)
			data = tempData
		else:
			data = [[key] + list(value) for key, value in data.items()]
	elif not isinstance(data, list):
		data = list(data)
	if isinstance(data[0], dict):
		tempData = [data[0].keys()]
		tempData.extend([list(item.values()) for item in data])
		data = tempData
	data = [[str(item) for item in row] for row in data]
	num_cols = len(data[0])
	col_widths = [0] * num_cols
	for c in range(num_cols):
		col_widths[c] = max(
			len(re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", row[c])) for row in data
		)
	if header:
		header_widths = [
			len(re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", col)) for col in header
		]
		col_widths = [max(col_widths[i], header_widths[i]) for i in range(num_cols)]
	row_format = " | ".join("{{:<{}}}".format(width) for width in col_widths)
	if not header:
		header = data[0]
		outTable = []
		outTable.append(row_format.format(*header))
		outTable.append("-+-".join("-" * width for width in col_widths))
		for row in data[1:]:
			if not any(row):
				outTable.append("-+-".join("-" * width for width in col_widths))
			else:
				outTable.append(row_format.format(*row))
	else:
		if isinstance(header, str):
			header = header.split(delimiter)
		if len(header) < num_cols:
			header += [""] * (num_cols - len(header))
		elif len(header) > num_cols:
			header = header[:num_cols]
		outTable = []
		outTable.append(row_format.format(*header))
		outTable.append("-+-".join("-" * width for width in col_widths))
		for row in data:
			if not any(row):
				outTable.append("-+-".join("-" * width for width in col_widths))
			else:
				outTable.append(row_format.format(*row))
	return "\n".join(outTable) + "\n"


def format_bytes(
	size, use_1024_bytes=None, to_int=False, to_str=False, str_format=".2f"
):
	if to_int or isinstance(size, str):
		if isinstance(size, int):
			return size
		elif isinstance(size, str):
			match = re.match(r"(\d+(\.\d+)?)\s*([a-zA-Z]*)", size)
			if not match:
				if to_str:
					return size
				print(
					"Invalid size format. Expected format: 'number [unit]', "
					"e.g., '1.5 GiB' or '1.5GiB'"
				)
				print(f"Got: {size}")
				return 0
			number, _, unit = match.groups()
			number = float(number)
			unit = unit.strip().lower().rstrip("b")
			if unit.endswith("i"):
				use_1024_bytes = True
			elif use_1024_bytes is None:
				use_1024_bytes = False
			unit = unit.rstrip("i")
			if use_1024_bytes:
				power = 2**10
			else:
				power = 10**3
			unit_labels = {
				"": 0,
				"k": 1,
				"m": 2,
				"g": 3,
				"t": 4,
				"p": 5,
				"e": 6,
				"z": 7,
				"y": 8,
			}
			if unit not in unit_labels:
				if to_str:
					return size
			else:
				if to_str:
					return format_bytes(
						size=int(number * (power**unit_labels[unit])),
						use_1024_bytes=use_1024_bytes,
						to_str=True,
						str_format=str_format,
					)
				return int(number * (power**unit_labels[unit]))
		else:
			try:
				return int(size)
			except Exception:
				return 0
	elif to_str or isinstance(size, int) or isinstance(size, float):
		if isinstance(size, str):
			try:
				size = size.rstrip("B").rstrip("b")
				size = float(size.lower().strip())
			except Exception:
				return size
		if use_1024_bytes or use_1024_bytes is None:
			power = 2**10
			n = 0
			power_labels = {
				0: "",
				1: "Ki",
				2: "Mi",
				3: "Gi",
				4: "Ti",
				5: "Pi",
				6: "Ei",
				7: "Zi",
				8: "Yi",
			}
			while size > power:
				size /= power
				n += 1
			return f"{size:{str_format}} {' '}{power_labels[n]}".replace("  ", " ")
		else:
			power = 10**3
			n = 0
			power_labels = {
				0: "",
				1: "K",
				2: "M",
				3: "G",
				4: "T",
				5: "P",
				6: "E",
				7: "Z",
				8: "Y",
			}
			while size > power:
				size /= power
				n += 1
			return f"{size:{str_format}} {' '}{power_labels[n]}".replace("  ", " ")
	else:
		try:
			return format_bytes(float(size), use_1024_bytes)
		except Exception:
			pass
		return 0


def is_partition(name):
	real = os.path.realpath(os.path.join("/sys/class/block", name))
	return os.path.exists(os.path.join(real, "partition"))


def get_partition_parent_name(name):
	real = os.path.realpath(os.path.join("/sys/class/block", name))
	part_file = os.path.join(real, "partition")
	if not os.path.exists(part_file):
		return None
	parent = os.path.basename(os.path.dirname(real))
	return parent if parent and parent != name else None

def get_drives_info(print_bytes = False, use_1024 = False, mounted_only=False, best_only=False, formated_only=False, show_zero_size_devices=False):
		# Build UUID/LABEL maps and reverse maps for resolving mount "source"
	uuid_map = build_symlink_map("/dev/disk/by-uuid")
	label_map = build_symlink_map("/dev/disk/by-label")
	uuid_rev = {v: k for k, v in uuid_map.items()}
	label_rev = {v: k for k, v in label_map.items()}

	# Mount info maps
	by_majmin, by_devname, _ = parse_mountinfo_enhanced(uuid_rev, label_rev)

	results = []
	results_by_name = {}
	df_stats_by_name = {}  # name -> (blocks, bavail)
	parent_to_children = defaultdict(list)

	sys_class_block = "/sys/class/block"
	try:
		entries = sorted(os.listdir(sys_class_block))
	except Exception:
		entries = []

	for name in entries:
		block_path = os.path.join(sys_class_block, name)

		devnode = os.path.join("/dev", name)
		if not is_block_device(devnode):
			pass

		parent_name = get_partition_parent_name(name)
		if parent_name:
			parent_to_children[parent_name].append(name)

		majmin_str = read_text(os.path.join(block_path, "dev"))
		if not majmin_str or ":" not in majmin_str:
			continue
		try:
			major, minor = majmin_str.split(":", 1)
			major = int(major)
			minor = int(minor)
		except Exception:
			continue

		sectors = read_int(os.path.join(block_path, "size")) or 0
		lb_size = (
			read_int(os.path.join(block_path, "queue", "logical_block_size")) or 512
		)
		size_bytes = sectors * lb_size
		if not show_zero_size_devices and size_bytes == 0:
			continue

		parent_block_path = os.path.join(sys_class_block, parent_name) if parent_name else None
		model, serial = read_model_and_serial(block_path)
		parent_model, parent_serial = read_model_and_serial(parent_block_path)

		# UUID/Label from by-uuid/by-label symlinks
		
		props = get_udev_props(major, minor=minor)
		# Fallback to udev props
		rec = {
				"NAME": name,
				"FSTYPE": props.get("ID_FS_TYPE"),
				"LABEL": label_map.get(name, props.get("ID_FS_LABEL")),
				"UUID": uuid_map.get(name, props.get("ID_FS_UUID")),
				"MOUNTPOINT": None,
				"MODEL": model if model else parent_model,
				"SERIAL": serial if serial else parent_serial,
				"DISCARD": bool(read_discard_support(block_path) or read_discard_support(parent_block_path)),
				"SIZE": f"{format_bytes(size_bytes, to_int=print_bytes, use_1024_bytes=use_1024)}B",
				"FSUSE%": None,
				"SMART": 'N/A',
		}
		if SMARTCTL_PATH:
			# if do not have read permission on the denode, set SMART to 'DENIED'
			if not os.access(devnode, os.R_OK):
				rec["SMART"] = 'DENIED'
			try:
				# run smartctl -H <device>
				outputLines = subprocess.check_output([SMARTCTL_PATH, "-H", devnode], stderr=subprocess.STDOUT).decode().splitlines()
				# Parse output for SMART status
				for line in outputLines:
					line = line.lower()
					if "health" in line:
						smartinfo = line.rpartition(':')[2].strip().upper()
						rec["SMART"] = smartinfo.replace('PASSED', 'OK')
			except:
				pass
		# Mount and fstype: try maj:min first, then by resolved devname
		mounts = by_majmin.get(majmin_str, [])
		if not mounts:
			mounts = by_devname.get(name, [])
		if best_only:
			mounts = [choose_mount_for_dev(name, mounts)] if mounts else []
		if not mounted_only and not mounts:
			if formated_only and not rec.get("FSTYPE"):
				continue
			results.append(rec)
			results_by_name[name] = rec
		for mount in mounts:
			rec = rec.copy()
			mountpoint = mount.get("MOUNTPOINT")
			if mount.get("FSTYPE"):
				rec["FSTYPE"] = mount.get("FSTYPE")
			if formated_only and not rec.get("FSTYPE"):
				continue
			# Use% via statvfs and collect raw stats for aggregation
			if mountpoint:
				try:
					st = os.statvfs(mountpoint)
					if st.f_blocks > 0:
						use_pct = 100.0 * (1.0 - (st.f_bavail / float(st.f_blocks)))
						rec["FSUSE%"] = f'{use_pct:.1f}%'
						df_stats_by_name[name] = (st.f_blocks, st.f_bavail)
				except Exception:
					pass
			rec["MOUNTPOINT"] = mountpoint
			results.append(rec)
			results_by_name[name] = rec

	# Aggregate use% for parent devices with partitions:
	# parent's use% = 1 - sum(bavail)/sum(blocks) over mounted partitions
	for parent, children in parent_to_children.items():
		sum_blocks = 0
		sum_bavail = 0
		for ch in children:
			vals = df_stats_by_name.get(ch)
			if not vals:
				continue
			b, ba = vals
			if b and b > 0:
				sum_blocks += b
				sum_bavail += ba if ba is not None else 0
		if sum_blocks > 0 and parent in results_by_name:
			pct = 100.0 * (1.0 - (sum_bavail / float(sum_blocks)))
			results_by_name[parent]["FSUSE%"] = f'{pct:.1f}%'

	results.sort(key=lambda x: x["NAME"])  # type: ignore
	return results

def main():
	parser = argparse.ArgumentParser(description="Gather disk and partition info for block devices.")
	parser.add_argument('-j','--json', help="Produce JSON output", action="store_true")
	parser.add_argument('-b','--bytes', help="Print the SIZE column in bytes rather than in a human-readable format", action="store_true")
	parser.add_argument('-H','--si', help="Use powers of 1000 not 1024 for SIZE column", action="store_true")
	parser.add_argument('-F','-fo','--formated_only', help="Show only formated filesystems", action="store_true")
	parser.add_argument('-M','-mo','--mounted_only', help="Show only mounted filesystems", action="store_true")
	parser.add_argument('-B','-bo','--best_only', help="Show only best mount for each device", action="store_true")
	parser.add_argument('--show_zero_size_devices', help="Show devices with zero size", action="store_true")
	parser.add_argument('-V', '--version', action='version', version=f"%(prog)s {version} @ {COMMIT_DATE} stat drives by pan@zopyr.us")

	args = parser.parse_args()
	results = get_drives_info(print_bytes = args.bytes, use_1024 = not args.si, 
						   mounted_only=args.mounted_only, best_only=args.best_only, 
						   formated_only=args.formated_only, show_zero_size_devices=args.show_zero_size_devices)
	if args.json:
		import json
		print(json.dumps(results, indent=4))
	else:
		print(pretty_format_table(results))


if __name__ == "__main__":
	main()