"""Constants for SZÉP Card balance sensor."""
DOMAIN = "szep_card_balance"

CONF_CARD_NUMBER = "card_number"
CONF_CARD_CODE = "card_code"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 1200 # seconds
DEFAULT_ICON = "mdi:credit-card-outline"
DEFAULT_UNIT = "Ft"
DEFAULT_URL_API = "https://magan.szepkartya.otpportalok.hu/ajax/egyenleglekerdezes/"
DEFAULT_URL_HTML = "https://magan.szepkartya.otpportalok.hu/fooldal/"
