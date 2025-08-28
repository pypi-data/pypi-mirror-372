"""Model with basic utils for building progress bars"""

from math import atan2, pi


def draw_circle(  # noqa: PLR0912
	size: int = 10,
	percentage: int = 50,
	filled_char: str = "█",
	empty_char: str = "░",
	title: str | None = None,
):
	"""
	Draw a circle with the given size and fill percentage.

	**Parameters:**

	- `size`: Diameter of the circle in characters.
	- `percentage`: Percentage of the circle to be filled.
	- `filled_char`: Character used for the filled part of the circle.
	- `empty_char`: Character used for the empty part of the circle.
	- `title`: Optional text to be displayed inside or below the circle.

	**Returns:**

	String representation of the circle.
	"""
	result = []
	center = size // 2
	radius = size // 2 - 1

	# Prepare title lines for centering
	title_lines = []
	if title:
		max_width = max(1, int(radius * 1.5))  # Approximate max width for text
		words = title.split()
		current_line = ""

		for word in words:
			test_line = f"{current_line} {word}".strip()
			if len(test_line) <= max_width:
				current_line = test_line
			else:
				if current_line:
					title_lines.append(current_line)
				current_line = word
		if current_line:
			title_lines.append(current_line)

	# Vertical centering for text
	text_start_y = center - len(title_lines) // 2

	for y in range(size):
		line = ""
		for x in range(size):
			# Calculate distance from center
			dx = x - center
			dy = y - center
			distance = (dx**2 + dy**2) ** 0.5
			angle = ((180 / pi) * (pi + atan2(dy, dx))) % 360

			# Determine if current position is within text area
			is_text_area = distance < radius / 1.3

			if is_text_area and title:
				text_line_index = y - text_start_y
				if 0 <= text_line_index < len(title_lines):
					current_text_line = title_lines[text_line_index]
					text_start_x = center - len(current_text_line) // 2
					char_index = x - text_start_x

					if 0 <= char_index < len(current_text_line):
						line += current_text_line[char_index] + " "
						continue  # Skip normal drawing if text is placed

			# Draw circle if not in text area
			if distance <= radius:
				fill_angle = (percentage / 100) * 360
				if angle <= fill_angle:
					line += filled_char * 2
				else:
					line += empty_char * 2
			else:
				line += "  "

		result.append(line.rstrip())  # Remove trailing spaces for clean output

	return "\n\r".join(result)


def draw_fluid(
	size: int = 10,
	percentage: int = 50,
	filled_char: str = "█",
	empty_char: str = "░",
	title: str | None = None,
):
	result = []
	center = size // 2
	radius = size // 2 - 1
	borders = 5
	fill_height = (percentage / 100) * (radius * 2)
	for y in range(size):
		line = ""
		for x in range(size):
			dx = x - center
			dy = y - center
			distance = (dx**2 + dy**2) ** 0.5
			if distance <= radius:
				if abs(distance) > borders:
					line += filled_char * 2
					continue
				height_from_bottom = (center + radius) - y
				if height_from_bottom <= fill_height:
					line += filled_char * 2
				else:
					line += empty_char * 2
			else:
				line += "  "
		result.append(line.rstrip())

	return "\n\r".join(result)
