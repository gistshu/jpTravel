from math import asin, cos, radians, sin, sqrt

import httpx
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.repositories.castle_repository import CastleRepository
from app.schemas.castle import NearbyPlaceRead

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
DEFAULT_RADIUS_METERS = 1500
MAX_RESULTS = 80
MIN_RADIUS_METERS = 5
MAX_RADIUS_METERS = 3000


class NearbyPlaceService:
    """Service for OpenStreetMap nearby POI lookup."""

    def __init__(self, db_session: Session) -> None:
        self.castle_repository = CastleRepository(db_session)

    async def list_nearby_places(
        self,
        castle_id: int,
        radius_meters: int = DEFAULT_RADIUS_METERS,
    ) -> list[NearbyPlaceRead]:
        """Return nearby OSM POIs around one castle."""
        castle = self.castle_repository.get_by_id(castle_id)
        if castle is None:
            raise ResourceNotFoundError("城堡不存在")

        return await self.list_nearby_places_by_coordinate(
            castle.latitude,
            castle.longitude,
            radius_meters,
        )

    async def list_nearby_places_by_coordinate(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int,
    ) -> list[NearbyPlaceRead]:
        """Return nearby OSM POIs around a coordinate."""
        query = _build_overpass_query(latitude, longitude, radius_meters)
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.post(
                    OVERPASS_URL,
                    data={"data": query},
                    headers={
                        "User-Agent": "JPTravel/0.1 (+http://127.0.0.1:8000)",
                    },
                )
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError):
            return []

        places = []
        seen: set[tuple[str, str]] = set()
        for element in payload.get("elements", []):
            place = _build_place_read(element, latitude, longitude)
            if place is None:
                continue
            identity = (place.osm_type, place.osm_id)
            if identity in seen:
                continue
            seen.add(identity)
            places.append(place)

        return sorted(places, key=lambda place: place.distance_meters)[:MAX_RESULTS]


def _build_overpass_query(latitude: float, longitude: float, radius_meters: int) -> str:
    radius = max(MIN_RADIUS_METERS, min(radius_meters, MAX_RADIUS_METERS))
    filters = [
        '["tourism"~"attraction|museum|viewpoint|theme_park|gallery|zoo"]',
        '["historic"]',
        '["amenity"~"restaurant|cafe|fast_food|bar|pub|ice_cream|food_court"]',
        '["shop"]',
    ]
    selectors = []
    for selector_filter in filters:
        selectors.extend(
            [
                f'node(around:{radius},{latitude},{longitude})["name"]{selector_filter};',
                f'way(around:{radius},{latitude},{longitude})["name"]{selector_filter};',
                f'relation(around:{radius},{latitude},{longitude})["name"]{selector_filter};',
            ],
        )
    return f"""
        [out:json][timeout:10];
        (
          {"".join(selectors)}
        );
        out center tags {MAX_RESULTS * 2};
    """


def _build_place_read(
    element: dict,
    castle_latitude: float,
    castle_longitude: float,
) -> NearbyPlaceRead | None:
    tags = element.get("tags") or {}
    name = str(tags.get("name") or tags.get("name:ja") or "").strip()
    if not name:
        return None

    latitude = element.get("lat") or element.get("center", {}).get("lat")
    longitude = element.get("lon") or element.get("center", {}).get("lon")
    if latitude is None or longitude is None:
        return None

    osm_type = str(element.get("type") or "node")
    osm_id = str(element.get("id") or "")
    if not osm_id:
        return None

    return NearbyPlaceRead(
        name=name,
        category=_category_from_tags(tags),
        latitude=float(latitude),
        longitude=float(longitude),
        distance_meters=round(
            _distance_meters(
                castle_latitude,
                castle_longitude,
                float(latitude),
                float(longitude),
            ),
        ),
        address=_address_from_tags(tags),
        osm_type=osm_type,
        osm_id=osm_id,
        osm_url=f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
    )


def _category_from_tags(tags: dict) -> str:
    amenity = tags.get("amenity")
    shop = tags.get("shop")
    tourism = tags.get("tourism")
    if tourism or tags.get("historic"):
        return "attraction"
    if amenity in {"restaurant", "fast_food", "food_court", "ice_cream"}:
        return "food"
    if amenity == "cafe":
        return "cafe"
    if amenity in {"bar", "pub"}:
        return "food"
    if shop:
        return "shop"
    return "other"


def _address_from_tags(tags: dict) -> str:
    parts = [
        tags.get("addr:province"),
        tags.get("addr:city"),
        tags.get("addr:suburb"),
        tags.get("addr:quarter"),
        tags.get("addr:street"),
        tags.get("addr:housenumber"),
    ]
    return "".join(str(part) for part in parts if part)


def _distance_meters(
    start_latitude: float,
    start_longitude: float,
    end_latitude: float,
    end_longitude: float,
) -> float:
    radius = 6_371_000
    lat1 = radians(start_latitude)
    lat2 = radians(end_latitude)
    delta_lat = radians(end_latitude - start_latitude)
    delta_lon = radians(end_longitude - start_longitude)
    haversine = (
        sin(delta_lat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    )
    return 2 * radius * asin(sqrt(haversine))
