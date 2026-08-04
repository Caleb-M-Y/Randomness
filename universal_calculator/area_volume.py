from __future__ import annotations

from equations import Action, BaseCalculator, IOContext, format_result


class AreaVolumeCalculator(BaseCalculator):
	title = "Area and Volume Calculator"

	def actions(self) -> list[Action]:
		return [
			Action("Area of a circle", self.area_circle),
			Action("Area of a rectangle", self.area_rectangle),
			Action("Area of a triangle", self.area_triangle),
			Action("Area of a parallelogram", self.area_parallelogram),
			Action("Area of a trapezoid", self.area_trapezoid),
			Action("Area of an ellipse", self.area_ellipse),
			Action("Volume of a cube", self.volume_cube),
			Action("Volume of a rectangular prism", self.volume_prism),
			Action("Volume of a sphere", self.volume_sphere),
			Action("Volume of a hemisphere", self.volume_hemisphere),
			Action("Volume of a cylinder", self.volume_cylinder),
			Action("Volume of a cone", self.volume_cone),
			Action("Volume of a pyramid", self.volume_pyramid),
		]

	def _require(self, io: IOContext, prompt: str) -> float | None:
		value = io.ask_float(prompt)
		if value is None:
			return None
		if value < 0:
			io.error("Enter a non-negative value.")
			return None
		return value

	def area_circle(self, io: IOContext) -> None:
		radius = self._require(io, "Radius")
		if radius is None:
			return
		io.tell(f"Area: {format_result(3.141592653589793 * radius * radius)}")

	def area_rectangle(self, io: IOContext) -> None:
		width = self._require(io, "Width")
		if width is None:
			return
		length = self._require(io, "Length")
		if length is None:
			return
		io.tell(f"Area: {format_result(width * length)}")

	def area_triangle(self, io: IOContext) -> None:
		base = self._require(io, "Base")
		if base is None:
			return
		height = self._require(io, "Height")
		if height is None:
			return
		io.tell(f"Area: {format_result(0.5 * base * height)}")

	def area_parallelogram(self, io: IOContext) -> None:
		base = self._require(io, "Base")
		if base is None:
			return
		height = self._require(io, "Height")
		if height is None:
			return
		io.tell(f"Area: {format_result(base * height)}")

	def area_trapezoid(self, io: IOContext) -> None:
		base_one = self._require(io, "Base one")
		if base_one is None:
			return
		base_two = self._require(io, "Base two")
		if base_two is None:
			return
		height = self._require(io, "Height")
		if height is None:
			return
		io.tell(f"Area: {format_result(0.5 * (base_one + base_two) * height)}")

	def area_ellipse(self, io: IOContext) -> None:
		semi_major = self._require(io, "Semi-major axis")
		if semi_major is None:
			return
		semi_minor = self._require(io, "Semi-minor axis")
		if semi_minor is None:
			return
		io.tell(f"Area: {format_result(3.141592653589793 * semi_major * semi_minor)}")

	def volume_cube(self, io: IOContext) -> None:
		side = self._require(io, "Side length")
		if side is None:
			return
		io.tell(f"Volume: {format_result(side ** 3)}")

	def volume_prism(self, io: IOContext) -> None:
		length = self._require(io, "Length")
		if length is None:
			return
		width = self._require(io, "Width")
		if width is None:
			return
		height = self._require(io, "Height")
		if height is None:
			return
		io.tell(f"Volume: {format_result(length * width * height)}")

	def volume_sphere(self, io: IOContext) -> None:
		radius = self._require(io, "Radius")
		if radius is None:
			return
		io.tell(f"Volume: {format_result((4.0 / 3.0) * 3.141592653589793 * radius ** 3)}")

	def volume_hemisphere(self, io: IOContext) -> None:
		radius = self._require(io, "Radius")
		if radius is None:
			return
		io.tell(f"Volume: {format_result((2.0 / 3.0) * 3.141592653589793 * radius ** 3)}")

	def volume_cylinder(self, io: IOContext) -> None:
		radius = self._require(io, "Radius")
		if radius is None:
			return
		height = self._require(io, "Height")
		if height is None:
			return
		io.tell(f"Volume: {format_result(3.141592653589793 * radius ** 2 * height)}")

	def volume_cone(self, io: IOContext) -> None:
		radius = self._require(io, "Radius")
		if radius is None:
			return
		height = self._require(io, "Height")
		if height is None:
			return
		io.tell(f"Volume: {format_result((1.0 / 3.0) * 3.141592653589793 * radius ** 2 * height)}")

	def volume_pyramid(self, io: IOContext) -> None:
		base_area = self._require(io, "Base area")
		if base_area is None:
			return
		height = self._require(io, "Height")
		if height is None:
			return
		io.tell(f"Volume: {format_result((1.0 / 3.0) * base_area * height)}")
