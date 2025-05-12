from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

# Definition der zu erzeugenden Sensoren (Pfad im JSON, Anzeigename, Einheit optional)
SENSOR_TYPES = [
    (("display", "status"), "Display Status"),
    (("display", "brightness"), "Display Brightness"),
    (("display", "current_code"), "Display Code"),
    (("status", "power"), "Pump Power"),
    (("status", "boost"), "Boost Mode"),
    (("status", "sleep"), "Sleep Mode"),
    (("status", "o3_generation"), "O3 Generation"),
    (("status", "pump_low_flow"), "Low Flow Alarm"),
    (("status", "low_salt"), "Low Salt Alarm"),
    (("status", "high_salt"), "High Salt Alarm"),
    (("status", "service"), "Service Alarm"),
    (("mode", "working"), "Working Mode"),
    (("mode", "programming"), "Programming Mode"),
]

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    client = data["client"]
    coordinator = data["coordinator"]

    entities = []
    for path, name in SENSOR_TYPES:
        entities.append(IntexSWGSensor(client, coordinator, path, name))
    async_add_entities(entities)

class IntexSWGSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, client, coordinator, path, name):
        super().__init__(coordinator)
        self._client = client
        self._path = path
        self._attr_name = name

    @property
    def unique_id(self):
        return f"{self.coordinator.name}_{"_".join(self._path)}"

    @property
    def state(self):
        data = self._client.data
        for key in self._path:
            data = data.get(key, {})
        return data if not isinstance(data, dict) else None

    @property
    def available(self):
        return bool(self._client.data)

    @property
    def extra_state_attributes(self):
        return {}