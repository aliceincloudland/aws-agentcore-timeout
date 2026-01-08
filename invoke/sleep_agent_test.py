"""
Sleep Agent test - configurable duration
"""
import boto3
import json
import time
import logging
import os
import socket
from botocore.config import Config

# Configure aggressive TCP keep-alive to prevent GitHub Actions timeouts
def enable_socket_keepalive():
    """Enable aggressive TCP keep-alive probes"""
    original_socket = socket.socket
    
    def socket_with_keepalive(*args, **kwargs):
        sock = original_socket(*args, **kwargs)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        
        # Start probes after 60 seconds of inactivity
        if hasattr(socket, 'TCP_KEEPIDLE'):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
        
        # Send probe every 30 seconds
        if hasattr(socket, 'TCP_KEEPINTVL'):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
        
        # Give up after 3 failed probes
        if hasattr(socket, 'TCP_KEEPCNT'):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
        
        return sock
    
    socket.socket = socket_with_keepalive

# Enable keep-alive before any network operations
enable_socket_keepalive()

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('boto3').setLevel(logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.DEBUG)

def test_sleep_agent(duration_seconds=10):
    """Test sleep agent with configurable duration"""
    
    config = Config(
        read_timeout=900,  # 15 minutes
        connect_timeout=60,
        retries={'max_attempts': 1},
        # Force TCP keep-alive settings
        tcp_keepalive=True
    )
    
    client = boto3.client('bedrock-agentcore', region_name='us-west-2', config=config)
    
    payload = {
        'duration_seconds': duration_seconds,
        'test_type': 'sleep_test',
        'message': f'Testing {duration_seconds}s sleep duration'
    }
    
    session_id = f'sleep-test-{int(time.time())}-{int(time.time() * 1000000)}'
    
    print(f'🚀 SLEEP AGENT TEST: {duration_seconds}s duration')
    print(f'🎯 Session ID: {session_id}')
    print(f'⏱️  Expected: {duration_seconds} second sleep')
    print('')
    
    try:
        account_id = "724772064768"
        agent_arn = "arn:aws:bedrock-agentcore:us-west-2:724772064768:runtime/sleep_agent-kFTzKmC01Y"
        
        start_time = time.time()
        print(f"📡 Starting invoke at {time.strftime('%H:%M:%S')}")
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=json.dumps(payload)
        )
        
        # Read the streaming response body
        response_body = response['response'].read().decode('utf-8')
        
        # Replace the StreamingBody with decoded content for logging
        response_copy = response.copy()
        response_copy['response'] = response_body
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f'✅ SUCCESS: Response received after {duration:.1f} seconds')
        print(f'📋 Full Response Object: {response_copy}')
        print(f'⏰ Completed at {time.strftime("%H:%M:%S")}')
        
        # Try to parse response as JSON
        # try:
        #     response_json = json.loads(response_body)
        #     reported_duration = response_json.get('duration_seconds', 0)
        #     if abs(duration - duration_seconds) <= 2:  # Within 2 seconds tolerance
        #         print(f'🎉 Duration verification: PASSED ({duration:.1f}s ≈ {duration_seconds}s)')
        #         print(f'🔍 Agent reported: {reported_duration}s sleep')
        #     else:
        #         print(f'⚠️  Duration verification: Expected {duration_seconds}s, got {duration:.1f}s')
        # except json.JSONDecodeError:
        #     print(f'⚠️  Could not parse response as JSON')
            
    except Exception as e:
        duration = time.time() - start_time
        print(f'❌ FAILURE after {duration:.1f} seconds: {e}')

if __name__ == "__main__":
    # Test multiple durations between 290-330 seconds (4m50s - 5m30s) with keep-alive
    test_cases = [
        290,  # 4m50s
        295,  # 4m55s
        300,  # 5m00s
        310,  # 5m10s
        320,  # 5m20s
        325   # 5m25s
    ]
    
    for duration in test_cases:
        print("=" * 60)
        test_sleep_agent(duration)
        print("=" * 60)
        print()
        
        # Wait between tests
        if duration != test_cases[-1]:
            print("⏸️  Waiting 5 seconds before next test...")
            time.sleep(5)
