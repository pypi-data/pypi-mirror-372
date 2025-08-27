"""Celery Generator - Generates Celery configuration for background tasks"""

from ...generators.base_generator import BaseGenerator


class CeleryGenerator(BaseGenerator):
    """Generates Celery configuration for background tasks"""

    def should_generate(self):
        return self.config.include_celery

    def generate(self):
        """Generate Celery files"""
        if not self.config.include_celery:
            return

        # Generate celery.py
        celery_content = self._get_celery_template()
        self.write_file(f"{self.config.path}/app/core/celery.py", celery_content)

        # Generate tasks.py
        tasks_content = self._get_tasks_template()
        self.write_file(f"{self.config.path}/app/core/tasks.py", tasks_content)

    def _get_celery_template(self) -> str:
        """Get Celery configuration template"""
        template = f'''"""
Celery configuration for {self.config.name}
"""

from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "{self.config.name}",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.core.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Auto-discover tasks
celery_app.autodiscover_tasks()
'''
        return template

    def _get_tasks_template(self) -> str:
        """Get tasks template"""
        template = f'''"""
Celery tasks for {self.config.name}
"""

import time
from celery import current_task
from app.core.celery import celery_app


@celery_app.task(bind=True)
def example_task(self, seconds: int = 10):
    """
    Example background task that simulates work
    """
    for i in range(seconds):
        # Update task progress
        current_task.update_state(
            state="PROGRESS",
            meta={{"current": i + 1, "total": seconds, "status": f"Processing step {{i + 1}}..."}}
        )
        time.sleep(1)
    
    return {{"status": "Task completed!", "result": f"Processed {{seconds}} steps"}}


@celery_app.task
def send_email_task(email: str, subject: str, body: str):
    """
    Example email sending task
    """
    # Implement your email sending logic here
    print(f"Sending email to {{email}} with subject: {{subject}}")
    time.sleep(2)  # Simulate email sending delay
    return f"Email sent to {{email}}"


@celery_app.task
def process_data_task(data: dict):
    """
    Example data processing task
    """
    # Implement your data processing logic here
    print(f"Processing data: {{data}}")
    time.sleep(5)  # Simulate processing delay
    return {{"status": "success", "processed_data": data}}
'''
        return template
