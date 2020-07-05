#!/usr/bin/env python3

import boto3
import time
import sys, os
import signal
import select
import threading
import argparse
from queue import Queue

q = Queue()
active = True

def signal_handler(signo, stack_frame):
    global active
    active = False

def readstdin():
    global active, q
    timeout=1

    while active:
        (ready, _, _) = select.select([sys.stdin], [], [], timeout)

        if ready:
            line = sys.stdin.readline()
            if not line:
                break
            q.put(line)

    active = False

def put_msgs(log_group_name, log_stream_name=None):
    global active, q

    # log_group_name = '/bodygram/masa-test-createami'
    if not log_stream_name:
        log_stream_name = "{}/{}/{}".format(int(time.time()) * 1000, os.uname()[1], os.getpid())

    logs_client = boto3.client('logs')

    logs_client.create_log_stream(
        logGroupName=log_group_name,
        logStreamName=log_stream_name,
    )

    seq_token=None
    def put_log_events(msgs:list):
        nonlocal seq_token
        req = {
            'logGroupName': log_group_name,
            'logStreamName': log_stream_name,
            'logEvents': msgs,
        }

        if seq_token:
            req['sequenceToken'] = seq_token

        res = logs_client.put_log_events(**req)
        seq_token = res['nextSequenceToken']
    
        return res

    def put_log_event(msg:str):
        return put_log_events([
            {
                'timestamp': int(time.time()) * 1000,
                'message': msg,
            }
        ])

    put_log_event('Init log stream')

    while active:
        log_events = []
        while q.qsize():
            msg = q.get_nowait()
            q.task_done()

            if msg:
                log_events.append({
                    'timestamp': int(time.time()) * 1000,
                    'message': msg}
                )

        if not log_events:
            time.sleep(1)
            continue
    
        put_log_events(log_events)

    put_log_event('Close log stream')

def handler():
    parser = argparse.ArgumentParser(description='stdin to cloudwatch')
    parser.add_argument('--log-group-name', help='Log Group Name', required=True)
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    t1 = threading.Thread(target=readstdin)
    t2 = threading.Thread(target=put_msgs, args=(args.log_group_name, ))
    t1.start()
    t2.start()
    t2.join()

if __name__ == "__main__":
    handler()