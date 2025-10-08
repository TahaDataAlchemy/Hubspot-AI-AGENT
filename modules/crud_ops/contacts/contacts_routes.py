from fastapi import APIRouter
from modules.crud_ops.contacts.routes import contacts_router
# Router for the health check
API_ROUTER = APIRouter(prefix="/api/v1/contacts", tags=["contact_crud_ops"])

# Include all routers from the health check
API_ROUTER.include_router(contacts_router)