import argparse
import os

def main():
    from .app import build_app, load_store, seed_jobs, save_store, MOCK_MODE

    parser = argparse.ArgumentParser(
        prog="data-monitor-drm",
        description="Run the Data Monitor DRM dashboard server."
    )
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8050")))
    parser.add_argument("--debug", action="store_true", default=False)
    parser.add_argument("--mock", type=int, choices=[0, 1], default=None,
                        help="Override MOCK_MODE env (1 on, 0 off)")
    parser.add_argument("--refresh", type=int, default=None,
                        help="Override REFRESH_MS in seconds, e.g. 30")
    args = parser.parse_args()

    if args.mock is not None:
        os.environ["MOCK_MODE"] = "1" if args.mock == 1 else "0"
    if args.refresh is not None:
        os.environ["REFRESH_MS"] = str(int(args.refresh) * 1000)

    app = build_app()

    try:
        if os.getenv("MOCK_MODE", "1") == "1" or MOCK_MODE:
            s = load_store()
            if not s.get("jobs"):
                seed_jobs(s)
                save_store(s)
    except Exception:
        pass

    run = getattr(app, "run", None)
    if callable(run):
        run(host=args.host, port=args.port, debug=args.debug)
    else:
        app.run_server(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()