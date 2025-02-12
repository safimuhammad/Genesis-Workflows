from fastapi import APIRouter, Body
from celery.schedules import crontab
import os
from fastapi import Depends
from models import User
import uuid
import os
from main import get_current_user

router = APIRouter(
    tags=["Background"],
)

# Celery Client Setup
from celery import Celery

celery_client = Celery(
    broker=os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "rpc://"),
)


# Endpoint to enqueue a task
@router.post("/enqueue")
def enqueue_example_task(data: dict, current_user: User = Depends(get_current_user)):
    chain = data.get("chain", {})
    chain_id = chain.get("chain_id")
    message = chain.get("message")
    chain = chain.get("chain")
    

    task = celery_client.send_task(
        "app.tasks.process_chain_task",
        kwargs={"chain_id": chain_id, "chain": chain, "message": message},
    )
    return {"task_id_new": task.id, "status": "Task has been enqueued."}


# Endpoint to get task result
@router.get("/task_result/{task_id}")
def get_task_result(task_id: str, current_user: User = Depends(get_current_user)):
    result = celery_client.AsyncResult(task_id)
    if result.state == "PENDING":
        return {"task_id": task_id, "status": result.state, "result": None}
    elif result.state == "SUCCESS":
        return {"task_id": task_id, "status": result.state, "result": result.result}
    else:
        return {"task_id": task_id, "status": result.state, "result": str(result.info)}


@router.post("/schedule")
def schedule_periodic_task(data: dict, current_user: User = Depends(get_current_user)):
    cron_data = data.get("cron", {})
    chain = data.get("chain", {})
    chain_id = chain.get("chain_id")
    message = chain.get("message")
    chain_value = chain.get("chain")
    
    # Create a unique key for this scheduled task
    schedule_id = f"process-chain-{uuid.uuid4().hex}"
    
    # Construct a crontab schedule; use "*" defaults if not provided
    minute = cron_data.get("minute", "*")
    hour = cron_data.get("hour", "*")
    day_of_week = cron_data.get("day_of_week", "*")
    day_of_month = cron_data.get("day_of_month", "*")
    month_of_year = cron_data.get("month_of_year", "*")
    
    # Update the beat schedule in the Celery configuration
    celery_client.conf.beat_schedule[schedule_id] = {
        "task": "celery_service.app.tasks.process_chain_task",
        "schedule": crontab(
            minute=minute,
            hour=hour,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
        ),
        "kwargs": {"chain_id": chain_id, "chain": chain_value, "message": message},
    }
    
    return {
        "schedule_id": schedule_id,
        "status": "Periodic task scheduled successfully.",
        "schedule": celery_client.conf.beat_schedule[schedule_id],
    }
