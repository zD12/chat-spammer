import json
import csv

from twisted.internet import defer, reactor
from quarry.net.client import ClientFactory, SpawningClientProtocol
from quarry.net.auth import Profile, OfflineProfile

with open("config.json") as config_file:
	config = json.load(config_file).data

messages = []

with open("messages.csv", newline="") as _messages_csv:
	_messages = csv.DictReader(_messages_csv)
	for row in _messages:
		messages.append((row["prefix_flag"], row["message"]))


class SpammerProtocol(SpawningClientProtocol):
	def player_joined(self):
		print("connected")
		super(SpammerProtocol, self).player_joined()
		self.ticker.add_loop(config["anti_afk"], self.anti_afk)
		
	def anti_afk(self):
		print("anti-afk script ran")
		

class SpammerFactory(ClientFactory):
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
