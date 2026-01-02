from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class IngestionJobStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class IngestionJob:
    """
    Represents a complete ingestion process for a single book or website.
    """
    id: str  # unique identifier for the job
    source_url: str  # root URL being ingested
    status: IngestionJobStatus  # current status of the job
    start_time: datetime = field(default_factory=datetime.now)  # when job started
    end_time: Optional[datetime] = None  # when job completed/failed
    total_pages: int = 0  # total number of pages discovered
    processed_pages: int = 0  # number of pages successfully processed
    total_chunks: int = 0  # total number of content chunks created
    failed_pages: List[str] = field(default_factory=list)  # URLs that failed during processing
    error_log: str = ""  # summary of errors encountered

    def __post_init__(self):
        """
        Validate the IngestionJob after initialization
        """
        if not self.id:
            raise ValueError("IngestionJob.id must be provided")
        if not self.source_url:
            raise ValueError("IngestionJob.source_url must be provided")
        if self.status not in IngestionJobStatus:
            raise ValueError(f"IngestionJob.status must be one of {list(IngestionJobStatus)}")
        if self.start_time and self.end_time and self.start_time > self.end_time:
            raise ValueError("IngestionJob.start_time must be before end_time")
        if self.processed_pages > self.total_pages:
            raise ValueError("IngestionJob.processed_pages cannot exceed total_pages")

    def complete_job(self):
        """
        Mark the job as completed
        """
        self.status = IngestionJobStatus.COMPLETED
        self.end_time = datetime.now()

    def fail_job(self, error_message: str = ""):
        """
        Mark the job as failed
        """
        self.status = IngestionJobStatus.FAILED
        self.end_time = datetime.now()
        if error_message:
            self.error_log = error_message

    def add_failed_page(self, url: str, error: str = ""):
        """
        Add a failed page to the job
        """
        self.failed_pages.append(url)
        if error:
            self.error_log += f"\nFailed to process {url}: {error}"

    def update_progress(self, pages_processed: int, chunks_created: int):
        """
        Update the job's progress
        """
        self.processed_pages = pages_processed
        self.total_chunks = chunks_created

    @classmethod
    def create_new(cls, source_url: str) -> 'IngestionJob':
        """
        Create a new ingestion job with a unique ID
        """
        return cls(
            id=str(uuid.uuid4()),
            source_url=source_url,
            status=IngestionJobStatus.PENDING
        )


@dataclass
class IngestionJobStats:
    """
    Statistics for an ingestion job
    """
    total_pages: int
    processed_pages: int
    failed_pages: int
    total_chunks: int
    completion_percentage: float

    @classmethod
    def from_ingestion_job(cls, job: IngestionJob) -> 'IngestionJobStats':
        """
        Create stats from an ingestion job
        """
        completion_percentage = (job.processed_pages / job.total_pages * 100) if job.total_pages > 0 else 0
        return cls(
            total_pages=job.total_pages,
            processed_pages=job.processed_pages,
            failed_pages=len(job.failed_pages),
            total_chunks=job.total_chunks,
            completion_percentage=completion_percentage
        )


if __name__ == "__main__":
    # Example usage
    job = IngestionJob.create_new("https://example-book.com")
    print(f"Created new ingestion job: {job.id}")
    print(f"Source URL: {job.source_url}")
    print(f"Status: {job.status.value}")
    print(f"Start time: {job.start_time}")

    # Simulate processing
    job.update_progress(pages_processed=5, chunks_created=12)
    job.add_failed_page("https://example-book.com/page404", "Page not found")
    job.complete_job()

    print(f"Status: {job.status.value}")
    print(f"End time: {job.end_time}")
    print(f"Processed pages: {job.processed_pages}")
    print(f"Total chunks: {job.total_chunks}")
    print(f"Failed pages: {job.failed_pages}")

    # Get stats
    stats = IngestionJobStats.from_ingestion_job(job)
    print(f"Completion percentage: {stats.completion_percentage}%")