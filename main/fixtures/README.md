# Fixtures Documentation

## Overview
This directory contains sample data fixtures for the CV Project application.

## Fixture Files

### `initial_data.json`
Main fixture containing a complete CV with all related data:
- 1 CV (John Doe)
- 5 Skills (Python, Django, React, Team Leadership, English)
- 3 Projects (E-commerce Platform, Task Management System, AI Chatbot Integration)
- 5 Contacts (email, phone, LinkedIn, GitHub, website)

### `initial_cv_data.json`
Additional CV records:
- 3 CVs total (John Doe, Jane Smith, Alex Johnson)

### `initial_skills_data.json`
Skills data for all CVs:
- 10 skills across different categories (technical, soft, language)

### `initial_projects_data.json`
Projects data for all CVs:
- 7 projects with different statuses (completed, in_progress)

### `initial_contacts_data.json`
Contact information for all CVs:
- 13 contacts of different types (email, phone, LinkedIn, GitHub, website)

## Loading Fixtures

### Method 1: Individual Fixtures
```bash
python manage.py loaddata main/fixtures/initial_data.json
python manage.py loaddata main/fixtures/initial_cv_data.json
python manage.py loaddata main/fixtures/initial_skills_data.json
python manage.py loaddata main/fixtures/initial_projects_data.json
python manage.py loaddata main/fixtures/initial_contacts_data.json
```

### Method 2: Custom Management Command
```bash
# Load all fixtures
python manage.py load_sample_data

# Clear existing data and load all fixtures
python manage.py load_sample_data --clear
```

### Method 3: Django Admin
1. Go to Django Admin panel
2. Navigate to each model (CV, Skill, Project, Contact)
3. Use the "Load data" functionality if available

## Data Structure

### CV Model
- **John Doe**: Published CV with full profile
- **Jane Smith**: Published CV with frontend focus
- **Alex Johnson**: Draft CV with DevOps focus

### Skills Categories
- **Technical**: Python, Django, React, JavaScript, Node.js, AWS, Docker, Kubernetes
- **Soft**: Team Leadership
- **Language**: English

### Project Statuses
- **Completed**: E-commerce Platform, Task Management System, Social Media Dashboard, Mobile App Backend, Cloud Infrastructure Migration
- **In Progress**: AI Chatbot Integration, CI/CD Pipeline Automation

### Contact Types
- **Email**: Primary email addresses
- **Phone**: Phone numbers
- **LinkedIn**: Professional profiles
- **GitHub**: Code repositories
- **Website**: Personal/professional websites

## Notes
- All fixtures use realistic sample data
- Foreign key relationships are properly maintained
- Timestamps are set to realistic dates
- Data follows the model constraints and validations
