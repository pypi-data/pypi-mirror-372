# data-monitor-drm

Dash-based job monitor (Live/Backfill) with collapsible table (run_type → dataset → stage),
clickable KPIs and two status-mix pies. Includes a minimal CLI:

```bash
data-monitor-drm --host 0.0.0.0 --port 8050
```
**Important:** If you have an old `setup.cfg` in the project root, **delete it**, or at least remove any `[egg_info] egg_base = src` lines—this is often the direct cause of your error.

### 2) Build and (optionally) upload
```bash
python -m pip install --upgrade build twine
python -m build
```
# To TestPyPI:
# python -m twine upload -r testpypi dist/*

# To main PyPI (requires a real PyPI token in ~/.pypirc):
# python -m twine upload dist/*