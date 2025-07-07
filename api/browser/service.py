import base64
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from fastapi import BackgroundTasks

from src.models.agent import AgentRunStatus
from src.utils.database import MongoDB

logger = logging.getLogger(__name__)

class BrowserService:
    async def start_browser_task(
        self,
        user_id: str,
        instructions: str,
        url: Optional[str] = None,
        developer_mode: bool = False,
        headless: bool = False,
        background_tasks: BackgroundTasks = BackgroundTasks()
    ) -> str:
        if not instructions or instructions.strip() == "":
            raise ValueError("Instructions cannot be empty")
        task_id = str(uuid.uuid4())
        now = datetime.utcnow()
        screenshots_dir = os.path.join(os.getcwd(), "data", "screenshots", user_id)
        os.makedirs(screenshots_dir, exist_ok=True)
        task_doc = {
            "_id": task_id,
            "user_id": user_id,
            "instructions": instructions,
            "url": url,
            "status": AgentRunStatus.PENDING,
            "screenshots": [],
            "started_at": now.isoformat(),
            "developer_mode": developer_mode
        }
        await MongoDB.db.browser_tasks.insert_one(task_doc)
        background_tasks.add_task(self._run_browser_task, task_id, user_id, instructions, url, developer_mode, headless, screenshots_dir)
        return task_id

    async def _run_browser_task(self, task_id, user_id, instructions, url, developer_mode, headless, screenshots_dir):
        # Placeholder for actual browser automation logic
        await MongoDB.db.browser_tasks.update_one({"_id": task_id}, {"$set": {"status": AgentRunStatus.RUNNING}})
        try:
            import time
            time.sleep(2)
            # Simulate screenshot creation
            screenshot_path = os.path.join(screenshots_dir, f"{task_id}_screenshot.png")
            with open(screenshot_path, "wb") as f:
                f.write(b"fake image data")
            now = datetime.utcnow()
            await MongoDB.db.browser_tasks.update_one(
                {"_id": task_id},
                {"$set": {
                    "status": AgentRunStatus.COMPLETED,
                    "screenshots": [screenshot_path],
                    "result": f"Browser automation completed for: {instructions}",
                    "completed_at": now.isoformat(),
                    "duration_seconds": (now - datetime.fromisoformat(await self._get_started_at(task_id))).total_seconds()
                }}
            )
        except Exception as e:
            now = datetime.utcnow()
            await MongoDB.db.browser_tasks.update_one(
                {"_id": task_id},
                {"$set": {
                    "status": AgentRunStatus.FAILED,
                    "error": str(e),
                    "completed_at": now.isoformat(),
                    "duration_seconds": (now - datetime.fromisoformat(await self._get_started_at(task_id))).total_seconds()
                }}
            )

    async def _get_started_at(self, task_id: str) -> str:
        task = await MongoDB.db.browser_tasks.find_one({"_id": task_id})
        return task["started_at"] if task else datetime.utcnow().isoformat()

    async def get_browser_task(self, task_id: str, user_id: str) -> Optional[Dict]:
        task = await MongoDB.db.browser_tasks.find_one({"_id": task_id, "user_id": user_id})
        if task and "screenshots" in task and task["screenshots"]:
            for i, screenshot_path in enumerate(task["screenshots"]):
                if os.path.exists(screenshot_path):
                    with open(screenshot_path, "rb") as img_file:
                        img_data = img_file.read()
                        base64_data = base64.b64encode(img_data).decode("utf-8")
                        task["screenshots"][i] = f"data:image/png;base64,{base64_data}"
        return task

    async def get_browser_tasks(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 10,
        status: Optional[AgentRunStatus] = None
    ) -> Tuple[List[Dict], int]:
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        skip = (page - 1) * limit
        cursor = MongoDB.db.browser_tasks.find(query)
        total = await MongoDB.db.browser_tasks.count_documents(query)
        cursor = cursor.sort("started_at", -1).skip(skip).limit(limit)
        tasks = await cursor.to_list(length=limit)
        for task in tasks:
            if "screenshots" in task:
                task["screenshots"] = [f"Screenshot {i+1}" for i in range(len(task["screenshots"]))]
        return tasks, total

    async def cancel_browser_task(self, task_id: str, user_id: str) -> bool:
        task = await MongoDB.db.browser_tasks.find_one({
            "_id": task_id,
            "user_id": user_id,
            "status": {"$in": [AgentRunStatus.PENDING, AgentRunStatus.RUNNING]}
        })
        if not task:
            return False
        now = datetime.utcnow()
        result = await MongoDB.db.browser_tasks.update_one(
            {"_id": task_id},
            {"$set": {
                "status": AgentRunStatus.CANCELLED,
                "completed_at": now.isoformat(),
                "duration_seconds": (now - datetime.fromisoformat(task["started_at"])).total_seconds()
            }}
        )
        return result.modified_count > 0

browser_service = BrowserService() 