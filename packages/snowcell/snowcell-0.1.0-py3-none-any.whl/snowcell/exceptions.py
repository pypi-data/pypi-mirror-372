import httpx

class SnowcellException(Exception):
    """Base class for all Snowcell SDK exceptions."""


class SnowcellError(SnowcellException):
    """Error from Snowcell's API."""

    def __init__(
        self,
        type: str | None = None,
        title: str | None = None,
        status: int | None = None,
        detail: str | None = None,
        instance: str | None = None,
    ) -> None:
        self.type = type
        self.title = title
        self.status = status
        self.detail = detail
        self.instance = instance
        super().__init__(self.__str__())

    @classmethod
    def from_response(cls, response: httpx.Response) -> "SnowcellError":
        try:
            data = response.json()
        except ValueError:
            data = {}

        return cls(
            type=data.get("type"),
            title=data.get("title"),
            detail=data.get("detail"),
            status=response.status_code,
            instance=data.get("instance"),
        )

    def to_dict(self) -> dict[str, str | int | None]:
        return {k: v for k, v in {
            "type": self.type,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
            "instance": self.instance,
        }.items() if v is not None}

    def __str__(self) -> str:
        return "Snowcell API Error:\n" + "\n".join(f"{k}: {v}" for k, v in self.to_dict().items())

    def __repr__(self) -> str:
        params = ", ".join(f"{k}={repr(v)}" for k, v in self.to_dict().items())
        return f"SnowcellError({params})"
