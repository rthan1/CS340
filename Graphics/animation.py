from ursina import *
import math


class HeadBob:
	def __init__(self, camera_entity: Entity, amplitude: float = 0.03, frequency: float = 9.0):
		self.camera = camera_entity
		self.amplitude = amplitude
		self.frequency = frequency
		self.phase = 0.0

	def update(self, moving: bool, dt: float):
		if moving:
			self.phase += self.frequency * dt
			self.camera.y = 1.8 + math.sin(self.phase) * self.amplitude
		else:
			self.phase = max(0.0, self.phase - self.frequency * dt * 0.6)
			self.camera.y = lerp(self.camera.y, 1.8, min(1, dt*8))


def main():
	app = Ursina()
	window.title = 'CS340 First-Person Animation'
	window.borderless = False
	window.color = color.rgb(6, 10, 16)

	# Sunset sky tint and light fog for depth
	Sky(color=color.rgb(50, 40, 70))
	camera.clip_plane_far = 500
	camera.fov = 85
	if hasattr(camera, 'fog_density'):
		camera.fog_color = color.rgb(25, 20, 35)
		camera.fog_density = 0.02

	DirectionalLight(shadows=True, rotation=(55, 45, 0), color=color.rgb(255, 230, 200))
	AmbientLight(color=color.rgba(160, 175, 210, 255))

	# Try richer textures with fallbacks
	def tex(name: str) -> str:
		try:
			load_texture(name)
			return name
		except Exception:
			return 'white_cube'

	# Arena ground with tiling rock-like texture
	ground = Entity(model='plane', texture=tex('grass'), color=color.rgb(70, 85, 75), texture_scale=(80, 80), scale=160)

	# Pathway with metallic-ish tone
	path = Entity(model='cube', texture=tex('brick'), color=color.rgb(120, 120, 140), position=(0, 0.01, 0), scale=(6, 0.02, 90))

	# Architectural arches along the path
	arches: list[Entity] = []
	for i in range(14):
		z = 4 + i * 6.5
		pillar_l = Entity(model='cube', texture=tex('brick'), color=color.rgb(160, 160, 190), position=(-2.7, 1.75, z), scale=(0.5, 3.5, 0.5))
		pillar_r = Entity(model='cube', texture=tex('brick'), color=color.rgb(160, 160, 190), position=(2.7, 1.75, z), scale=(0.5, 3.5, 0.5))
		arch = Entity(model=Circle(resolution=64, mode='line', thickness=4), color=color.rgba(230, 230, 255, 160), position=(0, 3.55, z), rotation_x=90, scale=3.2)
		arches += [pillar_l, pillar_r, arch]

	# Floating lanterns that sway, with emissive bulbs and point lights
	lanterns: list[tuple[Entity, PointLight]] = []
	for i in range(12):
		z = 6 + i * 7
		for x in (-2.0, 2.0):
			bulb = Entity(model='sphere', texture=tex('white_cube'), color=color.rgb(255, 200, 110), position=(x, 3.8, z), scale=0.25)
			light = PointLight(parent=bulb, color=color.rgb(255, 210, 120), shadows=True)
			lanterns.append((bulb, light))

	# Player/camera rig for first-person animation
	player = Entity(position=(0, 1.8, -12))
	camera.parent = player
	camera.position = (0, 0, 0)
	camera.rotation = (0, 0, 0)

	head_bob = HeadBob(camera)

	# Animation path: forward, slight turns, and a finish spin
	keyframes = [
		{'t': 0.0,  'pos': Vec3(0, 1.8, -12), 'yaw': 0},
		{'t': 7.0,  'pos': Vec3(0, 1.8, 28),  'yaw': 0},
		{'t': 11.0, 'pos': Vec3(2.5, 1.8, 50), 'yaw': 12},
		{'t': 15.0, 'pos': Vec3(-2.5, 1.8, 74), 'yaw': -18},
		{'t': 18.0, 'pos': Vec3(0, 1.8, 90),  'yaw': 0},
		{'t': 21.0, 'pos': Vec3(0, 1.8, 90),  'yaw': 360},
	]

	def sample_track(time_s: float):
		if time_s <= keyframes[0]['t']:
			return keyframes[0]['pos'], keyframes[0]['yaw']
		if time_s >= keyframes[-1]['t']:
			return keyframes[-1]['pos'], keyframes[-1]['yaw']
		for i in range(len(keyframes) - 1):
			k0, k1 = keyframes[i], keyframes[i+1]
			if k0['t'] <= time_s <= k1['t']:
				a = (time_s - k0['t']) / (k1['t'] - k0['t'])
				return lerp(k0['pos'], k1['pos'], a), lerp(k0['yaw'], k1['yaw'], a)
		return keyframes[-1]['pos'], keyframes[-1]['yaw']

	# UI reticle only (removed vignette to avoid black box overlay)
	reticle = Entity(parent=camera.ui, model='quad', color=color.rgba(255,255,255,90), position=(0,0), scale=(0.006, 0.006))

	# Animation state encapsulated in a dedicated entity so its update is auto-called
	class Animator(Entity):
		def __init__(self):
			super().__init__()
			self.timer = 0.0
			self.finished = False

		def update(self):
			if self.finished:
				return
			self.timer += time.dt
			pos, yaw = sample_track(self.timer)
			player.position = pos
			player.rotation_y = yaw

			# Head bob when moving
			head_bob.update(True, time.dt)

			# Lantern sway and emissive pulse
			for idx, (bulb, light) in enumerate(lanterns):
				bulb.x += math.sin(self.timer * 0.9 + idx) * 0.002
				bulb.y = 3.8 + math.sin(self.timer * 2.3 + idx*0.5) * 0.02
				p = 0.5 + 0.5 * math.sin(self.timer * 3.0 + idx)
				bulb.color = color.rgb(210 + int(35*p), 160 + int(30*p), 80)
				light.color = color.rgb(255, 210 + int(25*p), 120)

			# Reticle pulse
			reticle.scale = (0.006 + 0.001*math.sin(self.timer*5), 0.006 + 0.001*math.sin(self.timer*5))

			if self.timer >= keyframes[-1]['t']:
				self.finished = True
				invoke(application.quit, delay=2.0)

	Animator()

	app.run()


if __name__ == '__main__':
	main()


