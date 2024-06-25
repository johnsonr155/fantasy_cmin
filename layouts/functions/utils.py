def get_username(href):
    try:
        return href.split("username=")[-1]

    except ValueError:
        return "Unknown user"


lens_1_categories = [
    "Mandatory Activities",
    "EOP",
    "STS",
    "HRE",
    "NAV",
    "CSC",
    "TEC",
    "Space Safety",
    "CIC",
]

lens_2_categories = [
    "Misc",
    "Space Domain Awareness",
    "Space Transportation",
    "Earth Applications",
    "In-Orbit Applications",
    "Space Science",
    "Space Exploration and Human Spaceflight",
]

