from passlib.context import CryptContext
import httpx

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_geo_location(client_ip: str) -> dict:
    """
    Calls ip-api.com (or any other service) to get location data.
    Returns a dict with 'country', 'regionName', 'city', etc.
    """
    try:
        url = f"http://ip-api.com/json/{client_ip}?fields=country,regionName,city,status,message"
        r = httpx.get(url, timeout=5.0)
        r.raise_for_status()
        data = r.json()
        if data.get("status") == "success":
            return data
        else:
            return None
    except httpx.ConnectTimeout:
        print("Connection timed out when trying to reach the geolocation API.")
        return {}
    except httpx.ReadTimeout:
        print("The geolocation API took too long to respond (read timeout).")
        return {}
    except httpx.HTTPStatusError as exc:
        print(f"HTTP error: {exc.response.status_code} - {exc.response.text}")
        return {}
    except httpx.RequestError as exc:
        print(f"Request error while trying to reach {exc.request.url!r}: {exc}")
        return {}
