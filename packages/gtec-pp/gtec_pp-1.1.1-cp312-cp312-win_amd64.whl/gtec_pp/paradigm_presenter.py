import ctypes
from .imp.pplib import pplib


class ParadigmPresenter:

    _id: str

    def __init__(self):
        self.constants = pplib.GetConstants().contents
        mode = self.constants.PRESENTERMODE_STANDALONE
        try:
            ll = self.constants.LOGTYPE_LOGIC + self.constants.LOGTYPE_TIMING
            success = self.setup(presenter_mode=mode, log_level=ll)
        except Exception:
            raise RuntimeError("Failed to set up paradigm presenter. "
                               "Make sure the license is valid.")
        if not success:
            raise RuntimeError("Failed to set up paradigm presenter.")

    def setup(self, presenter_mode, log_level) -> bool:
        import random
        self._id = f"{random.randint(0, 16**12 - 1):012x}"
        id_cstr = ctypes.c_char_p(self._id.encode())
        success = pplib.Setup(presenter_mode, log_level, ctypes.byref(id_cstr))
        return success

    def is_presenter_connected(self) -> bool:
        return pplib.IsPresenterConnected(self._id.encode())

    def open_window(self, window_type):
        pplib.OpenWindow(window_type, self._id.encode())

    def open_window_config(self, is_fullscreen, left, top, width, height, window_type):  # noqa: E501
        pplib.OpenWindowConfig(is_fullscreen, left, top, width, height, window_type, self._id.encode())  # noqa: E501

    def close_windows(self):
        pplib.CloseWindows(self._id.encode())

    def create_task_sequence(self) -> bool:
        return pplib.CreateTaskSequence(self._id.encode())

    def load_paradigm(self, file_name) -> bool:
        return pplib.LoadParadigm(file_name.encode(),
                                  self._id.encode())

    def start_paradigm(self) -> bool:
        return pplib.StartParadigm(self._id.encode())

    def pause_paradigm(self) -> bool:
        return pplib.PauseParadigm(self._id.encode())

    def resume_paradigm(self) -> bool:
        return pplib.ResumeParadigm(self._id.encode())

    def stop_paradigm(self) -> bool:
        return pplib.StopParadigm(self._id.encode())

    def reset_paradigm(self) -> bool:
        return pplib.ResetParadigm(self._id.encode())

    def shutdown(self) -> bool:
        return pplib.Shutdown(self._id.encode())

    def get_state(self) -> bool:
        return pplib.GetState(self._id.encode())

    def get_return_value(self) -> bool:
        return pplib.GetReturnValue(self._id.encode())

    def get_last_error(self) -> bool:
        error_message_ptr = ctypes.c_char_p()
        success = pplib.GetLastError(ctypes.byref(error_message_ptr),
                                     self._id.encode())
        return success, error_message_ptr.value.decode() if success else None

    def get_next_task_switch_time_ms(self, sample_time_ms) -> bool:
        return pplib.GetNextTaskSwitchTimeMs(sample_time_ms.encode())

    def get_task_id(self, sample_time_ms) -> bool:
        return pplib.GetTaskId(sample_time_ms.encode())

    def set_time(self, sample_time_ms) -> bool:
        return pplib.SetTime(sample_time_ms.encode())

    def get_api_state(self) -> bool:
        return pplib.GetApiState(self._id.encode())

    def log(self, log_type, message):
        pplib.Log(self._id.encode(), log_type, message.encode())
