import argparse
import sys

from google_docs_mcp.clients.google_auth import (
    authorize_console,
    authorize_interactive,
    revoke_local,
    token_info,
)
from google_docs_mcp.server import mcp


parser = argparse.ArgumentParser(prog="google-docs-mcp", description="Google Docs MCP CLI")
sub = parser.add_subparsers(dest="cmd")

# Server subcommand
p_server = sub.add_parser("server", help="Run the MCP server")
p_server.add_argument(
    "--transport",
    choices=["stdio", "http", "sse", "streamable-http"],
    default="stdio",
    help="Transport to use for the server (default: stdio)",
)

# Auth subcommand
p_auth = sub.add_parser("auth", help="Authorize with Google OAuth")
sub_auth = p_auth.add_subparsers(dest="subcmd")

p_authorize = sub_auth.add_parser("authorize", help="Authorize with Google OAuth")
# p_authorize.add_argument("-c", "--console", action="store_true", help="Use console flow (no browser)")
p_authorize.add_argument("-f", "--force", action="store_true", help="Force re-authorization (ignore existing token)")

sub_auth.add_parser("token-info", help="Show current token info and scope differences")
sub_auth.add_parser("revoke", help="Remove local token (does not remote-revoke)")


def main(argv: list[str] | None = None) -> None:
    args = parser.parse_args(argv)
    match args.cmd:
        case "server":
            mcp.run(transport=args.transport)
        case "auth":
            match args.subcmd:
                case "authorize":
                    if getattr(args, "console", False):
                        authorize_console(force=args.force)
                    else:
                        authorize_interactive(force=args.force)
                case "token-info":
                    info = token_info()
                    for k, v in info.model_dump(exclude_none=True).items():
                        print(f"{k}: {v}")
                case "revoke":
                    print(revoke_local())
                case _:
                    p_auth.print_help()
                    sys.exit(2)
        case _:
            parser.print_help()
            sys.exit(2)


if __name__ == "__main__":
    main()
