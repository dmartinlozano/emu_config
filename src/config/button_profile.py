SEMANTIC_BUTTONS: list[tuple[str, str]] = [
    ("BTN_A",      "A / Cross"),
    ("BTN_B",      "B / Circle"),
    ("BTN_X",      "X / Square"),
    ("BTN_Y",      "Y / Triangle"),
    ("BTN_L1",     "L1 (shoulder)"),
    ("BTN_R1",     "R1 (shoulder)"),
    ("BTN_L2",     "L2 (trigger)"),
    ("BTN_R2",     "R2 (trigger)"),
    ("BTN_L3",     "L3 (left stick click)"),
    ("BTN_R3",     "R3 (right stick click)"),
    ("BTN_START",  "Start / Menu"),
    ("BTN_SELECT", "Select / Back"),
]

# Standard HID gamepad: Linux input code → Android keycode
LINUX_TO_ANDROID: dict[int, int] = {
    0x130: 96,   # BTN_A / BTN_SOUTH
    0x131: 97,   # BTN_B / BTN_EAST
    0x133: 99,   # BTN_X / BTN_NORTH
    0x134: 100,  # BTN_Y / BTN_WEST
    0x136: 102,  # BTN_TL  → L1
    0x137: 103,  # BTN_TR  → R1
    0x138: 104,  # BTN_TL2 → L2
    0x139: 105,  # BTN_TR2 → R2
    0x13a: 109,  # BTN_SELECT
    0x13b: 108,  # BTN_START
    0x13d: 106,  # BTN_THUMBL → L3
    0x13e: 107,  # BTN_THUMBR → R3
}

# Flutter logical key label → Android keycode (D-pad and any keys with non-empty labels)
FLET_KEY_TO_ANDROID: dict[str, int] = {
    "Arrow Up":                  19,
    "Arrow Down":                20,
    "Arrow Left":                21,
    "Arrow Right":               22,
    "Game Button A":             96,
    "Game Button B":             97,
    "Game Button C":             98,
    "Game Button X":             99,
    "Game Button Y":             100,
    "Game Button Z":             101,
    "Game Button L1":            102,
    "Game Button R1":            103,
    "Game Button L2":            104,
    "Game Button R2":            105,
    "Game Button Thumb Left":    106,
    "Game Button Thumb Right":   107,
    "Game Button Start":         108,
    "Game Button Select":        109,
    "Game Button Mode":          110,
    "Enter":                     66,
    "Escape":                    111,
    " ":                         62,
}

# Default profile: Retroid Pocket / standard Android gamepad (Android keycodes)
DEFAULT_PROFILE: dict[str, int] = {
    "BTN_A":      96,
    "BTN_B":      97,
    "BTN_X":      99,
    "BTN_Y":      100,
    "BTN_L1":     102,
    "BTN_R1":     103,
    "BTN_L2":     104,
    "BTN_R2":     105,
    "BTN_L3":     106,
    "BTN_R3":     107,
    "BTN_START":  108,
    "BTN_SELECT": 109,
}
