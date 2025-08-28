import argparse
import sys

from . import _core


def main():
    """
    License Server入口函数
    启动许可证服务器
    """
    parser = argparse.ArgumentParser(
        description="GAXKey License Server - When no arguments are provided, the License Server will start by default"
    )

    parser.add_argument("--list-apps", nargs="?", const="", help="List client application information")
    parser.add_argument("--query-app", help="Query specific client application information")
    parser.add_argument("--approve", nargs='+', metavar='ARGS', help="Approve a client application, format: <clientId>")
    parser.add_argument("--set-renewable", nargs='+', metavar='ARGS', help="Set renewal status, format: <clientId> <enable|disable> [duration(s)]")
    # parser.add_argument("--duration", type=int, help="Set renewal duration (seconds)")

    args = parser.parse_args()

    try:
        # 在进入程序时，初始化数据库
        _core.init_db()
        if args.list_apps is not None:
            _core.list_apps(False)
        # elif args.License:
        #     _core.set_license_expiration(args.License)
        elif args.query_app:
            _core.query_app(args.query_app, False)
        elif args.approve:
            if len(args.approve) == 1:
                client_id = args.approve[0]
                _core.approve_app(client_id, "seedkcompiler")
            else:
                raise ValueError("Invalid format: --approve requires <clientId>")
        elif args.set_renewable:
            if len(args.set_renewable) == 2:
                client_id, status = args.set_renewable
                if status in ["enable", "disable"]:
                    _core.set_renew_status(client_id, "seedkcompiler", status)
                else:
                    raise ValueError("Status must be 'enable' or 'disable'")
            elif len(args.set_renewable) == 3:
                client_id, status, duration = args.set_renewable
                if status in ["enable", "disable"]:
                    if status == "enable":
                        _core.set_renew_status(client_id, "seedkcompiler", status, int(duration))
                    else:
                        # 对于disable状态，提供duration参数时直接报错
                        raise ValueError("Duration parameter is not allowed for disable status")
                else:
                    raise ValueError("Status must be 'enable' or 'disable'")
            else:
                raise ValueError("Invalid format: --set-renewable requires <clientId> <enable|disable> [duration(s)]")
        # elif args.duration:
        #     _core.set_duration(args.duration)
        else:
            # Default: start license server
            print("Starting GAXKey License Server...")
            if _core.start_license_server():
                return 0
            return -1
    except Exception as e:
        print(f"Error: {e}")
        return -1

    return 0


if __name__ == "__main__":
    sys.exit(main()) 