from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import time
import random

app = FastAPI()

# Serve static files (for ssexi.js)
app.mount("/static", StaticFiles(directory="."), name="static")

# Store todos in memory
todos = []

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the demo HTML page"""
    with open("index.html", "r") as f:
        return HTMLResponse(f.read())

@app.get("/website-logic")
async def website_logic():
    """Single SSE endpoint that handles all website logic"""
    async def event_generator():
        try:
            count = 0
            while True:
                count += 1
                timestamp = int(time.time())
                
                # Update timestamp
                timestamp_update = {
                    "html": {
                        "timestamp": f'<div id="timestamp">Current Time: {timestamp}</div>'
                    }
                }
                yield f"data: {json.dumps(timestamp_update)}\n\n"
                
                # Update counter
                counter_update = {
                    "html": {
                        "counter": f'<div id="counter">Count: {count}</div>'
                    }
                }
                yield f"data: {json.dumps(counter_update)}\n\n"
                
                # Update todos list
                todos_html = ''.join(f'<li>{todo}</li>' for todo in todos)
                todos_update = {
                    "html": {
                        "todos": f'<ul id="todos">{todos_html}</ul>'
                    }
                }
                yield f"data: {json.dumps(todos_update)}\n\n"
                
                # Every 5 counts, set a JS variable and execute some code
                if count % 5 == 0:
                    js_var_update = {
                        "js": {
                            "counterValue": count
                        }
                    }
                    yield f"data: {json.dumps(js_var_update)}\n\n"
                    
                    js_exec_update = {
                        "js": {
                            "exec": f"console.log('Counter reached {count}!');"
                        }
                    }
                    yield f"data: {json.dumps(js_exec_update)}\n\n"
                
                # Every 10 counts, change background color
                if count % 10 == 0:
                    colors = ["lightblue", "lightgreen", "lightcoral", "lightyellow"]
                    color = random.choice(colors)
                    
                    color_update = {
                        "js": {
                            "exec": f"document.body.style.backgroundColor = '{color}';"
                        }
                    }
                    yield f"data: {json.dumps(color_update)}\n\n"
                
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            pass
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Transfer-Encoding": "chunked"
        }
    )

@app.post("/todo")
async def add_todo(todo_text: str = Form(...)):
    """Add a new todo item and send form reset via SSE"""
    print(f"Received todo: {todo_text}")  # Print to console as requested
    todos.append(todo_text)
    
    # Since we can't send SSE directly from POST, we'll use a different approach
    # The SSE stream will pick up the updated todos automatically
    
    return {"status": "success", "message": f"Added todo: {todo_text}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)