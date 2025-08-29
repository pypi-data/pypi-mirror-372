import httpx
from bs4 import BeautifulSoup

from invasync import FLASH_GALLERY_ENDPOINT, MAP_LOGIN_ENDPOINT, MAP_RESTORE_ENDPOINT


class FlashError(Exception):
    """An error happened with FlashInvaders API."""


class User:
    def __init__(
        self,
        name: str,
        flash_uid: str,
        map_email: str,
        map_password: str,
        map_token: str,
    ) -> None:
        self.name = name
        self.flash_uid = flash_uid
        self.map_email = map_email
        self.map_password = map_password
        self.map_token = map_token
        self._client = httpx.AsyncClient()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "flash_uid": self.flash_uid,
            "map_email": self.map_email,
            "map_password": self.map_password,
            "map_token": self.map_token,
        }

    async def run(self) -> None:
        try:
            await self._get_invaders()
            await self._update_map()
        except Exception as e:  # noqa: BLE001
            print(f"[!] [{self.name}] - {e.__class__.__name__}: {e}")
        finally:
            await self._client.aclose()

    async def _get_invaders(self) -> None:
        print(f"[+] [{self.name}] - Fetching flashed invaders")
        response = await self._client.get(f"{FLASH_GALLERY_ENDPOINT}{self.flash_uid}")
        if response.status_code != httpx.codes.OK:
            msg = f"HTTP Error {response.status_code}"
            raise FlashError(msg)
        data: dict = response.json()
        self.total_invaders = len(data["invaders"])
        self.invaders_payload = (
            "[" + ",".join([f'"{invader_id}"' for invader_id in data["invaders"]]) + "]"
        ).encode()

    async def _login_map(self) -> None:
        print(f"[+] [{self.name}] - Performing map login")
        response = await self._client.get(MAP_LOGIN_ENDPOINT)
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.find("input", attrs={"name": "_csrf_token"})["value"]  # type: ignore[index]
        response = await self._client.post(
            MAP_LOGIN_ENDPOINT,
            data={
                "_username": self.map_email,
                "_password": self.map_password,
                "_remember_me": "off",
                "_csrf_token": csrf_token,
            },
        )
        self.map_token = response.cookies.get("PHPSESSID")  # type: ignore[assignment]

    async def _update_map(self) -> None:
        print(f"[+] [{self.name}] - Updating map")
        response = await self._client.get(
            MAP_RESTORE_ENDPOINT,
            cookies={"PHPSESSID": self.map_token},
        )
        if response.status_code != httpx.codes.OK:
            await self._login_map()
            response = await self._client.get(
                MAP_RESTORE_ENDPOINT,
                cookies={"PHPSESSID": self.map_token},
            )

        soup = BeautifulSoup(response.text, "html.parser")
        self.csrf_token = soup.find(
            "input",
            attrs={"name": "restore[_token]"},
        )["value"]  # type: ignore[index]
        await self._client.post(
            MAP_RESTORE_ENDPOINT,
            data={
                "restore[_token]": self.csrf_token,
            },
            files={
                "restore[file]": (
                    "invaders.txt",
                    self.invaders_payload,
                    "text/plain",
                ),
            },
            cookies={"PHPSESSID": self.map_token},
        )
        print(
            f"[+] [{self.name}] - Updated user's map with {self.total_invaders} entries",
        )
