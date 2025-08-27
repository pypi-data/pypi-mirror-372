import argparse
import sys
import json

from adaptsapi.generate_docs import post
from adaptsapi.config import load_token, load_default_endpoint


def main():
    default_ep = load_default_endpoint()
    parser = argparse.ArgumentParser(prog="adaptsapi")
    parser.add_argument(
        "--endpoint",
        default=default_ep,
        required=(default_ep is None),
        help="Full URL of the API endpoint (default from ./config.json)",
    )
    parser.add_argument(
        "--payload-file",
        type=argparse.FileType("r"),
        help="Path to JSON payload file (overrides inline --data)",
    )
    parser.add_argument("--data", help="Inline JSON payload string")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    token = load_token()
    # load payload
    if args.payload_file:
        payload = json.load(args.payload_file)
    elif args.data:
        payload = json.loads(args.data)
    else:
        print("Error: must specify --data or --payload-file", file=sys.stderr)
        sys.exit(1)

    resp = post(args.endpoint, token, payload, timeout=args.timeout)
    if resp.status_code >= 400:
        print(f"Error {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(resp.status_code)
    print(resp.text)


if __name__ == "__main__":
    main()
