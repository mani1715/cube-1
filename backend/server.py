from fastapi import FastAPI, APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from models import (
    SessionBooking, SessionBookingCreate,
    Event, EventCreate, EventRegistration,
    Blog, BlogCreate,
    Career, CareerCreate, CareerApplication,
    Volunteer, VolunteerCreate,
    Psychologist, PsychologistCreate,
    ContactForm, ContactFormCreate,
    Payment, PaymentCreate
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="A-Cube Mental Health Platform API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============= SESSION BOOKING ENDPOINTS =============
@api_router.post("/sessions/book", response_model=SessionBooking, status_code=status.HTTP_201_CREATED)
async def book_session(booking: SessionBookingCreate):
    """Book a therapy session"""
    try:
        booking_obj = SessionBooking(**booking.dict())
        await db.session_bookings.insert_one(booking_obj.dict())
        logger.info(f"New session booking created: {booking_obj.id}")
        return booking_obj
    except Exception as e:
        logger.error(f"Error booking session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to book session")


@api_router.get("/sessions", response_model=List[SessionBooking])
async def get_all_sessions(status_filter: Optional[str] = None):
    """Get all session bookings with optional status filter"""
    try:
        query = {"status": status_filter} if status_filter else {}
        bookings = await db.session_bookings.find(query).to_list(1000)
        return [SessionBooking(**booking) for booking in bookings]
    except Exception as e:
        logger.error(f"Error fetching sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch sessions")


@api_router.get("/sessions/{session_id}", response_model=SessionBooking)
async def get_session(session_id: str):
    """Get a specific session booking"""
    booking = await db.session_bookings.find_one({"id": session_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionBooking(**booking)


@api_router.patch("/sessions/{session_id}/status")
async def update_session_status(session_id: str, new_status: str):
    """Update session booking status"""
    result = await db.session_bookings.update_one(
        {"id": session_id},
        {"$set": {"status": new_status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Status updated successfully"}


# ============= EVENT ENDPOINTS =============
@api_router.post("/events", response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate):
    """Create a new event"""
    try:
        event_obj = Event(**event.dict())
        await db.events.insert_one(event_obj.dict())
        logger.info(f"New event created: {event_obj.id}")
        return event_obj
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create event")


@api_router.get("/events", response_model=List[Event])
async def get_all_events(is_active: Optional[bool] = None):
    """Get all events with optional active filter"""
    try:
        query = {"is_active": is_active} if is_active is not None else {}
        events = await db.events.find(query).sort("date", -1).to_list(1000)
        return [Event(**event) for event in events]
    except Exception as e:
        logger.error(f"Error fetching events: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch events")


@api_router.get("/events/{event_id}", response_model=Event)
async def get_event(event_id: str):
    """Get a specific event"""
    event = await db.events.find_one({"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return Event(**event)


@api_router.post("/events/{event_id}/register", response_model=EventRegistration, status_code=status.HTTP_201_CREATED)
async def register_for_event(event_id: str, full_name: str, email: str, phone: Optional[str] = None):
    """Register for an event"""
    try:
        # Check if event exists
        event = await db.events.find_one({"id": event_id})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        registration = EventRegistration(
            event_id=event_id,
            full_name=full_name,
            email=email,
            phone=phone
        )
        await db.event_registrations.insert_one(registration.dict())
        logger.info(f"New event registration: {registration.id}")
        return registration
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering for event: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to register for event")


# ============= BLOG ENDPOINTS =============
@api_router.post("/blogs", response_model=Blog, status_code=status.HTTP_201_CREATED)
async def create_blog(blog: BlogCreate):
    """Create a new blog post"""
    try:
        blog_obj = Blog(**blog.dict())
        await db.blogs.insert_one(blog_obj.dict())
        logger.info(f"New blog created: {blog_obj.id}")
        return blog_obj
    except Exception as e:
        logger.error(f"Error creating blog: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create blog")


@api_router.get("/blogs", response_model=List[Blog])
async def get_all_blogs(category: Optional[str] = None, featured: Optional[bool] = None):
    """Get all blog posts with optional filters"""
    try:
        query = {}
        if category:
            query["category"] = category
        if featured is not None:
            query["featured"] = featured
        
        blogs = await db.blogs.find(query).sort("date", -1).to_list(1000)
        return [Blog(**blog) for blog in blogs]
    except Exception as e:
        logger.error(f"Error fetching blogs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch blogs")


@api_router.get("/blogs/{blog_id}", response_model=Blog)
async def get_blog(blog_id: str):
    """Get a specific blog post"""
    blog = await db.blogs.find_one({"id": blog_id})
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return Blog(**blog)


# ============= CAREER ENDPOINTS =============
@api_router.post("/careers", response_model=Career, status_code=status.HTTP_201_CREATED)
async def create_job_posting(job: CareerCreate):
    """Create a new job posting"""
    try:
        job_obj = Career(**job.dict())
        await db.careers.insert_one(job_obj.dict())
        logger.info(f"New job posting created: {job_obj.id}")
        return job_obj
    except Exception as e:
        logger.error(f"Error creating job posting: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create job posting")


@api_router.get("/careers", response_model=List[Career])
async def get_all_jobs(is_active: Optional[bool] = None):
    """Get all job postings with optional active filter"""
    try:
        query = {"is_active": is_active} if is_active is not None else {}
        jobs = await db.careers.find(query).sort("posted_at", -1).to_list(1000)
        return [Career(**job) for job in jobs]
    except Exception as e:
        logger.error(f"Error fetching job postings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch job postings")


@api_router.get("/careers/{job_id}", response_model=Career)
async def get_job(job_id: str):
    """Get a specific job posting"""
    job = await db.careers.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return Career(**job)


@api_router.post("/careers/{job_id}/apply", response_model=CareerApplication, status_code=status.HTTP_201_CREATED)
async def apply_for_job(job_id: str, application: CareerApplication):
    """Apply for a job"""
    try:
        # Check if job exists
        job = await db.careers.find_one({"id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        application.job_id = job_id
        await db.career_applications.insert_one(application.dict())
        logger.info(f"New job application: {application.id}")
        return application
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying for job: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to apply for job")


# ============= VOLUNTEER ENDPOINTS =============
@api_router.post("/volunteers", response_model=Volunteer, status_code=status.HTTP_201_CREATED)
async def create_volunteer_application(volunteer: VolunteerCreate):
    """Submit volunteer application"""
    try:
        volunteer_obj = Volunteer(**volunteer.dict())
        await db.volunteers.insert_one(volunteer_obj.dict())
        logger.info(f"New volunteer application: {volunteer_obj.id}")
        return volunteer_obj
    except Exception as e:
        logger.error(f"Error creating volunteer application: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit volunteer application")


@api_router.get("/volunteers", response_model=List[Volunteer])
async def get_all_volunteers(status_filter: Optional[str] = None):
    """Get all volunteer applications with optional status filter"""
    try:
        query = {"status": status_filter} if status_filter else {}
        volunteers = await db.volunteers.find(query).to_list(1000)
        return [Volunteer(**volunteer) for volunteer in volunteers]
    except Exception as e:
        logger.error(f"Error fetching volunteers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch volunteers")


# ============= PSYCHOLOGIST ENDPOINTS =============
@api_router.post("/psychologists", response_model=Psychologist, status_code=status.HTTP_201_CREATED)
async def create_psychologist(psychologist: PsychologistCreate):
    """Create a new psychologist profile"""
    try:
        psychologist_obj = Psychologist(**psychologist.dict())
        await db.psychologists.insert_one(psychologist_obj.dict())
        logger.info(f"New psychologist profile created: {psychologist_obj.id}")
        return psychologist_obj
    except Exception as e:
        logger.error(f"Error creating psychologist profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create psychologist profile")


@api_router.get("/psychologists", response_model=List[Psychologist])
async def get_all_psychologists(is_active: Optional[bool] = None):
    """Get all psychologist profiles with optional active filter"""
    try:
        query = {"is_active": is_active} if is_active is not None else {}
        psychologists = await db.psychologists.find(query).to_list(1000)
        return [Psychologist(**psychologist) for psychologist in psychologists]
    except Exception as e:
        logger.error(f"Error fetching psychologists: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch psychologists")


@api_router.get("/psychologists/{psychologist_id}", response_model=Psychologist)
async def get_psychologist(psychologist_id: str):
    """Get a specific psychologist profile"""
    psychologist = await db.psychologists.find_one({"id": psychologist_id})
    if not psychologist:
        raise HTTPException(status_code=404, detail="Psychologist not found")
    return Psychologist(**psychologist)


# ============= CONTACT FORM ENDPOINTS =============
@api_router.post("/contact", response_model=ContactForm, status_code=status.HTTP_201_CREATED)
async def submit_contact_form(contact: ContactFormCreate):
    """Submit a contact form"""
    try:
        contact_obj = ContactForm(**contact.dict())
        await db.contact_forms.insert_one(contact_obj.dict())
        logger.info(f"New contact form submission: {contact_obj.id}")
        return contact_obj
    except Exception as e:
        logger.error(f"Error submitting contact form: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit contact form")


@api_router.get("/contact", response_model=List[ContactForm])
async def get_all_contact_forms(status_filter: Optional[str] = None):
    """Get all contact form submissions with optional status filter"""
    try:
        query = {"status": status_filter} if status_filter else {}
        forms = await db.contact_forms.find(query).to_list(1000)
        return [ContactForm(**form) for form in forms]
    except Exception as e:
        logger.error(f"Error fetching contact forms: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch contact forms")


# ============= PAYMENT ENDPOINTS =============
@api_router.post("/payments", response_model=Payment, status_code=status.HTTP_201_CREATED)
async def process_payment(payment: PaymentCreate):
    """Process a payment (mock)"""
    try:
        payment_obj = Payment(**payment.dict())
        await db.payments.insert_one(payment_obj.dict())
        logger.info(f"New payment processed: {payment_obj.id}")
        return payment_obj
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process payment")


@api_router.get("/payments/{payment_id}", response_model=Payment)
async def get_payment(payment_id: str):
    """Get payment details"""
    payment = await db.payments.find_one({"id": payment_id})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return Payment(**payment)


# ============= HEALTH CHECK =============
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "A-Cube Mental Health Platform API"}


@api_router.get("/")
async def root():
    return {
        "message": "A-Cube Mental Health Platform API",
        "version": "1.0.0",
        "status": "active"
    }


# Include the router in the main app
app.include_router(api_router)

# Include admin routers
from api.admin.admin_router import admin_router
from api.admin.auth import auth_router
from api.admin.bulk_operations import bulk_router
from api.admin.search import search_router
from api.admin.error_tracking import error_router
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(bulk_router)
app.include_router(search_router)
app.include_router(error_router)

# Mount static files for uploads
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Create static/uploads directory if it doesn't exist
static_dir = Path("/app/backend/static")
uploads_dir = static_dir / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Database connection closed")
