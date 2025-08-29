from dataclasses import dataclass
from analyst_klondike.state.app_state import AppState


def current_file_path(state: AppState) -> tuple[str, str]:
    return (
        state.current.opened_file_path,
        state.current.opened_file_name
    )


@dataclass
class VersionsInfo:
    app_version: str
    version_in_file: str
    is_file_compatible: bool


def versions(state: AppState) -> VersionsInfo:
    app_ver = state.current.app_version
    min_sup_ver = state.current.opened_file_min_supported_app_version

    return VersionsInfo(
        app_version=app_ver,
        version_in_file=min_sup_ver,
        is_file_compatible=is_compatible(app_ver, min_sup_ver)
    )


def is_compatible(app_ver: str, min_sup_ver: str) -> bool:
    av_tuple = app_ver.split(".")
    msp_tuple = min_sup_ver.split(".")
    return av_tuple >= msp_tuple
