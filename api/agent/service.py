import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from fastapi import BackgroundTasks

from src.models.agent import AgentRunStatus
from src.utils.database import MongoDB

logger = logging.getLogger(__name__)

class AgentService:
    async def start_agent_run(
        self,
        user_id: str,
        prompt: str,
        model: str,
        background_tasks: BackgroundTasks
    ) -> str:
        if not prompt or prompt.strip() == "":
            raise ValueError("Prompt cannot be empty")
        run_id = str(uuid.uuid4())
        now = datetime.utcnow()
        run_doc = {
            "_id": run_id,
            "user_id": user_id,
            "prompt": prompt,
            "status": AgentRunStatus.PENDING,
            "steps": [],
            "model": model,
            "started_at": now.isoformat(),
        }
        await MongoDB.db.agent_runs.insert_one(run_doc)
        background_tasks.add_task(self._run_agent, run_id, user_id, prompt, model)
        return run_id

    async def _run_agent(self, run_id: str, user_id: str, prompt: str, model: str):
        # Placeholder for actual agent execution logic
        # Update status to RUNNING
        await MongoDB.db.agent_runs.update_one({"_id": run_id}, {"$set": {"status": AgentRunStatus.RUNNING}})
        try:
            # Simulate agent processing (replace with real agent logic)
            import time
            time.sleep(2)
            result = f"Agent response for prompt: {prompt} (model: {model})"
            now = datetime.utcnow()
            await MongoDB.db.agent_runs.update_one(
                {"_id": run_id},
                {"$set": {
                    "status": AgentRunStatus.COMPLETED,
                    "result": result,
                    "completed_at": now.isoformat(),
                    "duration_seconds": (now - datetime.fromisoformat(await self._get_started_at(run_id))).total_seconds()
                }}
            )
        except Exception as e:
            now = datetime.utcnow()
            await MongoDB.db.agent_runs.update_one(
                {"_id": run_id},
                {"$set": {
                    "status": AgentRunStatus.FAILED,
                    "error": str(e),
                    "completed_at": now.isoformat(),
                    "duration_seconds": (now - datetime.fromisoformat(await self._get_started_at(run_id))).total_seconds()
                }}
            )

    async def _get_started_at(self, run_id: str) -> str:
        run = await MongoDB.db.agent_runs.find_one({"_id": run_id})
        return run["started_at"] if run else datetime.utcnow().isoformat()

    async def get_agent_run(self, run_id: str, user_id: str) -> Optional[Dict]:
        run = await MongoDB.db.agent_runs.find_one({"_id": run_id, "user_id": user_id})
        if run:
            run["id"] = run["_id"]
        return run

    async def get_agent_runs(
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
        cursor = MongoDB.db.agent_runs.find(query)
        total = await MongoDB.db.agent_runs.count_documents(query)
        cursor = cursor.sort("started_at", -1).skip(skip).limit(limit)
        runs = await cursor.to_list(length=limit)
        for run in runs:
            run["id"] = run["_id"]
        return runs, total

    async def cancel_agent_run(self, run_id: str, user_id: str) -> bool:
        run = await MongoDB.db.agent_runs.find_one({
            "_id": run_id,
            "user_id": user_id,
            "status": {"$in": [AgentRunStatus.PENDING, AgentRunStatus.RUNNING]}
        })
        if not run:
            return False
        now = datetime.utcnow()
        result = await MongoDB.db.agent_runs.update_one(
            {"_id": run_id},
            {"$set": {
                "status": AgentRunStatus.CANCELLED,
                "completed_at": now.isoformat(),
                "duration_seconds": (now - datetime.fromisoformat(run["started_at"])).total_seconds()
            }}
        )
        return result.modified_count > 0

agent_service = AgentService() 