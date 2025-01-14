from .SimConnect import SimConnect, millis, DWORD
from .RequestList import AircraftRequests, Request
from .EventList import AircraftEvents, Event
from .FacilitiesList import FacilitiesRequests, Facilities


def int_or_str(value):
	try:
		return int(value)
	except TypeError:
		return value


__version__ = "5.0.0"
VERSION = tuple(map(int_or_str, __version__.split(".")))

__all__ = ["SimConnect", "Request", "Event", "millis", "DWORD", "AircraftRequests", "AircraftEvents", "FacilitiesRequests"]