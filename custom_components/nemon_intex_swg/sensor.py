import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.core import callback
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_POWER_ENTITY

SENSOR_TYPES = [
    (("display", "brightness"), "Display Brightness"),
    (("display", "current_code"), "Display Code"),
    (("system", "uptime_seconds"), "Uptime (seconds)"),
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

    # Power sensor: only add if user configured one
    power_entity_id = entry.options.get(CONF_POWER_ENTITY)
    if power_entity_id:
        entities.append(IntexSWGPowerSensor(coordinator, entry.entry_id))

    async_add_entities(entities, update_before_add=True)

class IntexSWGSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, client, coordinator, path, name):
        super().__init__(coordinator)
        self._client = client
        self._path = path
        self._attr_name = name
        # unique_id: e.g. "nemon_intex_swg-XYZ_display_brightness"
        self._attr_unique_id = f"{coordinator.name}_{'_'.join(path)}"

        if self._path == ("system", "uptime_seconds"):
            self._attr_unit_of_measurement = "s"

    @property
    def state(self):
        data = self._client.data
        for key in self._path:
            data = data.get(key, {})
        return data if not isinstance(data, dict) else None

    @property
    def available(self):
        return bool(self._client.data)

class IntexSWGBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, client, coordinator, path, name):
        super().__init__(coordinator)
        self._client = client
        self._path = path
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.name}_{'_'.join(path)}"

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

class IntexSWGPowerSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry_id: str):
        super().__init__(coordinator)
        self._attr_name = "Power"
        self._attr_unique_id = f"{entry_id}_power"
        self._attr_unit_of_measurement = "W"

    @property
    def state(self):
        # returns None until client wrote a power value into data["power"]
        #return self.coordinator.data.get("power") if self.coordinator.data else None
        p = self.coordinator.data.get("power") if self.coordinator.data else None

        _LOGGER.debug("PowerSensor.state called, coordinator.data=%s → %s", self.coordinator.data, p)

        return p

    @property
    def available(self) -> bool:
        p = self.coordinator.data.get("power") if self.coordinator.data else None

        return isinstance(p, (int, float))
    
    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug("Coordinator new data: %s", self.coordinator.data)

        super()._handle_coordinator_update()    