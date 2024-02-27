"""
The BatchJSONLines class handles batching items then flushing to storage (local or S3 currently)
"""
import json
import time
from datetime import datetime
import threading
import uuid
import logging
import os
import boto3

logging.getLogger()
class BatchJSONLines:
    """
    The BatchJSONLines class handles batching items then flushing to S3
    
    Keyword arguments:
        buffer_limit -- Maximum number of items to buffer before flushing
        flush_interval -- Flush approximately every flush_interval seconds
        s3_bucket -- If provided, dump requests to S3 bucket instead of local file
    
    Example:
    buffer = BatchJSONLines(s3_bucket="XXXXXXXXX")
    buffer.add_request(request)
    
    """
    def __init__(self, buffer_limit=100, flush_interval=60, prefix="/tmp"):
        self.requests = []
        self.s3 = boto3.client("s3")
        self.lock = threading.Lock()
        if prefix.endswith("/"):
            self.prefix = prefix
        else:
            self.prefix = prefix + "/"
        self.buffer_limit = (
            buffer_limit  # Buffer up to buffer_limit items before flushing
        )
        self.dump_interval = (
            flush_interval  # Buffer approximately every dump_interval second
        )
        self.next_flush_time = time.time() + self.dump_interval
        # start a thread running self.dump_timer() and pass it a reference to self
        self.background_thread = threading.Thread(target=self._flush_thread, args=())
        self.stopping = False
        self.background_thread.start()

    def add_request(self, request):
        """
        Add a request to the buffer. 
        If the buffer is full, dump the buffer to S3. 
        If the buffer is empty, start the next flush timer.
        
        Keyword arguments:
            request -- The request to add to the buffer. 
                This should be any JSON serializable object
        """
        with self.lock:
            self.requests.append(request)
        if len(self.requests) >= self.buffer_limit:
            threading.Thread(target=self.flush, args=()).start()

    def shutdown(self):
        """
        Gracefully shutdown
        """
        self.stopping = True
        logging.info("Shutting down")
        self.flush()
        self.background_thread.join()
        logging.info("Shutdown complete")

    def flush(self):
        """
        Flush the buffer to S3. 
        If the buffer is empty, start the next flush timer.
        
        Keyword arguments:
            None
        
        Returns:
            None
        
        Raises:
            None
        """
        self.next_flush_time = time.time() + self.dump_interval
        if len(self.requests) > 0:
            with self.lock:
                my_requests = self.requests[: self.buffer_limit]
                self.requests = self.requests[self.buffer_limit :]
            now = datetime.now()
            filename = f"{now.year:04}/{now.month:02}/{now.day:02}/{now.hour:02}/{str(uuid.uuid4())}.json"
            # Create string to write
            output = "\n".join([json.dumps(i, default=str) for i in my_requests]) + "\n"
            logging.info("Writing %d items to %s", len(my_requests), filename)
            # Dump requests to file if s3_bucket is None, otherwise to s3
            if self.prefix.startswith("s3://"):
                prefix = self.prefix[5:]
                bucket, key = prefix.split("/", 1)
                self.s3.put_object(Bucket=bucket, Key=key+filename, Body=output)
            else:
                os.makedirs(os.path.dirname(self.prefix+filename), exist_ok=True)
                with open(self.prefix+filename, "w", encoding="utf-8") as f:
                    f.write(output)
        else:
            logging.debug("No requests to dump")

    def _flush_thread(self):
        """
        A timer that runs self.flush() every self.dump_interval seconds
        Keyword arguments:
            None
        
        Returns:
            None
        
        Raises:
            None
        """
        while not self.stopping:
            time.sleep(2)
            if self.next_flush_time < time.time():
                self.flush()

    def __exit__(self, *exc):
        """
        Flush the buffer when exiting the context.
        
        Keyword arguments:
            None
        
        Returns:
            None
        
        Raises:
            None
        """
        self.stopping = True
        while len(self.requests) > 0:
            self.flush()

    def __del__(self):
        """
        Flush the buffer when the object is deleted.
        
        Keyword arguments:
            None
        
        Returns:
            None
        
        Raises:
            None
        """
        self.stopping = True
        while len(self.requests) > 0:
            self.flush()
        logging.debug("BatchJSONLines flushed during deletion")
