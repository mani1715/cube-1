"""Background task utilities for async operations."""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
import io
import csv

logger = logging.getLogger(__name__)


# ============= EMAIL MOCK SERVICE =============

class EmailService:
    """Mock email service for sending notifications."""
    
    @staticmethod
    async def send_welcome_email(to_email: str, admin_name: str):
        """Send welcome email to new admin (mocked)."""
        logger.info(f"[MOCK EMAIL] Sending welcome email to {to_email}")
        logger.info(f"[MOCK EMAIL] Subject: Welcome to A-Cube Admin Panel")
        logger.info(f"[MOCK EMAIL] Body: Hello {admin_name}, welcome to the A-Cube platform!")
        return True
    
    @staticmethod
    async def send_session_confirmation(to_email: str, session_data: Dict[str, Any]):
        """Send session confirmation email (mocked)."""
        logger.info(f"[MOCK EMAIL] Sending session confirmation to {to_email}")
        logger.info(f"[MOCK EMAIL] Subject: Session Booking Confirmed")
        logger.info(f"[MOCK EMAIL] Session ID: {session_data.get('id')}")
        return True
    
    @staticmethod
    async def send_event_registration(to_email: str, event_data: Dict[str, Any]):
        """Send event registration email (mocked)."""
        logger.info(f"[MOCK EMAIL] Sending event registration to {to_email}")
        logger.info(f"[MOCK EMAIL] Subject: Event Registration Confirmed")
        logger.info(f"[MOCK EMAIL] Event: {event_data.get('title')}")
        return True
    
    @staticmethod
    async def send_volunteer_application_received(to_email: str, volunteer_data: Dict[str, Any]):
        """Send volunteer application confirmation (mocked)."""
        logger.info(f"[MOCK EMAIL] Sending volunteer application confirmation to {to_email}")
        logger.info(f"[MOCK EMAIL] Subject: Volunteer Application Received")
        logger.info(f"[MOCK EMAIL] Name: {volunteer_data.get('name')}")
        return True
    
    @staticmethod
    async def send_contact_form_acknowledgment(to_email: str, contact_data: Dict[str, Any]):
        """Send contact form acknowledgment (mocked)."""
        logger.info(f"[MOCK EMAIL] Sending contact form acknowledgment to {to_email}")
        logger.info(f"[MOCK EMAIL] Subject: We've received your message")
        logger.info(f"[MOCK EMAIL] Reference ID: {contact_data.get('id')}")
        return True
    
    @staticmethod
    async def send_bulk_operation_report(to_email: str, operation_type: str, result: Dict[str, Any]):
        """Send bulk operation completion report to admin (mocked)."""
        logger.info(f"[MOCK EMAIL] Sending bulk operation report to {to_email}")
        logger.info(f"[MOCK EMAIL] Subject: Bulk {operation_type} Operation Complete")
        logger.info(f"[MOCK EMAIL] Success: {result.get('success_count')}, Failed: {result.get('failed_count')}")
        return True


# ============= AUDIT EXPORT SERVICE =============

class AuditExportService:
    """Service for exporting audit logs to CSV."""
    
    @staticmethod
    async def export_audit_logs(
        admin_email: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10000
    ) -> str:
        """Export audit logs to CSV and return file path."""
        logger.info(f"[BACKGROUND JOB] Starting audit log export for {admin_email}")
        
        try:
            mongo_url = os.environ['MONGO_URL']
            client = AsyncIOMotorClient(mongo_url)
            db = client[os.environ['DB_NAME']]
            
            # Build query
            query = filters or {}
            
            # Fetch logs
            logs = await db.admin_logs.find(query).limit(limit).to_list(limit)
            
            logger.info(f"[BACKGROUND JOB] Fetched {len(logs)} audit logs")
            
            # Generate CSV content
            if not logs:
                logger.warning(f"[BACKGROUND JOB] No logs found for export")
                return None
            
            # Create CSV in memory
            output = io.StringIO()
            fieldnames = ['timestamp', 'admin_email', 'action', 'entity', 'entity_id', 'details']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            
            writer.writeheader()
            for log in logs:
                writer.writerow({
                    'timestamp': log.get('timestamp', ''),
                    'admin_email': log.get('admin_email', ''),
                    'action': log.get('action', ''),
                    'entity': log.get('entity', ''),
                    'entity_id': log.get('entity_id', ''),
                    'details': str(log.get('details', ''))
                })
            
            csv_content = output.getvalue()
            output.close()
            
            # Save to file (in production, would upload to S3 or similar)
            export_dir = "/app/backend/static/exports"
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audit_logs_{timestamp}.csv"
            filepath = os.path.join(export_dir, filename)
            
            with open(filepath, 'w') as f:
                f.write(csv_content)
            
            logger.info(f"[BACKGROUND JOB] Audit log export complete: {filename}")
            
            # Send email notification (mocked)
            await EmailService.send_bulk_operation_report(
                to_email=admin_email,
                operation_type="Audit Export",
                result={
                    "success_count": len(logs),
                    "failed_count": 0,
                    "file": filename
                }
            )
            
            return filename
            
        except Exception as e:
            logger.error(f"[BACKGROUND JOB] Error exporting audit logs: {str(e)}")
            raise


# ============= BULK OPERATIONS SERVICE =============

class BulkOperationsService:
    """Service for executing bulk operations in background."""
    
    @staticmethod
    async def bulk_delete(
        collection: str,
        ids: List[str],
        admin_email: str
    ) -> Dict[str, Any]:
        """Delete multiple records in background."""
        logger.info(f"[BACKGROUND JOB] Starting bulk delete: {len(ids)} items from {collection}")
        
        try:
            mongo_url = os.environ['MONGO_URL']
            client = AsyncIOMotorClient(mongo_url)
            db = client[os.environ['DB_NAME']]
            
            collection_ref = db[collection]
            
            success_count = 0
            failed_count = 0
            failed_ids = []
            
            for item_id in ids:
                try:
                    result = await collection_ref.delete_one({"id": item_id})
                    if result.deleted_count > 0:
                        success_count += 1
                    else:
                        failed_count += 1
                        failed_ids.append(item_id)
                except Exception as e:
                    logger.error(f"[BACKGROUND JOB] Failed to delete {item_id}: {str(e)}")
                    failed_count += 1
                    failed_ids.append(item_id)
            
            result = {
                "success_count": success_count,
                "failed_count": failed_count,
                "failed_ids": failed_ids
            }
            
            logger.info(f"[BACKGROUND JOB] Bulk delete complete: {success_count} success, {failed_count} failed")
            
            # Send completion email
            await EmailService.send_bulk_operation_report(
                to_email=admin_email,
                operation_type="Delete",
                result=result
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[BACKGROUND JOB] Error in bulk delete: {str(e)}")
            raise
    
    @staticmethod
    async def bulk_status_update(
        collection: str,
        ids: List[str],
        new_status: str,
        admin_email: str
    ) -> Dict[str, Any]:
        """Update status of multiple records in background."""
        logger.info(f"[BACKGROUND JOB] Starting bulk status update: {len(ids)} items to '{new_status}'")
        
        try:
            mongo_url = os.environ['MONGO_URL']
            client = AsyncIOMotorClient(mongo_url)
            db = client[os.environ['DB_NAME']]
            
            collection_ref = db[collection]
            
            success_count = 0
            failed_count = 0
            failed_ids = []
            
            for item_id in ids:
                try:
                    result = await collection_ref.update_one(
                        {"id": item_id},
                        {"$set": {"status": new_status}}
                    )
                    if result.matched_count > 0:
                        success_count += 1
                    else:
                        failed_count += 1
                        failed_ids.append(item_id)
                except Exception as e:
                    logger.error(f"[BACKGROUND JOB] Failed to update {item_id}: {str(e)}")
                    failed_count += 1
                    failed_ids.append(item_id)
            
            result = {
                "success_count": success_count,
                "failed_count": failed_count,
                "failed_ids": failed_ids,
                "new_status": new_status
            }
            
            logger.info(f"[BACKGROUND JOB] Bulk status update complete: {success_count} success, {failed_count} failed")
            
            # Send completion email
            await EmailService.send_bulk_operation_report(
                to_email=admin_email,
                operation_type="Status Update",
                result=result
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[BACKGROUND JOB] Error in bulk status update: {str(e)}")
            raise
