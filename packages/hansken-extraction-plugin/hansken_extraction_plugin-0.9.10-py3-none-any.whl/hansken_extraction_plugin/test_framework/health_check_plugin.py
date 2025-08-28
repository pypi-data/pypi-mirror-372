#!/usr/bin/python3
"""Contains a health check script to check if an extraction plugin is healthy."""
import argparse

import grpc

from hansken_extraction_plugin.framework import Health_pb2, Health_pb2_grpc
from hansken_extraction_plugin.test_framework import FriendlyError


def _wait_for_ready(hostname: str, port: int):
    with grpc.insecure_channel(f'{hostname}:{port}') as channel:
        # wait for ready state of channel
        grpc.channel_ready_future(channel).result()
        stub = Health_pb2_grpc.HealthStub(channel)

        status = stub.Check(Health_pb2.HealthCheckRequest()).status
        if status == 1:
            return status

        raise FriendlyError('Plugin is unhealthy')


def main():
    """Run health check for an extraction plugin."""
    parser = argparse.ArgumentParser(prog='health_check',
                                     usage='%(prog)s [options]',
                                     description='A script to check if a plugin is healthy.')
    parser.add_argument('hostname', help='Hostname of the plugin')
    parser.add_argument('port', type=int, help='Port of the plugin')
    args = parser.parse_args()

    _wait_for_ready(args.hostname, args.port)


if __name__ == '__main__':
    main()
