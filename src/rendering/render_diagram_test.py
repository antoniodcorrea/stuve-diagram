from src.rendering import render_diagram as module
from src.rendering.render_diagram import render_diagram


class _FakeFigure:
    def __init__(self):
        self.savefig_calls = []

    def savefig(self, path, **kwargs):
        self.savefig_calls.append((path, kwargs))


def _patch_pipeline(monkeypatch):
    """Replace matplotlib and every draw step with call recorders."""
    calls = []
    figure = _FakeFigure()
    ax = object()

    monkeypatch.setattr(module.plt, "subplots", lambda figsize: (figure, ax))
    monkeypatch.setattr(module.plt, "close", lambda fig: calls.append(("close", fig)))
    for name in ("draw_background", "draw_profile", "draw_altitude_labels",
                 "draw_wind_barbs", "configure_axes"):
        monkeypatch.setattr(module, name,
                            lambda *args, _name=name: calls.append((_name, args)))
    return calls, figure, ax


def test_runs_every_draw_step_on_the_axes(monkeypatch):
    calls, _figure, ax = _patch_pipeline(monkeypatch)
    render_diagram(sounding="S", subtitle="T", output_path="out.png")
    step_names = [name for name, _ in calls if name != "close"]
    assert step_names == [
        "draw_background", "draw_profile", "draw_altitude_labels",
        "draw_wind_barbs", "configure_axes"]
    # Every step draws on the same axes returned by plt.subplots.
    assert all(args[0] is ax for name, args in calls if name != "close")


def test_passes_sounding_and_subtitle_through(monkeypatch):
    calls, _figure, _ax = _patch_pipeline(monkeypatch)
    render_diagram(sounding="S", subtitle="T", output_path="out.png")
    by_step = dict(calls)
    assert by_step["draw_profile"][1] == "S"
    assert by_step["configure_axes"][1] == "T"


def test_saves_to_the_output_path(monkeypatch):
    _calls, figure, _ax = _patch_pipeline(monkeypatch)
    render_diagram(sounding="S", subtitle="T", output_path="out.png")
    assert len(figure.savefig_calls) == 1
    path, kwargs = figure.savefig_calls[0]
    assert path == "out.png"
    assert kwargs["dpi"] == module.FIGURE_DPI


def test_closes_the_figure(monkeypatch):
    calls, figure, _ax = _patch_pipeline(monkeypatch)
    render_diagram(sounding="S", subtitle="T", output_path="out.png")
    assert ("close", figure) in calls
