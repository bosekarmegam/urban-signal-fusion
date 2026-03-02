import h3

def point_to_hex(lat: float, lng: float, resolution: int = 9) -> str:
    """Converts a lat/lon to H3 hex ID defaults to 9 (~174m edge)."""
    return h3.latlng_to_cell(lat, lng, resolution)

def get_hex_boundary(hex_id: str) -> list[tuple[float, float]]:
    """Returns lat/lon pairs forming the hexagon boundary."""
    return h3.cell_to_boundary(hex_id)

def get_parent(hex_id: str, parent_resolution: int = 7) -> str:
    """Gets the parent broader hex area for spatial rollups."""
    return h3.cell_to_parent(hex_id, parent_resolution)
