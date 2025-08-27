import json
from typing import Any, Dict, Optional

from flink_job_manager_api import Client
from flink_job_manager_api.api.default import cancel_job, get_dashboard_configuration
from flink_job_manager_api.models import DashboardConfiguration, TerminationMode
from pydantic import BaseModel

from resinkit_api.core.config import settings


class JobExecutionResult(BaseModel):
    job_id: str
    status: Optional[str] = None
    application_status: Optional[str] = None
    job_execution_result: Dict[str, Any] = {}
    raw_response: Dict[str, Any] = {}


class FlinkJobManager:
    def __init__(self):
        self.client = Client(base_url=settings.FLINK_JOB_MANAGER_URL)

    async def get_config(self) -> "DashboardConfiguration":
        res: DashboardConfiguration = await get_dashboard_configuration.asyncio(client=self.client)
        return res

    async def get_job_execution_result(self, job_id: str) -> JobExecutionResult | None:
        """
        Get job execution result from the Flink Job Manager.

        Args:
            job_id: The Flink job ID

        Returns:
            JobExecutionResult containing job execution result including status, or None if job not found

        Response example:
        {
          "status": {
            "id": "COMPLETED"
          },
          "job-execution-result": {
            "id": "36b456babf6da7af738baac17393668d",
            "application-status": "CANCELED",
            "accumulator-results": {},
            "net-runtime": 134090
          }
        }
        """
        try:
            raw_response = await self.client.get_async_httpx_client().request(
                method="GET",
                url=f"/jobs/{job_id}/execution-result",
            )

            if raw_response.status_code != 200:
                return None

            response_data = raw_response.json()

            # Extract the relevant status information
            # The response has both status.id and job-execution-result.application-status
            result = JobExecutionResult(
                job_id=job_id,
                status=response_data.get("status", {}).get("id"),
                application_status=response_data.get("job-execution-result", {}).get("application-status"),
                job_execution_result=response_data.get("job-execution-result", {}),
                raw_response=response_data,
            )

            return result

        except Exception as e:
            # Log the error but don't raise it, return None to indicate job not found
            return None

    async def get_job_exceptions(self, job_id: str) -> str | None:
        """
        Response of GET /jobs/{job_id}/exceptions:
        {
          "root-exception": "org.apache.flink.util.FlinkException: xxx",
          "timestamp": 1748676177115,
          "all-exceptions": [],
          "truncated": false,
          "exceptionHistory": {
            "entries": [
              {
                "exceptionName": "org.apache.flink.util.FlinkException",
                "stacktrace": "xxx",
                "timestamp": 1748676177115,
                "failureLabels": {},
                "concurrentExceptions": []
              }
            ],
            "truncated": false
          }
        }
        """
        raw_response = await self.client.get_async_httpx_client().request(
            method="GET",
            url=f"/jobs/{job_id}/exceptions",
        )

        if raw_response.status_code != 200:
            return None

        root_exception = raw_response.json().get("root-exception")
        if root_exception:
            return root_exception

        excpetion_entries = raw_response.json().get("exceptionHistory", {}).get("entries", [])
        if excpetion_entries:
            return excpetion_entries[0].get("stacktrace")

        return None

    async def cancel_all_jobs(self, job_ids: list[str]) -> None:
        """
        Cancel jobs.
        """
        if not job_ids:
            return

        for job_id in job_ids:
            await cancel_job.asyncio_detailed(job_id, client=self.client, mode=TerminationMode.CANCEL)
