def main():
    import argparse

    parser = argparse.ArgumentParser(prog="redlite", description="CLI ops for redlite")
    subparsers = parser.add_subparsers(required=True, dest="cmd")

    parser_server = subparsers.add_parser("server", help="starts UI server")
    parser_server.add_argument("--port", "-p", type=int, default=8000, help="Server port")
    parser_server.add_argument("--skin", "-s", type=str, default="default", help="UI skin")

    parser_server_freeze = subparsers.add_parser(
        "server-freeze", help="generates files for a static website serving data"
    )
    parser_server_freeze.add_argument("outdir", type=str, help="Output directory")
    parser_server_freeze.add_argument("--skin", "-s", type=str, default="default", help="UI skin")

    parser_server = subparsers.add_parser("upload", help="Uploads all tasks to ZenoML (for review and analysis)")
    parser_server.add_argument("--api-key", "-k", help="Zeno API key (if not set, must be in ZENO_API_KEY env)")
    parser_server.add_argument(
        "--zeno-project", "-z", default="redlite", help='Name of the target Zeno project. Default is "redlite"'
    )

    args = parser.parse_args()
    if args.cmd == "server":
        from .server._app import main as server_main

        print(f"*** HTTP UI server. Skin={args.skin}")
        server_main(args.port, skin=args.skin)

    elif args.cmd == "server-freeze":
        from .server._app import freeze as server_freeze
        import asyncio

        print(f"*** Freezing UI server to {args.outdir}. Skin={args.skin}")
        asyncio.run(server_freeze(args.outdir, skin=args.skin))

    elif args.cmd == "upload":
        from .zeno.upload import upload

        upload(
            api_key=args.api_key,
            zeno_project=args.zeno_project,
        )


if __name__ == "__main__":
    main()
