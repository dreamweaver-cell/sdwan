def get_device_type(cisco_type: str) -> str:
    """Maps Cisco type to device type."""
    TYPES = {
        "ISR4351": "vedge-ISR-4351",
        "ISR4351/K9": "vedge-ISR-4351",
        "ISR4451-X/K9": "vedge-ISR-4451-X",
        "ISR4431/K9": "vedge-ISR-4431",
        "ISR4321/K9": "vedge-ISR-4321",
        "ISR4331/K9": "vedge-ISR-4331",
        "C1111-8P": "vedge-C1111-8P",
        "C1111-8PWA": "vedge-C1111-8PW",
        "C1111-8PWB": "vedge-C1111-8PW",
        "C1111-8PWE": "vedge-C1111-8PW",
        "C1111-8PWF": "vedge-C1111-8PW",
        "C1111-8PWQ": "vedge-C1111-8PW",
        "C1111-8PWR": "vedge-C1111-8PW",
        "C1111-8PWZ": "vedge-C1111-8PW",
    }
    if cisco_type in TYPES:
        return TYPES[cisco_type]
    else:
        raise ValueError('Unsupported Cisco device')
