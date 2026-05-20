import logging
import os
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import AsyncOpenAI, OpenAIError
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Backend API",
    description="Production-ready AI API powered by OpenAI",
    version="1.0.0"
)

# Configure CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY environment variable not set")
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = AsyncOpenAI(api_key=api_key)

# Conversation memory storage (in production, use Redis or database)
conversation_memory: dict[str, list] = {}

# ==================== Pydantic Models ====================

class Message(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000, description="User's prompt")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for memory")
    model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")
    temperature: float = Field(default=0.7, ge=0, le=2, description="Temperature for response creativity")
    max_tokens: Optional[int] = Field(default=2000, ge=1, le=4000, description="Max tokens in response")
    stream: bool = Field(default=False, description="Enable streaming responses")

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    model: str
    tokens_used: Optional[dict] = None
    timestamp: str

class StreamMessage(BaseModel):
    type: str
    content: str
    timestamp: str

class HealthCheck(BaseModel):
    status: str
    timestamp: str
    api_version: str

# ==================== Health Check ====================

@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    logger.info("Health check requested")
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        api_version="1.0.0"
    )

# ==================== Chat Endpoints ====================

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Send a message and get an AI response with conversation memory support
    
    - **prompt**: The user's message
    - **conversation_id**: Optional ID to maintain conversation history
    - **model**: OpenAI model (default: gpt-4o-mini)
    - **temperature**: Response creativity (0-2)
    - **max_tokens**: Maximum response length
    - **stream**: Enable streaming (use /stream endpoint instead)
    """
    
    conversation_id = request.conversation_id or f"conv_{datetime.now().timestamp()}"
    
    try:
        logger.info(f"Chat request received - Conversation: {conversation_id}")
        
        # Initialize conversation memory if needed
        if conversation_id not in conversation_memory:
            conversation_memory[conversation_id] = []
        
        # Build messages list with conversation history
        messages = conversation_memory[conversation_id].copy()
        messages.append({"role": "user", "content": request.prompt})
        
        # Call OpenAI API
        response = await client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        # Extract response
        assistant_message = response.choices[0].message.content
        
        # Store in conversation memory
        conversation_memory[conversation_id].append({"role": "user", "content": request.prompt})
        conversation_memory[conversation_id].append({"role": "assistant", "content": assistant_message})
        
        # Keep conversation history manageable (last 20 messages)
        if len(conversation_memory[conversation_id]) > 20:
            conversation_memory[conversation_id] = conversation_memory[conversation_id][-20:]
        
        logger.info(f"Chat response generated successfully - Conversation: {conversation_id}")
        
        return ChatResponse(
            conversation_id=conversation_id,
            response=assistant_message,
            model=request.model,
            tokens_used={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            timestamp=datetime.now().isoformat()
        )
        
    except OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(status_code=503, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/stream", tags=["Chat"])
async def stream_chat(request: ChatRequest):
    """
    Stream AI responses in real-time using Server-Sent Events (SSE)
    
    Ideal for low-latency frontend updates
    """
    
    conversation_id = request.conversation_id or f"conv_{datetime.now().timestamp()}"
    
    async def event_generator():
        try:
            logger.info(f"Stream request received - Conversation: {conversation_id}")
            
            # Initialize conversation memory if needed
            if conversation_id not in conversation_memory:
                conversation_memory[conversation_id] = []
            
            # Build messages list
            messages = conversation_memory[conversation_id].copy()
            messages.append({"role": "user", "content": request.prompt})
            
            # Store user message
            conversation_memory[conversation_id].append({"role": "user", "content": request.prompt})
            
            full_response = ""
            
            # Stream from OpenAI
            async with await client.chat.completions.create(
                model=request.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
            ) as stream:
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        
                        # Send as SSE
                        event = StreamMessage(
                            type="content",
                            content=content,
                            timestamp=datetime.now().isoformat()
                        )
                        yield f"data: {json.dumps(event.model_dump())}\n\n"
            
            # Store assistant message
            conversation_memory[conversation_id].append({"role": "assistant", "content": full_response})
            
            # Keep history manageable
            if len(conversation_memory[conversation_id]) > 20:
                conversation_memory[conversation_id] = conversation_memory[conversation_id][-20:]
            
            # Send completion event
            done_event = StreamMessage(
                type="done",
                content=conversation_id,
                timestamp=datetime.now().isoformat()
            )
            yield f"data: {json.dumps(done_event.model_dump())}\n\n"
            
            logger.info(f"Stream completed successfully - Conversation: {conversation_id}")
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error during streaming: {str(e)}")
            error_event = StreamMessage(
                type="error",
                content=f"OpenAI API error: {str(e)}",
                timestamp=datetime.now().isoformat()
            )
            yield f"data: {json.dumps(error_event.model_dump())}\n\n"
        except Exception as e:
            logger.error(f"Unexpected error during streaming: {str(e)}")
            error_event = StreamMessage(
                type="error",
                content="Internal server error",
                timestamp=datetime.now().isoformat()
            )
            yield f"data: {json.dumps(error_event.model_dump())}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/conversation/{conversation_id}", tags=["Chat"])
async def get_conversation(conversation_id: str):
    """Retrieve conversation history"""
    if conversation_id not in conversation_memory:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    logger.info(f"Conversation history retrieved - ID: {conversation_id}")
    return {
        "conversation_id": conversation_id,
        "messages": conversation_memory[conversation_id],
        "message_count": len(conversation_memory[conversation_id])
    }

@app.delete("/conversation/{conversation_id}", tags=["Chat"])
async def clear_conversation(conversation_id: str):
    """Clear conversation history"""
    if conversation_id in conversation_memory:
        del conversation_memory[conversation_id]
        logger.info(f"Conversation cleared - ID: {conversation_id}")
        return {"status": "cleared", "conversation_id": conversation_id}
    
    raise HTTPException(status_code=404, detail="Conversation not found")

# ==================== Root Endpoint ====================

@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint with API information"""
    return {
        "status": "online",
        "name": "AI Backend API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/chat (POST)",
            "stream": "/stream (POST)",
            "conversation": "/conversation/{id} (GET/DELETE)",
            "docs": "/docs"
        }
    }

# ==================== Error Handlers ====================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.error(f"Value error: {str(exc)}")
    return HTTPException(status_code=400, detail=str(exc))

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
