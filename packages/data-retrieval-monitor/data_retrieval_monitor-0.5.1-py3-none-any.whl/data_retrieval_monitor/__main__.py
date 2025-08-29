#!/usr/bin/env python3
import argparse, os, sys

def main():
    p = argparse.ArgumentParser(prog="data-monitor-drm")
    p.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    p.add_argument("--port", type=int, default=int(os.getenv("PORT", "8050")))
    p.add_argument("--debug", action="store_true", default=False)
    p.add_argument("--refresh", type=int, default=None, help="Refresh period in seconds")
    p.add_argument("--timezone", default=None)
    p.add_argument("--store-backend", choices=["memory", "file"], default=None)
    p.add_argument("--store-path", default=None)
    args = p.parse_args()

    if args.refresh is not None:
        os.environ["REFRESH_MS"] = str(int(args.refresh) * 1000)
    if args.timezone:
        os.environ["APP_TIMEZONE"] = args.timezone
    if args.store_backend:
        os.environ["STORE_BACKEND"] = args.store_backend
    if args.store_path:
        os.environ["STORE_PATH"] = args.store_path

    # Import AFTER env is set
    from .app import app

    app.run_server(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()