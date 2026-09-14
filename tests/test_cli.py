from types import SimpleNamespace

from ne111_checker import cli


def test_ctrl_c_stops_streamlit_process(monkeypatch) -> None:
    class Process:
        def __init__(self) -> None:
            self.terminated = False
            self.wait_calls = 0

        def wait(self, timeout: float | None = None) -> int:
            self.wait_calls += 1
            if self.wait_calls == 1:
                raise KeyboardInterrupt
            return 0

        def terminate(self) -> None:
            self.terminated = True

        def kill(self) -> None:
            raise AssertionError("The process should stop after terminate().")

    process = Process()
    monkeypatch.setattr(cli, "assignment_ids", lambda: ("A1",))
    monkeypatch.setattr(
        cli,
        "get_assignment",
        lambda _: SimpleNamespace(id="A1", expected_filename="A1.ipynb"),
    )
    monkeypatch.setattr(cli.subprocess, "Popen", lambda *args, **kwargs: process)

    assert cli.main(["A1"]) == 130
    assert process.terminated
    assert process.wait_calls == 2
