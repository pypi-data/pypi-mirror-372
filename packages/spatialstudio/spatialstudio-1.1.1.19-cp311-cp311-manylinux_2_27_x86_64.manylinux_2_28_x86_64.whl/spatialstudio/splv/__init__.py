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
	width, height, depth = self.get_dims()

	step = (6 * scale) + 1
	if flip:
		step *= -1

	if maxWidth is None:
		maxWidth = width if axis == 'z' else depth

	lines = []
	line = ""
	lineVoxels = 0

	words = text.split()
	for wi, word in enumerate(words):
		wordVoxels = len(word) * abs(step)
		spaceVoxels = abs(step) if line else 0

		if lineVoxels + spaceVoxels + wordVoxels <= maxWidth:
			if line:
				line += " "
				lineVoxels += spaceVoxels
			line += word
			lineVoxels += wordVoxels
		else:
			if wordVoxels <= maxWidth:
				if line:
					lines.append(line)
				line = word
				lineVoxels = wordVoxels
			else:
				remaining = maxWidth - lineVoxels
				charsFit = max(1, (remaining // abs(step)) - 1)
				if line:
					lines.append(line + " " + word[:charsFit] + "-")
				else:
					lines.append(word[:charsFit] + "-")
				wordRest = word[charsFit:]
				line = wordRest
				lineVoxels = len(wordRest) * abs(step)

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