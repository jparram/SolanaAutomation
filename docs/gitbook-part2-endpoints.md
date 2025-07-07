# API Endpoints Implementation

Now that we have set up the core server structure, let's implement the API endpoints for our SolanaAI Agent platform.

## API Router Configuration

Let's start by creating the main API router structure:

```bash
cd ../api
touch __init__.py
```

Create a file structure for our API modules:

```bash
mkdir -p auth agent browser blockchain payment
touch router.py
```

Let's first create the main router:

```python
# api/router.py
from fastapi import APIRouter

from .auth import router as auth_router
from .agent import router as agent_router
from .browser import router as browser_router
from .blockchain import router as blockchain_router
from .payment import router as payment_router

# Create main API router
api_router = APIRouter(prefix="/api")

# Include sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(agent_router, prefix="/agent", tags=["AI Agent"])
api_router.include_router(browser_router, prefix="/browser", tags=["Browser Automation"])
api_router.include_router(blockchain_router, prefix="/blockchain", tags=["Blockchain Operations"])
api_router.include_router(payment_router, prefix="/payment", tags=["Payments"])
```

Now, let's implement each of the routers one by one.

## Authentication Endpoints

Create the authentication endpoints:

```bash
cd auth
touch __init__.py
touch router.py
touch service.py
```

Implement the authentication router:

```python
# api/auth/__init__.py
from .router import router
```

```python
# api/auth/router.py
import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ...models.session import Session
from ...models.user import User, UserCreate, UserLogin
from ...utils.auth import get_current_user
from .service import auth_service

# Create router
router = APIRouter()

# Logger
logger = logging.getLogger(__name__)

@router.post("/register", response_model=Dict[str, Any])
async def register(user_data: UserCreate = Body(...)):
    """
    Register a new user.
    """
    try:
        user = await auth_service.register_user(user_data)
        return {
            "success": True,
            "message": "User registered successfully",
            "data": {"user_id": user["_id"]}
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registering user"
        )

@router.post("/login", response_model=Dict[str, Any])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate a user and return a token.
    """
    try:
        user_login = UserLogin(email=form_data.username, password=form_data.password)
        token, user = await auth_service.login_user(user_login)
        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user["_id"],
                    "email": user["email"],
                    "username": user["username"]
                }
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error logging in: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error logging in"
        )

@router.post("/logout", response_model=Dict[str, Any])
async def logout(current_user: User = Depends(get_current_user)):
    """
    Log out a user by invalidating their token.
    """
    try:
        await auth_service.logout_user(current_user.id)
        return {
            "success": True,
            "message": "Logout successful"
        }
    except Exception as e:
        logger.error(f"Error logging out: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error logging out"
        )

@router.get("/me", response_model=Dict[str, Any])
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the current user's information.
    """
    try:
        user_data = {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "wallets": current_user.wallets,
            "profile": current_user.profile,
            "preferences": current_user.preferences,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified
        }
        return {
            "success": True,
            "message": "User retrieved successfully",
            "data": user_data
        }
    except Exception as e:
        logger.error(f"Error retrieving user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user"
        )
```

Implement the authentication service:

```python
# api/auth/service.py
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Tuple, Union

from ...config import settings
from ...models.user import UserCreate, UserLogin
from ...utils.auth import create_jwt_token
from ...utils.database import MongoDB
from ...utils.password import hash_password, verify_password

# Logger
logger = logging.getLogger(__name__)

class AuthService:
    async def register_user(self, user_data: UserCreate) -> Dict:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Dict: The created user
            
        Raises:
            ValueError: If a user with the email already exists
        """
        # Check if email already exists
        existing_user = await MongoDB.db.users.find_one({"email": user_data.email})
        if existing_user:
            raise ValueError("Email already registered")
            
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user document
        now = datetime.utcnow()
        user_id = str(uuid.uuid4())
        user_doc = {
            "_id": user_id,
            "email": user_data.email,
            "username": user_data.username,
            "password": hashed_password,
            "wallets": [],
            "profile": None,
            "preferences": {
                "default_model": settings.DEFAULT_MODEL,
                "default_network": "devnet",
                "auto_approve_threshold": 0.1,
                "browser_headless": False,
                "receive_email_notifications": True,
                "receive_push_notifications": True
            },
            "is_active": True,
            "is_verified": False,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        
        # Insert user into database
        await MongoDB.db.users.insert_one(user_doc)
        
        # Return user (without password)
        user_doc.pop("password")
        return user_doc
        
    async def login_user(self, user_login: UserLogin) -> Tuple[str, Dict]:
        """
        Authenticate a user and create a session.
        
        Args:
            user_login: User login data
            
        Returns:
            Tuple[str, Dict]: The JWT token and user data
            
        Raises:
            ValueError: If the email or password is incorrect
        """
        # Find user by email
        user = await MongoDB.db.users.find_one({"email": user_login.email})
        if not user:
            raise ValueError("Invalid email or password")
            
        # Verify password
        if not verify_password(user_login.password, user["password"]):
            raise ValueError("Invalid email or password")
            
        # Check if user is active
        if not user.get("is_active", True):
            raise ValueError("User account is inactive")
            
        # Create JWT token
        token = create_jwt_token(user["_id"])
        
        # Create session
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=settings.JWT_EXPIRATION)
        session_id = str(uuid.uuid4())
        session_doc = {
            "_id": session_id,
            "user_id": user["_id"],
            "token": token,
            "expires_at": expires_at.isoformat(),
            "created_at": now.isoformat(),
            "last_activity": now.isoformat()
        }
        
        # Insert session into database
        await MongoDB.db.sessions.insert_one(session_doc)
        
        # Return token and user (without password)
        user.pop("password")
        return token, user
        
    async def logout_user(self, user_id: str) -> None:
        """
        Log out a user by invalidating all their sessions.
        
        Args:
            user_id: The ID of the user to log out
            
        Returns:
            None
        """
        # Delete all user sessions
        await MongoDB.db.sessions.delete_many({"user_id": user_id})

# Create service instance
auth_service = AuthService()
```

## Agent Endpoints

Now, let's implement the agent endpoints:

```bash
cd ../agent
touch __init__.py
touch router.py
touch service.py
```

Implement the agent router:

```python
# api/agent/__init__.py
from .router import router
```

```python
# api/agent/router.py
import logging
from typing import Any, Dict, List, Optional

from fastapi import (APIRouter, BackgroundTasks, Body, Depends, HTTPException,
                     Query, status)

from ...models.agent import AgentRun, AgentRunStatus
from ...models.user import User
from ...utils.auth import get_current_active_user
from .service import agent_service

# Create router
router = APIRouter()

# Logger
logger = logging.getLogger(__name__)

@router.post("/run", response_model=Dict[str, Any])
async def run_agent(
    prompt: str = Body(...),
    model: Optional[str] = Body(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_active_user)
):
    """
    Run the AI agent with a prompt.
    """
    try:
        # Start agent run in the background
        run_id = await agent_service.start_agent_run(
            user_id=current_user.id,
            prompt=prompt,
            model=model or current_user.preferences.default_model,
            background_tasks=background_tasks
        )
        
        return {
            "success": True,
            "message": "Agent run started",
            "data": {"run_id": run_id}
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting agent run: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error starting agent run"
        )

@router.get("/run/{run_id}", response_model=Dict[str, Any])
async def get_agent_run(
    run_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get an agent run by ID.
    """
    try:
        run = await agent_service.get_agent_run(run_id, current_user.id)
        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent run not found"
            )
            
        return {
            "success": True,
            "message": "Agent run retrieved",
            "data": run
        }
    except Exception as e:
        logger.error(f"Error retrieving agent run: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving agent run"
        )

@router.get("/runs", response_model=Dict[str, Any])
async def get_agent_runs(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[AgentRunStatus] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a list of agent runs for the current user.
    """
    try:
        runs, total = await agent_service.get_agent_runs(
            user_id=current_user.id,
            page=page,
            limit=limit,
            status=status
        )
        
        return {
            "success": True,
            "message": "Agent runs retrieved",
            "data": {
                "runs": runs,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving agent runs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving agent runs"
        )

@router.delete("/run/{run_id}", response_model=Dict[str, Any])
async def cancel_agent_run(
    run_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancel an agent run.
    """
    try:
        success = await agent_service.cancel_agent_run(run_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent run not found or already completed"
            )
            
        return {
            "success": True,
            "message": "Agent run cancelled"
        }
    except Exception as e:
        logger.error(f"Error cancelling agent run: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error cancelling agent run"
        )
```

Implement the agent service:

```python
# api/agent/service.py
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from fastapi import BackgroundTasks

from ...agent.solana_ai_agent import SolanaAIAgent
from ...models.agent import AgentRun, AgentRunStatus
from ...utils.database import MongoDB

# Logger
logger = logging.getLogger(__name__)

class AgentService:
    async def start_agent_run(
        self,
        user_id: str,
        prompt: str,
        model: str,
        background_tasks: BackgroundTasks
    ) -> str:
        """
        Start an agent run.
        
        Args:
            user_id: The ID of the user
            prompt: The prompt to run
            model: The model to use
            background_tasks: FastAPI background tasks
            
        Returns:
            str: The ID of the created run
            
        Raises:
            ValueError: If the prompt is empty
        """
        if not prompt or prompt.strip() == "":
            raise ValueError("Prompt cannot be empty")
            
        # Create run ID
        run_id = str(uuid.uuid4())
        
        # Create run document
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
        
        # Insert run into database
        await MongoDB.db.agent_runs.insert_one(run_doc)
        
        # Add task to background tasks
        background_tasks.add_task(self._run_agent, run_id, user_id, prompt, model)
        
        return run_id
        
    async def _run_agent(self, run_id: str, user_id: str, prompt: str, model: str) -> None:
        """
        Run the agent in the background.
        
        Args:
            run_id: The ID of the run
            user_id: The ID of the user
            prompt: The prompt to run
            model: The model to use
            
        Returns:
            None
        """
        try:
            # Update run status to running
            now = datetime.utcnow()
            await MongoDB.db.agent_runs.update_one(
                {"_id": run_id},
                {"$set": {
                    "status": AgentRunStatus.RUNNING,
                    "started_at": now.isoformat()
                }}
            )
            
            # Create agent instance
            agent = SolanaAIAgent(model_name=model)
            
            # Run agent
            result = agent.run(prompt)
            
            # Update run with result
            end_time = datetime.utcnow()
            duration = (end_time - now).total_seconds()
            
            await MongoDB.db.agent_runs.update_one(
                {"_id": run_id},
                {"$set": {
                    "status": AgentRunStatus.COMPLETED,
                    "result": result,
                    "completed_at": end_time.isoformat(),
                    "duration_seconds": duration
                }}
            )
            
        except Exception as e:
            logger.error(f"Error running agent: {e}")
            
            # Update run with error
            end_time = datetime.utcnow()
            duration = (end_time - now).total_seconds()
            
            await MongoDB.db.agent_runs.update_one(
                {"_id": run_id},
                {"$set": {
                    "status": AgentRunStatus.FAILED,
                    "error": str(e),
                    "completed_at": end_time.isoformat(),
                    "duration_seconds": duration
                }}
            )
            
    async def get_agent_run(self, run_id: str, user_id: str) -> Optional[Dict]:
        """
        Get an agent run by ID.
        
        Args:
            run_id: The ID of the run
            user_id: The ID of the user
            
        Returns:
            Optional[Dict]: The agent run if found, None otherwise
        """
        run = await MongoDB.db.agent_runs.find_one({"_id": run_id, "user_id": user_id})
        return run
        
    async def get_agent_runs(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 10,
        status: Optional[AgentRunStatus] = None
    ) -> Tuple[List[Dict], int]:
        """
        Get a list of agent runs for a user.
        
        Args:
            user_id: The ID of the user
            page: The page number
            limit: The number of runs per page
            status: Filter runs by status
            
        Returns:
            Tuple[List[Dict], int]: The list of runs and the total count
        """
        # Build query
        query = {"user_id": user_id}
        if status:
            query["status"] = status
            
        # Calculate skip
        skip = (page - 1) * limit
        
        # Get runs
        cursor = MongoDB.db.agent_runs.find(query)
        
        # Get total count
        total = await MongoDB.db.agent_runs.count_documents(query)
        
        # Apply pagination
        cursor = cursor.sort("started_at", -1).skip(skip).limit(limit)
        
        # Convert cursor to list
        runs = await cursor.to_list(length=limit)
        
        return runs, total
        
    async def cancel_agent_run(self, run_id: str, user_id: str) -> bool:
        """
        Cancel an agent run.
        
        Args:
            run_id: The ID of the run
            user_id: The ID of the user
            
        Returns:
            bool: True if the run was cancelled, False otherwise
        """
        # Check if run exists and is pending or running
        run = await MongoDB.db.agent_runs.find_one({
            "_id": run_id,
            "user_id": user_id,
            "status": {"$in": [AgentRunStatus.PENDING, AgentRunStatus.RUNNING]}
        })
        
        if not run:
            return False
            
        # Update run status to cancelled
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

# Create service instance
agent_service = AgentService()
```

## Browser Automation Endpoints

Implement the browser automation endpoints:

```bash
cd ../browser
touch __init__.py
touch router.py
touch service.py
```

Implement the browser router:

```python
# api/browser/__init__.py
from .router import router
```

```python
# api/browser/router.py
import logging
from typing import Any, Dict, List, Optional

from fastapi import (APIRouter, BackgroundTasks, Body, Depends, HTTPException,
                     Query, status)

from ...models.agent import AgentRunStatus, BrowserTask
from ...models.user import User
from ...utils.auth import get_current_active_user
from .service import browser_service

# Create router
router = APIRouter()

# Logger
logger = logging.getLogger(__name__)

@router.post("/automate", response_model=Dict[str, Any])
async def run_browser_automation(
    instructions: str = Body(...),
    url: Optional[str] = Body(None),
    developer_mode: bool = Body(False),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_active_user)
):
    """
    Run browser automation with instructions.
    """
    try:
        # Start browser task in the background
        task_id = await browser_service.start_browser_task(
            user_id=current_user.id,
            instructions=instructions,
            url=url,
            developer_mode=developer_mode,
            headless=current_user.preferences.browser_headless,
            background_tasks=background_tasks
        )
        
        return {
            "success": True,
            "message": "Browser automation started",
            "data": {"task_id": task_id}
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting browser automation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error starting browser automation"
        )

@router.get("/task/{task_id}", response_model=Dict[str, Any])
async def get_browser_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a browser task by ID.
    """
    try:
        task = await browser_service.get_browser_task(task_id, current_user.id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Browser task not found"
            )
            
        return {
            "success": True,
            "message": "Browser task retrieved",
            "data": task
        }
    except Exception as e:
        logger.error(f"Error retrieving browser task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving browser task"
        )

@router.get("/tasks", response_model=Dict[str, Any])
async def get_browser_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[AgentRunStatus] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a list of browser tasks for the current user.
    """
    try:
        tasks, total = await browser_service.get_browser_tasks(
            user_id=current_user.id,
            page=page,
            limit=limit,
            status=status
        )
        
        return {
            "success": True,
            "message": "Browser tasks retrieved",
            "data": {
                "tasks": tasks,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving browser tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving browser tasks"
        )

@router.delete("/task/{task_id}", response_model=Dict[str, Any])
async def cancel_browser_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancel a browser task.
    """
    try:
        success = await browser_service.cancel_browser_task(task_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Browser task not found or already completed"
            )
            
        return {
            "success": True,
            "message": "Browser task cancelled"
        }
    except Exception as e:
        logger.error(f"Error cancelling browser task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error cancelling browser task"
        )
```

Implement the browser service:

```python
# api/browser/service.py
import base64
import logging
import os
import uuid
from datetime import datetime
from io import BytesIO
from typing import Dict, List, Optional, Tuple, Union

from fastapi import BackgroundTasks
from PIL import Image

from ...browser.solana_web_browser import SolanaWebBrowser, SolanaDeveloperBrowser
from ...config import settings
from ...models.agent import AgentRunStatus, BrowserTask
from ...utils.database import MongoDB

# Logger
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
        """
        Start a browser automation task.
        
        Args:
            user_id: The ID of the user
            instructions: The instructions to run
            url: The URL to navigate to (optional)
            developer_mode: Whether to use developer mode
            headless: Whether to run in headless mode
            background_tasks: FastAPI background tasks
            
        Returns:
            str: The ID of the created task
            
        Raises:
            ValueError: If the instructions are empty
        """
        if not instructions or instructions.strip() == "":
            raise ValueError("Instructions cannot be empty")
            
        # Create task ID
        task_id = str(uuid.uuid4())
        
        # Create screenshot directory if it doesn't exist
        screenshots_dir = os.path.join(os.getcwd(), "data", "screenshots", user_id)
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # Create task document
        now = datetime.utcnow()
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
        
        # Insert task into database
        await MongoDB.db.browser_tasks.insert_one(task_doc)
        
        # Add task to background tasks
        background_tasks.add_task(
            self._run_browser_task,
            task_id,
            user_id,
            instructions,
            url,
            developer_mode,
            headless,
            screenshots_dir
        )
        
        return task_id
        
    async def _run_browser_task(
        self,
        task_id: str,
        user_id: str,
        instructions: str,
        url: Optional[str],
        developer_mode: bool,
        headless: bool,
        screenshots_dir: str
    ) -> None:
        """
        Run the browser automation task in the background.
        
        Args:
            task_id: The ID of the task
            user_id: The ID of the user
            instructions: The instructions to run
            url: The URL to navigate to (optional)
            developer_mode: Whether to use developer mode
            headless: Whether to run in headless mode
            screenshots_dir: The directory to save screenshots
            
        Returns:
            None
        """
        browser = None
        try:
            # Update task status to running
            now = datetime.utcnow()
            await MongoDB.db.browser_tasks.update_one(
                {"_id": task_id},
                {"$set": {
                    "status": AgentRunStatus.RUNNING,
                    "started_at": now.isoformat()
                }}
            )
            
            # Create browser instance
            if developer_mode:
                browser = SolanaDeveloperBrowser(
                    headless=headless,
                    model_id=settings.DEFAULT_MODEL,
                    api_key=settings.ANTHROPIC_API_KEY
                )
            else:
                browser = SolanaWebBrowser(
                    headless=headless,
                    model_id=settings.DEFAULT_MODEL,
                    api_key=settings.ANTHROPIC_API_KEY
                )
            
            # Build instructions
            full_instructions = instructions
            if url:
                full_instructions = f"Go to {url} and then {instructions}"
            
            # Run browser automation
            result = browser.run(full_instructions)
            
            # Save screenshots
            screenshots = []
            if browser.agent and browser.agent.memory and browser.agent.memory.steps:
                for i, step in enumerate(browser.agent.memory.steps):
                    if hasattr(step, 'observations_images') and step.observations_images:
                        for j, img in enumerate(step.observations_images):
                            screenshot_path = os.path.join(
                                screenshots_dir,
                                f"{task_id}_{i}_{j}.png"
                            )
                            img.save(screenshot_path)
                            screenshots.append(screenshot_path)
            
            # Update task with result
            end_time = datetime.utcnow()
            duration = (end_time - now).total_seconds()
            
            await MongoDB.db.browser_tasks.update_one(
                {"_id": task_id},
                {"$set": {
                    "status": AgentRunStatus.COMPLETED,
                    "result": result,
                    "screenshots": screenshots,
                    "completed_at": end_time.isoformat(),
                    "duration_seconds": duration
                }}
            )
            
        except Exception as e:
            logger.error(f"Error running browser automation: {e}")
            
            # Update task with error
            end_time = datetime.utcnow()
            duration = (end_time - now).total_seconds() if 'now' in locals() else 0
            
            await MongoDB.db.browser_tasks.update_one(
                {"_id": task_id},
                {"$set": {
                    "status": AgentRunStatus.FAILED,
                    "error": str(e),
                    "completed_at": end_time.isoformat(),
                    "duration_seconds": duration
                }}
            )
        finally:
            # Close browser if it was created
            if browser:
                browser.close()
        
    async def get_browser_task(self, task_id: str, user_id: str) -> Optional[Dict]:
        """
        Get a browser task by ID.
        
        Args:
            task_id: The ID of the task
            user_id: The ID of the user
            
        Returns:
            Optional[Dict]: The browser task if found, None otherwise
        """
        task = await MongoDB.db.browser_tasks.find_one({"_id": task_id, "user_id": user_id})
        
        # Convert screenshots to base64
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
        """
        Get a list of browser tasks for a user.
        
        Args:
            user_id: The ID of the user
            page: The page number
            limit: The number of tasks per page
            status: Filter tasks by status
            
        Returns:
            Tuple[List[Dict], int]: The list of tasks and the total count
        """
        # Build query
        query = {"user_id": user_id}
        if status:
            query["status"] = status
            
        # Calculate skip
        skip = (page - 1) * limit
        
        # Get tasks
        cursor = MongoDB.db.browser_tasks.find(query)
        
        # Get total count
        total = await MongoDB.db.browser_tasks.count_documents(query)
        
        # Apply pagination
        cursor = cursor.sort("started_at", -1).skip(skip).limit(limit)
        
        # Convert cursor to list
        tasks = await cursor.to_list(length=limit)
        
        # Don't include screenshots in the list view
        for task in tasks:
            if "screenshots" in task:
                task["screenshots"] = [f"Screenshot {i+1}" for i in range(len(task["screenshots"]))]
        
        return tasks, total
        
    async def cancel_browser_task(self, task_id: str, user_id: str) -> bool:
        """
        Cancel a browser task.
        
        Args:
            task_id: The ID of the task
            user_id: The ID of the user
            
        Returns:
            bool: True if the task was cancelled, False otherwise
        """
        # Check if task exists and is pending or running
        task = await MongoDB.db.browser_tasks.find_one({
            "_id": task_id,
            "user_id": user_id,
            "status": {"$in": [AgentRunStatus.PENDING, AgentRunStatus.RUNNING]}
        })
        
        if not task:
            return False
            
        # Update task status to cancelled
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

# Create service instance
browser_service = BrowserService()
```

## Update Main Application

Now, let's update the main application to include our API router:

```bash
cd ../../../
```

Edit `main.py`:

```python
import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.router import api_router
from src.config import settings
from src.utils.database import initialize_db, shutdown_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up server...")
    await initialize_db()
    
    yield
    
    # Shutdown
    logger.info("Shutting down server...")
    await shutdown_db()

# Create FastAPI application
app = FastAPI(
    title="SolanaAI Agent API",
    description="API for SolanaAI Agent platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "SolanaAI Agent API",
        "version": "1.0.0",
        "status": "online",
        "environment": settings.ENVIRONMENT,
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
```

This completes the core API endpoints for our backend server. In the next part, we'll implement the core agent and browser modules that power our platform.
