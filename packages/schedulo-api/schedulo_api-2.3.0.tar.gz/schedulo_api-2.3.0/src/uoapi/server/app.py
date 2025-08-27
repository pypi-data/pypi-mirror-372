"""
FastAPI application for serving course data.
"""

from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from uoapi.discovery.discovery_service import (
    get_available_universities,
    get_courses_data,
    get_course_count,
    get_subjects_list,
    search_courses
)


class UniversityInfo(BaseModel):
    university: str
    total_courses: int
    total_subjects: int
    subjects: List[str]
    data_metadata: Optional[Dict[str, Any]] = None
    discovery_metadata: Optional[Dict[str, Any]] = None


class CourseData(BaseModel):
    subject: str
    code: str
    title: str
    credits: str  # Credits can be "3 units", "0.5", etc.
    description: str


class CoursesResponse(BaseModel):
    university: str
    subject_filter: Optional[str] = None
    query: Optional[str] = None
    total_courses: int
    courses_shown: int
    courses: List[CourseData]


class SubjectsResponse(BaseModel):
    university: str
    subjects: List[str]
    total_subjects: int


class HealthResponse(BaseModel):
    status: str
    available_universities: List[str]
    version: str


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Schedulo API Server",
        description="FastAPI server for accessing University of Ottawa and Carleton University course data",
        version="2.3.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint."""
        from uoapi import __version__
        return HealthResponse(
            status="healthy",
            available_universities=get_available_universities(),
            version=__version__
        )

    @app.get("/universities")
    async def get_universities():
        """Get list of available universities."""
        return {
            "universities": get_available_universities(),
            "count": len(get_available_universities())
        }

    @app.get("/universities/{university}/info", response_model=UniversityInfo)
    async def get_university_info(university: str):
        """Get comprehensive information about a university."""
        available_unis = get_available_universities()
        
        # Normalize university parameter
        normalized_uni = university.lower().replace(' ', '').replace('university', '').replace('of', '')
        
        if 'ottawa' in normalized_uni:
            target_uni = 'uottawa'
        elif 'carleton' in normalized_uni:
            target_uni = 'carleton'
        else:
            target_uni = normalized_uni
            
        if target_uni not in available_unis:
            raise HTTPException(
                status_code=404, 
                detail=f"University '{university}' not found. Available: {available_unis}"
            )
        
        try:
            data = get_courses_data(target_uni)
            course_count = get_course_count(target_uni)
            subjects = get_subjects_list(target_uni)
            
            info = UniversityInfo(
                university=target_uni,
                total_courses=course_count,
                total_subjects=len(subjects),
                subjects=sorted(subjects)
            )
            
            # Add metadata if available
            if 'metadata' in data:
                info.data_metadata = data['metadata']
            
            if 'discovery_metadata' in data:
                info.discovery_metadata = data['discovery_metadata']
                
            return info
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get university info: {str(e)}")

    @app.get("/universities/{university}/subjects", response_model=SubjectsResponse)
    async def get_university_subjects(university: str):
        """Get list of available subjects for a university."""
        available_unis = get_available_universities()
        
        # Normalize university parameter
        normalized_uni = university.lower().replace(' ', '').replace('university', '').replace('of', '')
        
        if 'ottawa' in normalized_uni:
            target_uni = 'uottawa'
        elif 'carleton' in normalized_uni:
            target_uni = 'carleton'
        else:
            target_uni = normalized_uni
            
        if target_uni not in available_unis:
            raise HTTPException(
                status_code=404,
                detail=f"University '{university}' not found. Available: {available_unis}"
            )
        
        try:
            subjects = get_subjects_list(target_uni)
            return SubjectsResponse(
                university=target_uni,
                subjects=sorted(subjects),
                total_subjects=len(subjects)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get subjects: {str(e)}")

    @app.get("/universities/{university}/courses", response_model=CoursesResponse)
    async def get_university_courses(
        university: str,
        subject: Optional[str] = Query(None, description="Filter by subject code"),
        search: Optional[str] = Query(None, description="Search in course titles and descriptions"),
        limit: int = Query(50, description="Maximum number of results to return", ge=0, le=1000)
    ):
        """Get courses for a university with optional filtering."""
        available_unis = get_available_universities()
        
        # Normalize university parameter
        normalized_uni = university.lower().replace(' ', '').replace('university', '').replace('of', '')
        
        if 'ottawa' in normalized_uni:
            target_uni = 'uottawa'
        elif 'carleton' in normalized_uni:
            target_uni = 'carleton'
        else:
            target_uni = normalized_uni
            
        if target_uni not in available_unis:
            raise HTTPException(
                status_code=404,
                detail=f"University '{university}' not found. Available: {available_unis}"
            )
        
        try:
            courses = search_courses(target_uni, subject_code=subject, query=search)
            
            # Apply limit
            if limit > 0:
                limited_courses = courses[:limit]
            else:
                limited_courses = courses
            
            # Convert to CourseData models
            course_data = []
            for course in limited_courses:
                course_data.append(CourseData(
                    subject=course["subject"],
                    code=course["code"],
                    title=course["title"],
                    credits=course["credits"],
                    description=course["description"]
                ))
            
            return CoursesResponse(
                university=target_uni,
                subject_filter=subject,
                query=search,
                total_courses=len(courses),
                courses_shown=len(limited_courses),
                courses=course_data
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get courses: {str(e)}")

    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": "Endpoint not found"}
        )

    @app.exception_handler(500)
    async def internal_error_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

    return app