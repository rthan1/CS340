from ursina import *


def main():
	app = Ursina()
	window.title = 'CS340 Still Image'
	window.borderless = False
	window.color = color.rgb(6, 10, 16)

	# Match the animation's starting environment
	Sky(color=color.rgb(50, 40, 70))
	camera.clip_plane_far = 500
	camera.fov = 85
	if hasattr(camera, 'fog_density'):
		camera.fog_color = color.rgb(25, 20, 35)
		camera.fog_density = 0.02

	DirectionalLight(shadows=True, rotation=(55, 45, 0), color=color.rgb(255, 230, 200))
	AmbientLight(color=color.rgba(160, 175, 210, 255))

	# Helper for textures with safe fallback
	def tex(name: str) -> str:
		try:
			load_texture(name)
			return name
		except Exception:
			return 'white_cube'

	# Ground and path like in the animation start
	ground = Entity(model='plane', texture=tex('grass'), color=color.rgb(70, 85, 75), texture_scale=(80, 80), scale=160)
	path = Entity(model='cube', texture=tex('brick'), color=color.rgb(120, 120, 140), position=(0, 0.01, 0), scale=(6, 0.02, 90))

	# Architectural arches ahead
	for i in range(14):
		z = 4 + i * 6.5
		Entity(model='cube', texture=tex('brick'), color=color.rgb(160, 160, 190), position=(-2.7, 1.75, z), scale=(0.5, 3.5, 0.5))
		Entity(model='cube', texture=tex('brick'), color=color.rgb(160, 160, 190), position=(2.7, 1.75, z), scale=(0.5, 3.5, 0.5))
		Entity(model=Circle(resolution=64, mode='line', thickness=4), color=color.rgba(230, 230, 255, 160), position=(0, 3.55, z), rotation_x=90, scale=3.2)

	# Static lantern bulbs and lights (no sway in still image)
	for i in range(12):
		z = 6 + i * 7
		for x in (-2.0, 2.0):
			bulb = Entity(model='sphere', texture=tex('white_cube'), color=color.rgb(255, 200, 110), position=(x, 3.8, z), scale=0.25)
			PointLight(parent=bulb, color=color.rgb(255, 210, 120), shadows=True)

	# Position the camera at the animation's starting frame
	camera.position = (0, 1.8, -12)
	camera.rotation = (0, 0, 0)

	app.run()


if __name__ == '__main__':
	main()


