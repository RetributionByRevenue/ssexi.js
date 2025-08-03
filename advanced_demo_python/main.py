from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import base64
import secrets
import random
import string
import json
import asyncio
from typing import Dict
from models import Homepage
import uuid

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Serve static files (for ssexi.js)
app.mount("/static", StaticFiles(directory="."), name="static")

# Simulated user database
USERS = {
    "mark": "pass123",
    "luke": "pass456"
}

# Store active user sessions
user_sessions: Dict[str, Homepage] = {}

async def create_homepage(username: str) -> Homepage:
    """Create a new Homepage instance with initialized queue."""
    homepage = Homepage(username)
    # Initialize the queue in an async context
    homepage._update_queue = asyncio.Queue()
    return homepage

async def verify_credentials(username: str, password: str):
    """Verify user credentials and create/return Homepage instance."""
    if username in USERS and secrets.compare_digest(password, USERS[username]):
        if username not in user_sessions:
            user_sessions[username] = await create_homepage(username)
        return user_sessions[username]
    return None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        return RedirectResponse(url="/login")

    try:
        username = base64.b64decode(auth_token).decode().split(":")[0]
        user = user_sessions.get(username)
        if not user:
            return RedirectResponse(url="/login")
        user.sessionId = str(uuid.uuid4())
    except Exception:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = await verify_credentials(username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid credentials"}
        )

    auth_token = base64.b64encode(f"{username}:authenticated".encode()).decode()
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="auth_token",
        value=auth_token,
        httponly=True,
        max_age=1800,
        samesite="lax"
    )
    return response

@app.get("/logout")
async def logout(request: Request):
    auth_token = request.cookies.get("auth_token")
    if auth_token:
        try:
            username = base64.b64decode(auth_token).decode().split(":")[0]
            # Clean up the user session on logout
            user_sessions.pop(username, None)
        except Exception:
            pass
    
    response = RedirectResponse(url="/login")
    response.delete_cookie("auth_token")
    return response

@app.post("/add_post")
async def add_post(request: Request, post_content: str = Form(...)):
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    try:
        username = base64.b64decode(auth_token).decode().split(":")[0]
        user = user_sessions.get(username)
        if not user:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
    except Exception:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    # Add the new post
    user.add_post(post_content)
    
    # Update posts list with delete buttons
    posts_html = (
        f'<ol id="ol_{user.username}" style="background: #f8f9fa; padding: 1.5rem; border-radius: 4px; min-height: 200px;">'
    )
    
    if user.posts:
        for i, post in enumerate(user.posts):
            posts_html += f'''
                <li style="padding: 0.5rem 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center;">
                    <span>{i+1}. {post}</span>
                    <form sx-post="/delete_post" sx-swap="none" style="margin: 0;">
                        <input type="hidden" name="post_index" value="{i}">
                        <button type="submit" id="delete_btn_{i}"
                                style="background: #dc3545; color: white; border: none; padding: 0.25rem 0.5rem; border-radius: 3px; cursor: pointer; font-size: 0.8rem;">
                            🗑️ Delete
                        </button>
                    </form>
                </li>
            '''
    else:
        posts_html += '<li style="color: #666; font-style: italic;">No posts yet. Add some above! 👆</li>'
    
    posts_html += '</ol>'
    await user.send_html_update(f"ol_{user.username}", posts_html)
    
    # Send form reset command using SSEXI format
    await user.send_js_execution('document.getElementById("addPostForm").reset();')

    # update the h2
    await user.send_html_update(
        f"post_title_length_{ user.username }", 
        f'<h2 id="post_title_length_{user.username}"> 📋 Your Posts ({user.post_count} total)</h2>'
    )
    
    # Update chart in real-time via SSEXI JS variable
    chart_data = { 'x': user.post_count , 'y': user.post_count }
    await user.send_js_execution(f'myChart.data.datasets[0].data = [{chart_data}]; myChart.update();')

    return {"status": "success"}

@app.post("/generate_posts")
async def generate_posts(request: Request):
    """SSEXI-powered endpoint for generating random posts"""
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    try:
        username = base64.b64decode(auth_token).decode().split(":")[0]
        user = user_sessions.get(username)
        if not user:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
    except Exception:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    # Disable the button using SSEXI
    await user.send_html_update(
        f"btn_{user.username}", 
        f'''<button id="btn_{ user.username }" type="submit"
          style="width: 100%; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem;"
          disabled>
          🎯 Generate 5 Posts
          </button>
        '''
    )

    for i in range(5):
        # Generate random post
        random_post = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        user.add_post(random_post)
        
        # Update posts list with delete buttons
        posts_html = (
            f'<ol id="ol_{user.username}" style="background: #f8f9fa; padding: 1.5rem; border-radius: 4px; min-height: 200px;">'
        )
        
        if user.posts:
            for j, post in enumerate(user.posts):
                posts_html += f'''
                    <li style="padding: 0.5rem 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center;">
                        <span>{j+1}. {post}</span>
                        <form sx-post="/delete_post" sx-swap="none" style="margin: 0;">
                            <input type="hidden" name="post_index" value="{j}">
                            <button type="submit" id="delete_btn_{j}"
                                    style="background: #dc3545; color: white; border: none; padding: 0.25rem 0.5rem; border-radius: 3px; cursor: pointer; font-size: 0.8rem;">
                                🗑️ Delete
                            </button>
                        </form>
                    </li>
                '''
        else:
            posts_html += '<li style="color: #666; font-style: italic;">No posts yet. Add some above! 👆</li>'
        
        posts_html += '</ol>'
        await user.send_html_update(f"ol_{user.username}", posts_html)
        
        # Update counter in real-time during generation
        await user.send_html_update(
            f"post_title_length_{ user.username }", 
            f'<h2 id="post_title_length_{user.username}"> 📋 Your Posts ({user.post_count} total)</h2>'
        )

        # Update chart in real-time via SSEXI JS variable
        chart_data = { 'x': user.post_count , 'y': user.post_count }
        await user.send_js_execution(f'myChart.data.datasets[0].data = [{chart_data}]; myChart.update();')
        
        
        await asyncio.sleep(0.5)

    # Re-enable the button using SSEXI
    await user.send_html_update(
        f"btn_{user.username}", 
        f'''<button id="btn_{ user.username }" type="submit"
            style="width: 100%; background: #6c757d; color: white; border: 2px solid black; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem;">
            🎯 Generate 5 Posts
            </button>
        '''
    )
    
    # Send success notificationlee[p]
    await user.send_js_execution("console.log('✅ Generated 5 random posts!');")

    return {"status": "success"}

@app.post("/get_server_message")
async def get_server_message(request: Request):
    """Display server's hidden message via JavaScript alert"""
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    try:
        username = base64.b64decode(auth_token).decode().split(":")[0]
        user = user_sessions.get(username)
        if not user:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
    except Exception:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    # Send JavaScript alert with hidden message
    await user.send_js_execution(f'alert("{user.hiddenMsg}");')
    
    return {"status": "success"}

@app.post("/delete_post")
async def delete_post(request: Request, post_index: int = Form(...)):
    """Delete a post by index"""
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    try:
        username = base64.b64decode(auth_token).decode().split(":")[0]
        user = user_sessions.get(username)
        if not user:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
    except Exception:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    # Delete the post
    success = user.delete_post(post_index)
    
    if success:
        # Send updated posts list with consistent delete buttons
        posts_html = (
            f'<ol id="ol_{user.username}" style="background: #f8f9fa; padding: 1.5rem; border-radius: 4px; min-height: 200px;">'
        )
        
        if user.posts:
            for i, post in enumerate(user.posts):
                posts_html += f'''
                    <li style="padding: 0.5rem 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center;">
                        <span>{i+1}. {post}</span>
                        <form sx-post="/delete_post" sx-swap="none" style="margin: 0;">
                            <input type="hidden" name="post_index" value="{i}">
                            <button type="submit" id="delete_btn_{i}"
                                    style="background: #dc3545; color: white; border: none; padding: 0.25rem 0.5rem; border-radius: 3px; cursor: pointer; font-size: 0.8rem;">
                                🗑️ Delete
                            </button>
                        </form>
                    </li>
                '''
        else:
            posts_html += '<li style="color: #666; font-style: italic;">No posts yet. Add some above! 👆</li>'
        
        posts_html += '</ol>'
        await user.send_html_update(f"ol_{user.username}", posts_html)
        
        # Update counter
        await user.send_html_update(
            f"post_title_length_{user.username}", 
            f'<h2 id="post_title_length_{user.username}"> 📋 Your Posts ({user.post_count} total)</h2>'
        )

        # Update chart in real-time via SSEXI JS variable
        chart_data = { 'x': user.post_count , 'y': user.post_count }
        await user.send_js_execution(f'myChart.data.datasets[0].data = [{chart_data}]; myChart.update();')

        # Success notification
        await user.send_js_execution("console.log('✅ Post deleted successfully!');")
    else:
        # Error notification
        await user.send_js_execution("console.log('❌ Failed to delete post - invalid index');")
    
    return {"status": "success" if success else "error"}

@app.get("/stream/{username}")
async def message_stream(username: str):
    user = user_sessions.get(username)
    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)

    async def event_generator():
        try:
            while True:
                update = await user._update_queue.get()
                yield f"data: {json.dumps(update)}\n\n"
        except asyncio.CancelledError:
            # Handle disconnection
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

@app.on_event("startup")
async def startup_event():
    """Initialize any async resources on startup."""
    pass

@app.on_event("shutdown")  
async def shutdown_event():
    """Clean up any async resources on shutdown."""
    user_sessions.clear()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)