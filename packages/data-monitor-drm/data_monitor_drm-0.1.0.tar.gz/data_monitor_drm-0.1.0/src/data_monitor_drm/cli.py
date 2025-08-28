from .app import app, load_store, seed_jobs, save_store, MOCK_MODE
import argparse

def main():
    p = argparse.ArgumentParser(prog="data-monitor-drm")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8050)
    args = p.parse_args()

    # seed once if MOCK_MODE and empty
    if MOCK_MODE:
        s = load_store()
        if not s.get("jobs"):
            seed_jobs(s)
            save_store(s)

    app.run_server(host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()
