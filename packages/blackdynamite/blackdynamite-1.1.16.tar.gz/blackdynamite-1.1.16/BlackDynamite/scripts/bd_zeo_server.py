#!/usr/bin/env python

import BlackDynamite as BD


def main(argv=None):
    parser = BD.bdparser.BDParser()
    group = parser.register_group("server")
    group.add_argument(
        "--action",
        type=str,
        choices=["stop", "start", "status"],
        help="Can be start stop or status",
        default="status",
    )

    params = parser.parseBDParameters(argv)
    if params["action"] == "stop":
        BD.base_zeo.BaseZEO.stopZdaemon()
    elif params["action"] == "status":
        BD.base_zeo.BaseZEO.statusZdaemon()
        BD.base_zeo.BaseZEO.statusConnection()
    elif params["action"] == "start":
        print("Server starting")
        base = BD.base.Base(start_daemon=True, **params)
        base.statusZdaemon()


if __name__ == "__main__":
    main()
