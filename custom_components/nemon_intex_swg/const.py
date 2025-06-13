from datetime import timedelta

DOMAIN = "nemon_intex_swg"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_POWER_ENTITY = "power_entity"
CONF_REBOOT_ENABLED = "reboot_enabled"
CONF_REBOOT_INTERVAL = "reboot_interval"

DEVICE_NAME = "Intex SWG"
DEVICE_MANUFACTURER = "INTEX"
DEVICE_MODEL = "ECO 6220 / CG-26670 / QS500"

DEFAULT_PORT = 8080
DEFAULT_SCAN_INTERVAL = 30  # seconds
DEFAULT_POWER_ENTITY = None
DEFAULT_REBOOT_ENABLED = False
DEFAULT_REBOOT_INTERVAL = 720  # minutes (12 hours)

PLATFORMS = ["sensor", "button"]

# https://pictogrammers.com/library/mdi/