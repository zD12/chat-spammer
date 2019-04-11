import json
import csv
import glm

from twisted.internet import defer, reactor
from quarry.net.client import ClientFactory, SpawningClientProtocol
from quarry.net.auth import Profile, OfflineProfile
import random

from twisted.internet.protocol import ReconnectingClientFactory

with open("config.json") as config_file:
	config = json.load(config_file)

messages = []

with open("messages.csv", newline="") as _messages_csv:
	_messages = csv.DictReader(_messages_csv)
	for row in _messages:
		messages.append((row["prefix_flag"], row["message"]))


class SpammerProtocol(SpawningClientProtocol):
	def __init__(self, *args, **kwargs):
		super(SpammerProtocol, self).__init__(*args, **kwargs)
		self.player_position = glm.vec3(0, 0, 0)
		
		self.loop = {
			"afk": True,
			"message": True
		}
		
		self.crouched = False
		self.walk_cycle_running = False
		self.player_eid = -1
		
	def player_joined(self):
		super(SpammerProtocol, self).player_joined()
		
		print("connected")
		
		self.ticker.add_delay(50, self.anti_afk)
		self.ticker.add_delay(50, self.random_message)
		
		if config["spawn_mode"]["enabled"]:
			self.ticker.add_loop(config["spawn_mode"]["speed"], self.toggle_crouch)
		
	def anti_afk(self):
		if not self.loop["afk"]:
			return
		
		self.walk_cycle()
		self.send_packet("use_item", self.buff_type.pack_varint(random.choice([0, 1])))
		self.send_packet("held_item_change", self.buff_type.pack("h", random.randint(0, 8)))
		
		# getting loop interval every time instead of getting once
		self.ticker.add_delay(self.get_delay("anti_afk"), self.anti_afk)
		
	def walk_cycle(self):
		if self.walk_cycle_running:
			return
		
		speed_divider = config["walk"]["speed_divider"]
		self.walk_cycle_running = True
		
		limit = config["walk"]["walk_distance"]
		direction = random.choice([glm.vec3(1, 0, 0), glm.vec3(-1, 0, 0), glm.vec3(0, 0, 1), glm.vec3(0, 0, -1)])
		
		global sequence
		sequence = []
		
		for _ in range(limit * speed_divider):
			sequence.append(direction / speed_divider)
		
		for _ in range(limit * speed_divider):
			sequence.append((direction / speed_divider) * glm.vec3(-1, 1, -1))
			
		def walk(position):
			x, y, z = self.player_position = self.player_position - position
			self.pos_look[0] = x
			self.pos_look[1] = y
			self.pos_look[2] = z
			self.send_packet("player_position", self.buff_type.pack("ddd?", x, y, z, True))
		
		global index
		index = 0
		
		def ticker_loop():
			global index
			global sequence
			
			walk(sequence[index])
			
			if not index + 1 > sequence.__len__() - 1:
				index += 1
				self.ticker.add_delay(config["walk"]["speed"], ticker_loop)
			else:
				self.walk_cycle_running = False
		
		ticker_loop()
		
	def random_message(self):
		if not self.loop["message"]:
			return
		
		msg_index = random.randint(0, messages.__len__() - 1)
		prefix_flag, msg = messages[msg_index]
		
		if prefix_flag == "random":
			show_prefix = bool(random.getrandbits(1))
		else:
			show_prefix = prefix_flag == "always"
			
		output = ""
		if show_prefix:
			output += config["prefix"]
		
		output += msg
		self.send_packet('chat_message', self.buff_type.pack_string(output))
		self.logger.debug("sending message: %s" % output)
		
		# getting loop interval every time instead of getting once
		self.ticker.add_delay(self.get_delay("message_speed"), self.random_message)
	
	def toggle_crouch(self):
		if self.crouched:
			new_action = 1
		else:
			new_action = 0
			
		self.send_packet("entity_action", self.buff_type.pack_varint(self.player_eid), self.buff_type.pack_varint(new_action), self.buff_type.pack_varint(0))
		
		self.crouched = not self.crouched
	
	def respawn(self):
		self.send_packet("client_status", self.buff_type.pack_varint(0))
		
	@staticmethod
	def get_delay(name):
		if name in config["rng_events"]:
			return random.randint(0, config[name])
		return config[name]
		
	# packet handling
	def packet_update_health(self, buff):
		hp = buff.unpack("f")
		buff.discard()

		if hp <= 0:
			self.ticker.add_delay(self.get_delay("respawn_speed"), self.respawn)
			
	def packet_player_position_and_look(self, buff):
		super(SpammerProtocol, self).packet_player_position_and_look(buff)
		self.player_position = glm.vec3(self.pos_look[0], self.pos_look[1], self.pos_look[2])
	
	def packet_join_game(self, buff):
		buff.save()
		self.player_eid = buff.unpack_varint()
		buff.restore()
		super(SpammerProtocol, self).packet_unhandled(buff, "join_game")
		
	# misc
	def update_player_full(self):
		if not self.walk_cycle_running:
			super(SpammerProtocol, self).update_player_full()

	
class SpammerFactory(ClientFactory, ReconnectingClientFactory):
	protocol = SpammerProtocol
	
	def __init__(self, *args, **kwargs):
		print("Connecting...")
		super(SpammerFactory, self).__init__(*args, **kwargs)


@defer.inlineCallbacks
def main():
	if config["account"]["online"]:
		profile = yield Profile.from_credentials(config["account"]["email"], config["account"]["password"])
	else:
		profile = yield OfflineProfile.from_display_name(config["account"]["username"])
	
	factory = SpammerFactory(profile)
	yield factory.connect(config["server"]["host"], config["server"]["port"])


if __name__ == "__main__":
	main()
	reactor.run()
