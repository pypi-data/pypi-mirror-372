from analyst_klondike.state.app_state import AppState


def select_is_in_teacher_mode(state: AppState) -> bool:
    return state.is_teacher_mode
