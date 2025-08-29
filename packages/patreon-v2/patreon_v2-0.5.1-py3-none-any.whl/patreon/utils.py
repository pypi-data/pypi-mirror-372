import pkg_resources
import platform

def user_agent_string():
	return "Patreon-Python, version {}, platform {}".format(
		pkg_resources.get_distribution('patreon-v2').version,
		platform.platform(),
	)