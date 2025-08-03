from typing import Optional, List
import asyncio

class Homepage:
    def __init__(self, username: str):
        self._username = username
        self._posts = []
        self._update_queue: Optional[asyncio.Queue] = None
        self._btnPressed = False
        self._sessionId = ''
        self._hiddenMsg = "🎉 Secret message from the server!"

    @property
    def username(self) -> str:
        return self._username

    @property
    def posts(self) -> List[str]:
        return self._posts

    @property
    def btnPressed(self) -> bool:
        return self._btnPressed

    @btnPressed.setter
    def btnPressed(self, value: bool) -> None:
        self._btnPressed = value

    @property
    def sessionId(self) -> str:
        return self._sessionId

    @sessionId.setter
    def sessionId(self, value: str) -> None:
        if self._sessionId == '':
            self._sessionId = value

    @property
    def post_count(self) -> int:
        """Get the number of posts"""
        return len(self._posts)

    @property
    def hiddenMsg(self) -> str:
        """Get the hidden message"""
        return self._hiddenMsg

    def add_post(self, content: str) -> None:
        """Add a post to the list"""
        self._posts.append(content)

    def delete_post(self, index: int) -> bool:
        """Delete a post by index, returns True if successful"""
        try:
            if 0 <= index < len(self._posts):
                self._posts.pop(index)
                return True
            return False
        except (IndexError, ValueError):
            return False

    async def queue_update(self, update_data: dict) -> None:
        """Queue SSE update - supports SSEXI message format"""
        if self._update_queue is not None:
            await self._update_queue.put(update_data)

    async def send_html_update(self, element_id: str, html_content: str) -> None:
        """Helper method to send HTML updates in SSEXI format"""
        await self.queue_update({"html": {element_id: html_content}})

    async def send_js_variable(self, var_name: str, value) -> None:
        """Helper method to send JS variable updates in SSEXI format"""
        await self.queue_update({"js": {var_name: value}})

    async def send_js_execution(self, js_code: str) -> None:
        """Helper method to send JS execution commands in SSEXI format"""
        await self.queue_update({"js": {"exec": js_code}})