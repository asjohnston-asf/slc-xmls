import random

import boto3

queue_url = ''
sqs = boto3.client('sqs')


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


with open('slcs.txt') as f:
    granules = [line.strip() for line in f.readlines()]

n = 0
for batch in divide_chunks(granules, 10):
    entries = [{'Id': granule, 'MessageBody': granule} for granule in batch]
    sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)
    n += len(entries)
    print(n)
