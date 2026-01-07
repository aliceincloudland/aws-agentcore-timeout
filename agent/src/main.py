import time
import logging
from datetime import datetime
from strands import Agent, tool
from bedrock_agentcore.runtime import BedrockAgentCoreApp

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = BedrockAgentCoreApp()
log = app.logger

@tool
def add_numbers(a: int, b: int) -> int:
    """Return the sum of two numbers"""
    return a+b

@app.entrypoint
def invoke(payload, context):
    session_id = getattr(context, 'session_id', 'default')
    request_id = getattr(context, 'request_id', 'unknown')
    
    log.info(f"🚀 SLEEP AGENT: Starting at {datetime.now()}")
    log.info(f"📝 Session ID: {session_id}, Request ID: {request_id}")
    log.info(f"📝 Payload: {payload}")
    
    duration_seconds = payload.get('duration_seconds', 280)
    
    log.info(f"⏳ Starting {duration_seconds}s wait...")
    time.sleep(duration_seconds)
    
    log.info(f"✅ SLEEP AGENT: Completed at {datetime.now()}")
    
    return {
        "status": "completed",
        "duration_seconds": duration_seconds,
        "session_id": session_id,
        "request_id": request_id,
        "completion_time": datetime.now().isoformat(),
        "message": f"{duration_seconds}s wait test completed successfully"
    }

if __name__ == "__main__":
    app.run()
