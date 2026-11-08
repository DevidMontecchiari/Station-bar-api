"""From the repository root: python extensions/frontend/run.py api-client"""
import argparse
import uvicorn
from app_server import create_app


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('variant', choices=['static', 'api-client', 'server-rendered'])
    parser.add_argument('--host', choices=['127.0.0.1', '0.0.0.0'], default='127.0.0.1')
    parser.add_argument('--port', type=int)
    parser.add_argument('--api-url', default='http://127.0.0.1:8000')
    args = parser.parse_args()
    port = args.port or {'static': 8080, 'api-client': 8081, 'server-rendered': 8082}[args.variant]
    if not 1 <= port <= 65535:
        parser.error('Port must be between 1 and 65535')
    uvicorn.run(create_app(args.variant, args.api_url), host=args.host, port=port)


if __name__ == '__main__':
    main()
