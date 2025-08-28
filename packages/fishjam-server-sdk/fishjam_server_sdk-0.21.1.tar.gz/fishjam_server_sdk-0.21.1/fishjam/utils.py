from fishjam.errors import MissingFishjamIdError


def get_fishjam_url(fishjam_id: str | None, fishjam_url: str | None) -> str:
    if not fishjam_url and not fishjam_id:
        raise MissingFishjamIdError

    if fishjam_url:
        return fishjam_url

    return f"https://fishjam.io/api/v1/connect/{fishjam_id}"
