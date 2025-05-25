"""Initialize sample data for tags and course-tag relationships."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session
from app.db.session import engine
from app.models.course import Tag, Course, CourseTagLink


def init_sample_tags():
    """Create sample tags and assign them to courses."""
    
    # Sample tags
    tags_data = [
        {"name": "Python", "slug": "python"},
        {"name": "JavaScript", "slug": "javascript"},
        {"name": "Web開発", "slug": "web-development"},
        {"name": "データサイエンス", "slug": "data-science"},
        {"name": "機械学習", "slug": "machine-learning"},
        {"name": "初心者向け", "slug": "beginner"},
        {"name": "中級者向け", "slug": "intermediate"},
        {"name": "上級者向け", "slug": "advanced"},
    ]
    
    with Session(engine) as session:
        # Create tags
        tags = []
        for tag_data in tags_data:
            # Check if tag already exists
            existing_tag = session.query(Tag).filter(Tag.slug == tag_data["slug"]).first()
            if not existing_tag:
                tag = Tag(**tag_data)
                session.add(tag)
                tags.append(tag)
            else:
                tags.append(existing_tag)
        
        session.commit()
        
        # Assign tags to courses
        courses = session.query(Course).all()
        
        for i, course in enumerate(courses):
            # Clear existing tags
            session.query(CourseTagLink).filter(CourseTagLink.course_id == course.id).delete()
            
            # Assign 2-3 tags per course based on index
            tag_indices = []
            if i % 3 == 0:
                tag_indices = [0, 2, 5]  # Python, Web開発, 初心者向け
            elif i % 3 == 1:
                tag_indices = [1, 2, 6]  # JavaScript, Web開発, 中級者向け
            else:
                tag_indices = [3, 4, 7]  # データサイエンス, 機械学習, 上級者向け
            
            for tag_index in tag_indices:
                if tag_index < len(tags):
                    link = CourseTagLink(course_id=course.id, tag_id=tags[tag_index].id)
                    session.add(link)
        
        session.commit()
        print(f"Created {len(tags)} tags and assigned them to {len(courses)} courses")


if __name__ == "__main__":
    init_sample_tags()