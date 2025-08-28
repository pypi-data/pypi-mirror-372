from .libsplv_py import *

FONT_5x5 = {
	'A': [
		" ### ",
		"#   #",
		"#   #",
		"#####",
		"#   #",
	],
	'B': [
		"#### ",
		"#   #",
		"####",
		"#   #",
		"####",
	],
	'C': [
		" ####",
		"#    ",
		"#    ",
		"#    ",
		" ####",
	],
	'D': [
		"####",
		"#   #",
		"#   #",
		"#   #",
		"####",
	],
	'E': [
		"#####",
		"#    ",
		"#### ",
		"#    ",
		"#####",
	],
	'F': [
		"#####",
		"#    ",
		"#### ",
		"#    ",
		"#    ",
	],
	'G': [
		" ####",
		"#    ",
		"# ###",
		"#   #",
		" ####",
	],
	'H': [
		"#   #",
		"#   #",
		"#####",
		"#   #",
		"#   #",
	],
	'I': [
		"#####",
		"  #  ",
		"  #  ",
		"  #  ",
		"#####",
	],
	'J': [
		"    #",
		"    #",
		"#   #",
		"#   #",
		" ### ",
	],
	'K': [
		"#   #",
		"#  # ",
		"###  ",
		"#  #",
		"#   #",
	],
	'L': [
		"#    ",
		"#    ",
		"#    ",
		"#    ",
		"#####",
	],
	'M': [
		"#   #",
		"## ##",
		"# # #",
		"# # #",
		"#   #",
	],
	'N': [
		"#   #",
		"##  #",
		"# # #",
		"#  ##",
		"#   #",
	],
	'O': [
		" ### ",
		"#   #",
		"#   #",
		"#   #",
		" ### ",
	],
	'P': [
		"#### ",
		"#   #",
		"#### ",
		"#    ",
		"#    ",
	],
	'Q': [
		" ### ",
		"#   #",
		"#   #",
		"#  # ",
		" ## #",
	],
	'R': [
		"#### ",
		"#   #",
		"#### ",
		"#  # ",
		"#   #",
	],
	'S': [
		" ####",
		"#    ",
		" ### ",
		"    #",
		"#### ",
	],
	'T': [
		"#####",
		"  #  ",
		"  #  ",
		"  #  ",
		"  #  ",
	],
	'U': [
		"#   #",
		"#   #",
		"#   #",
		"#   #",
		" ### ",
	],
	'V': [
		"#   #",
		"#   #",
		"#   #",
		" # # ",
		"  #  ",
	],
	'W': [
		"#   #",
		"# # #",
		"# # #",
		"# # #",
		" ### ",
	],
	'X': [
		"#   #",
		" # # ",
		"  #  ",
		" # # ",
		"#   #",
	],
	'Y': [
		"#   #",
		"#   #",
		" ### ",
		"  #  ",
		"  #  ",
	],
	'Z': [
		"#####",
		"   # ",
		"  #  ",
		" #   ",
		"#####",
	],
	'0': [
		" ### ",
		"##  #",
		"# # #",
		"#  ##",
		" ### ",
	],
	'1': [
		" ##  ",
		"# #  ",
		"  #  ",
		"  #  ",
		"#####",
	],
	'2': [
		"#### ",
		"    #",
		"  ## ",
		" #   ",
		"#####",
	],
	'3': [
		"#####",
		"    #",
		" ####",
		"    #",
		"#####",
	],
	'4': [
		"#   #",
		"#   #",
		"#####",
		"    #",
		"    #",
	],
	'5': [
		"#####",
		"#    ",
		"#####",
		"    #",
		"#####",
	],
	'6': [
		"#####",
		"#    ",
		"#####",
		"#   #",
		"#####",
	],
	'7': [
		"#####",
		"    #",
		"   # ",
		"  #  ",
		" #   ",
	],
	'8': [
		"#####",
		"#   #",
		"#####",
		"#   #",
		"#####",
	],
	'9': [
		"#####",
		"#   #",
		"#####",
		"    #",
		"#####",
	],
	' ': [
		"     ",
		"     ",
		"     ",
		"     ",
		"     ",
	],
	'.': [
		"     ",
		"     ",
		"     ",
		"     ",
		"  #  ",
	],
	'?': [
		" ### ",
		"   # ",
		"  #  ",
		"     ",
		"  #  ",
	],
	'!': [
		"  #  ",
		"  #  ",
		"  #  ",
		"     ",
		"  #  ",
	],
	'(': [
		"  ## ",
		" #   ",
		" #   ",
		" #   ",
		"  ## ",
	],
	')': [
		" ##  ",
		"   # ",
		"   # ",
		"   # ",
		" ##  ",
	],
	'+': [
		"     ",
		"  #  ",
		" ### ",
		"  #  ",
		"     ",
	],
	'-': [
		"     ",
		"     ",
		" ### ",
		"     ",
		"     ",
	],
	'*': [
		"     ",
		" # # ",
		"  #  ",
		" # # ",
		"     ",
	],
	'/': [
		"    #",
		"   # ",
		"  #  ",
		" #   ",
		"#    ",
	],
	'=': [
		"     ",
		"#####",
		"     ",
		"#####",
		"     ",
	],
	':': [
		"     ",
		"  #  ",
		"     ",
		"  #  ",
		"     ",
	],
}

def write_char(self, ch, pos, voxel=(0, 0, 0), outlineVoxel=(255, 255, 255), axis='z', flip=False, scale=1):
	ch = ch.upper()
	bitmap = FONT_5x5.get(ch, FONT_5x5[' '])

	width, height, depth = self.get_dims()

	filled = set()
	for y, row in enumerate(bitmap):
		for x, c in enumerate(row):
			if c != ' ':
				if flip:
					xWrite = 4 - x
				else:
					xWrite = x
				
				filled.add((xWrite, 4 - y))

	dirs = [(-1,-1), (0,-1), (1,-1),
			(-1, 0),         (1, 0),
			(-1, 1), (0, 1), (1, 1)]
	outline = set()
	for (px, py) in filled:
		for dx, dy in dirs:
			npx, npy = px + dx, py + dy
			if (npx, npy) not in filled:
				outline.add((npx, npy))

	def map_to_axis(px, py, pos, axis):
		if axis == 'z':
			return (pos[0] + px, pos[1] + py, pos[2])
		elif axis == 'x':
			return (pos[0], pos[1] + py, pos[2] + px)
		else:
			raise ValueError(f"Unknown axis {axis}")

	for (px, py) in outline:
		for sy in range(int(scale)):
			for sx in range(int(scale)):
				vx, vy, vz = map_to_axis(px*scale + sx, py*scale + sy, pos, axis)
				if 0 <= vx < width and 0 <= vy < height and 0 <= vz < depth:
					self[vx, vy, vz] = outlineVoxel

	for (px, py) in filled:
		for sy in range(int(scale)):
			for sx in range(int(scale)):
				vx, vy, vz = map_to_axis(px*scale + sx, py*scale + sy, pos, axis)
				if 0 <= vx < width and 0 <= vy < height and 0 <= vz < depth:
					self[vx, vy, vz] = voxel

def write_string(self, text, startPos, voxel=(0, 0, 0), outlineVoxel=(255, 255, 255), axis='z', flip=False, scale=1, maxWidth=None):
	width, _, depth = self.get_dims()

	step = (6 * scale) + 1
	if flip:
		step *= -1

	if maxWidth is None:
		if flip:
			maxWidth = startPos[0] if axis == 'x' else startPos[2]
		else:
			maxWidth = width - startPos[0] if axis == 'x' else depth - startPos[2]

	if maxWidth <= 0:
		maxWidth = width if axis == 'x' else depth

	maxChars = max(1, maxWidth // abs(step))
	words = text.split()
	lines = []
	line = ""

	for word in words:
		if len(word) <= maxChars:
			if not line:
				line = word
			elif len(line) + 1 + len(word) <= maxChars:
				line += " " + word
			else:
				lines.append(line)
				line = word
			continue

		if line:
			spaceLeft = maxChars - len(line) - 1
			if spaceLeft >= 2:
				take = min(spaceLeft - 1, len(word))
				if take > 0:
					line += " " + word[:take] + "-"
					word = word[take:]
					lines.append(line)
					line = ""
			else:
				lines.append(line)
				line = ""

		while word:
			if len(word) <= maxChars:
				line = word
				word = ""
			else:
				if maxChars > 1:
					chunk = word[: maxChars - 1]
					lines.append(chunk + "-")
					word = word[len(chunk) :]
				else:
					lines.append(word[0] + "-")
					word = word[1:]

	if line:
		lines.append(line)

	for li, line in enumerate(lines):
		for i, ch in enumerate(line):
			dx, dz = 0, 0
			if axis == 'z':
				dx = int(i * step)
			elif axis == 'x':
				dz = int(i * step)

			pos = (startPos[0] + dx, startPos[1] - li * (6 * scale), startPos[2] + dz)
			self.write_char(
				ch, pos,
				voxel=voxel, outlineVoxel=outlineVoxel,
				axis=axis, scale=scale, flip=flip
			)

Frame.write_char = write_char
Frame.write_string = write_string