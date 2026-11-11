"""Animation presets the play_animation action offers.

Every entry maps the preset name the user picks to a callable that
builds the animation with the arguments the Flitsmeister app uses.
"""

from collections.abc import Callable
from functools import partial

from flitsmeister_dot_ble import DotAnimation, DotSound, animations

PRESET_ANIMATIONS: dict[str, Callable[[], DotAnimation]] = {
    "startup": animations.startup,
    "fade_out": animations.fade_out,
    "speed_trap": animations.speed_trap,
    "speed_cam": animations.speed_cam,
    "traffic_camera": animations.traffic_camera,
    "avg_speed_check_start": animations.avg_speed_check_start,
    "avg_speed_check_end": animations.avg_speed_check_end,
    "traffic_jam_start": animations.traffic_jam_start,
    "traffic_jam_end": animations.traffic_jam_end,
    "police_hotspot": animations.police_hotspot,
    "roadworks": animations.roadworks,
    "ambulance": animations.ambulance,
    "fire_truck": animations.fire_truck,
    "police": animations.police,
    "emergency_vehicle": animations.emergency_vehicle,
    "railway_crossing": animations.railway_crossing,
    "wrong_way_driving": animations.wrong_way_driving,
    "wrong_way_driver": animations.wrong_way_driver,
    "reporting": animations.reporting,
    "brightness_sample": animations.brightness_sample,
    "orientation_sample": animations.orientation_sample,
    "updating": animations.updating,
    "accident": partial(animations.incident, speech=DotSound.SPEECH_ACCIDENT),
    "stationary_vehicle": partial(animations.incident, speech=DotSound.SPEECH_STATIONARY_VEHICLE),
    "object_on_road": partial(animations.incident, speech=DotSound.SPEECH_OBJECT_ON_ROAD),
    "animal_on_the_road": partial(animations.incident, speech=DotSound.SPEECH_ANIMAL_ON_THE_ROAD),
    "person_on_the_road": partial(animations.incident, speech=DotSound.SPEECH_PERSON_ON_THE_ROAD),
    "dangerous_situation": partial(animations.incident, speech=DotSound.SPEECH_DANGEROUS_SITUATION_1),
    "impact_attenuator": partial(animations.incident, speech=DotSound.SPEECH_IMPACT_ATTENUATOR),
    "poor_visibility": partial(animations.incident, speech=DotSound.SPEECH_POOR_VISIBILITY),
    "slippery_road": partial(animations.incident, speech=DotSound.SPEECH_SLIPPERY_ROAD),
    "bumpy_road": partial(animations.incident, speech=DotSound.SPEECH_BUMPY_ROAD),
    "lane_closed": partial(animations.lane_closure, speech=DotSound.SPEECH_LANE_CLOSED),
    "left_lane_closed": partial(animations.lane_closure, speech=DotSound.SPEECH_LEFT_LANE_CLOSED),
    "right_lane_closed": partial(animations.lane_closure, speech=DotSound.SPEECH_RIGHT_LANE_CLOSED),
}
