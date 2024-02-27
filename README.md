# Batch JSON Processing API

This project provides an API for batch processing JSON requests to be stored on Amazon S3 or other storage services. 
It buffers requests in memory and periodically flushes them to storage to avoid the small files problem.
This serves the same goal as the original AWS Kinesis Data Firehose before lots more features were added to that. 
This is designed to run in cluster, either as a sidecar or a service. 

# Why use this? 

AWS Kinesis Data Firehose is a great service, but initially we were troubleshooting problems that turnd out to be CoreDNS
(which doesn't auto scale in EKS). Once we developed this tho we realized there was no reason to pay for firehose when we
had the same thing running locally on the pods - This was a trivial cost savings but also allowed us more flexibility to have
faster flushes for troubleshooting if needed.

# Why JSONL / JSON Lines format? 

Snowflake uess this format was the original use case, however we are also planning to use this AWS Athena for cheaper debug logs

# Configuration

The following environment variables can be used to configure the behavior:

`PREFIX` - The directory or S3 prefix to store flushed requests (default: /tmp/)

`FLUSH_INTERVAL` - How often to flush buffered requests, in seconds (default: 120, max: 900)

`BUFFER_LIMIT` - Maximum number of requests to buffer before flushing (default: 100)

# API

The API is exposed on port 8000 to accept POST requests. JSON payloads will be buffered and later flushed to storage.

## Sample request via curl:
    curl -X POST \
    http://localhost:8000/send \
    -H 'Content-Type: application/json' \
    -d '{"key":"value"}'
