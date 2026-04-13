from app import db, models
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAPPINGS = {
    "ITS": "Institut Teknologi Sepuluh Nopember",
    "PENS": "Politeknik Elektronika Negeri Surabaya",
    "Politeknik Elektronika Negeri Surabaya": "Politeknik Elektronika Negeri Surabaya",
    "PPNS": "Politeknik Perkapalan Negeri Surabaya",
    "UNAIR": "Universitas Airlangga",
    "UNESA": "Universitas Negeri Surabaya",
}

def merge_campuses():
    session = next(db.get_db())
    
    for alias, authoritative in MAPPINGS.items():
        if alias == authoritative:
            continue
            
        logger.info(f"Merging {alias} into {authoritative}...")
        
        # Get both campus objects
        alias_campus = session.query(models.Campus).filter_by(name=alias).first()
        auth_campus = session.query(models.Campus).filter_by(name=authoritative).first()
        
        if not alias_campus:
            logger.info(f"Alias {alias} not found. Skipping.")
            continue
            
        if not auth_campus:
            # If authoritative doesn't exist, just rename alias to authoritative
            logger.info(f"Authoritative {authoritative} not found. Renaming {alias} to {authoritative}.")
            alias_campus.name = authoritative
            session.commit()
            continue
            
        # Move all departments from alias to authoritative
        depts = session.query(models.Department).filter_by(campus_id=alias_campus.id).all()
        for dept in depts:
            # Check if dept with same name already exists in auth_campus
            existing_dept = session.query(models.Department).filter_by(campus_id=auth_campus.id, name=dept.name).first()
            if existing_dept:
                # Merge curricula from dept into existing_dept
                logger.info(f"  Merging department {dept.name} curricula...")
                curricula = session.query(models.Curriculum).filter_by(department_id=dept.id).all()
                for curr in curricula:
                    # Check if curriculum for same semester already exists
                    existing_curr = session.query(models.Curriculum).filter_by(department_id=existing_dept.id, semester=curr.semester).first()
                    if existing_curr:
                        # Move courses
                        logger.info(f"    Moving courses from {curr.semester} session...")
                        courses = session.query(models.Course).filter_by(curriculum_id=curr.id).all()
                        for course in courses:
                            course.curriculum_id = existing_curr.id
                        session.delete(curr)
                    else:
                        curr.department_id = existing_dept.id
                session.delete(dept)
            else:
                dept.campus_id = auth_campus.id
        
        # Delete the alias campus
        session.delete(alias_campus)
        session.commit()
        logger.info(f"Successfully merged {alias} into {authoritative}.")

    # Clean up weird entries like "(KKN)", "(HAM)", "Berkembang"
    WEIRD_ENTRIES = ["Berkembang", "(KKN)", "(HAM)"]
    for weird in WEIRD_ENTRIES:
        campus = session.query(models.Campus).filter_by(name=weird).first()
        if campus:
            logger.info(f"Deleting weird entry: {weird}")
            session.delete(campus)
    
    session.commit()
    logger.info("Database cleanup and normalization complete.")

if __name__ == "__main__":
    merge_campuses()
