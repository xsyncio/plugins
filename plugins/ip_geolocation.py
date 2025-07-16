from osintbuddy.elements import Title, Empty, TextInput
import osintbuddy as ob

class IPGeolocation(ob.Plugin):
    label = "IP Geolocation"
    is_available = False
    entity = "map-pin"
    author = "OSIB"
    color = "#FFCC33"
    entity = [
        [
            TextInput(label="City", icon="map-pin"),
            TextInput(label="ASN", icon="access-point"),
        ],
        [
            TextInput(label="State", icon="map-pin"),
            TextInput(label="Hostname", icon="access-point"),
        ],
        [
            TextInput(label="Country", icon="map-pin"),
            TextInput(label="Range", icon="access-point"),
        ],
        [
            TextInput(label="Postal", icon="map-pin"),
            TextInput(label="Company", icon="trademark"),
        ],
        [
            TextInput(label="Timezone", icon="clock"),
            TextInput(label="Hosted domains", icon="access-point"),
        ],
        [
            TextInput(label="Coordinates", icon="map-pin"),
            TextInput(label="Privacy", icon="network"),
        ],
        [
            TextInput(label="Abuse Contact", icon="map-pin"),
            TextInput(label="Anycast", icon="network"),
        ],
        [
            Empty(),
            TextInput(label="ASN type", icon="access-point"),
        ],
    ]

