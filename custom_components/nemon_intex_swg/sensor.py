from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

SENSOR_TYPES = [
    (("display", "brightness"), "Display Brightness"),
    (("display", "current_code"), "Display Code"),
]

BOOL_SENSOR_TYPES = [
    (("display", "status"), "Display Status"),
    (("status", "boost"), "Boost Mode"),
    (("status", "sleep"), "Sleep Mode"),
    (("status", "o3_generation"), "O3 Generation"),
    (("status", "pump_low_flow"), "Low Flow Alarm"),
    (("status", "low_salt"), "Low Salt Alarm"),
    (("status", "high_salt"), "High Salt Alarm"),
    (("status", "service"), "Service Alarm"),
    (("mode", "working"), "Working Mode"),
    (("mode", "programming"), "Programming Mode")
]

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    client = data["client"]
    coordinator = data["coordinator"]

    entities = []

    for path, name in SENSOR_TYPES:
        entities.append(IntexSWGSensor(client, coordinator, path, name))

    for path, name in BOOL_SENSOR_TYPES:
        entities.append(IntexSWGBinarySensor(client, coordinator, path, name))

    async_add_entities(entities)

class IntexSWGSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, client, coordinator, path, name):
        super().__init__(coordinator)
        self._client = client
        self._path = path
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.name}_{"_".join(path)}"

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

class IntexSWGBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, client, coordinator, path, name):
        super().__init__(coordinator)
        self._client = client
        self._path = path
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.name}_{"_".join(path)}"

    @property
    def is_on(self) -> bool:
        data = self._client.data
        for key in self._path:
            data = data.get(key, {})
        # If boolean type, use directly
        if isinstance(data, bool):
            return data
        # Otherwise map string ON/OFF to boolean
        return str(data).upper() == "ON"

    @property
    def available(self) -> bool:
        return bool(self._client.data)

    @property
    def extra_state_attributes(self):
        return {}