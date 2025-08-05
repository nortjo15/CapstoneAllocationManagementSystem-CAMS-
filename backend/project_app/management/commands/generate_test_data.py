import csv 
import os 
from django.conf import settings
from django.core.management.base import BaseCommand
from student_app.models import Student, GroupPreference 
from project_app.models import (
    Project,
    ProjectPreference, 
    SuggestedGroup, 
    SuggestedGroupMember,
    FinalGroup,
    FinalGroupMember
)

# Generate test data from specified or default file 
# - Stored in project_app/fixtues 
class Command(BaseCommand):
    help = "Generate test data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Path to CSV file to import student data',
            default=os.path.join(settings.BASE_DIR, 'project_app', 'fixtures', 'test_students.csv')
        )
        parser.add_argument(
            '--project-path',
            type=str, 
            help='Path to CSV file to import project data',
            default=os.path.join(settings.BASE_DIR, 'project_app', 'fixtures', 'test_projects.csv')
        )

    def handle(self, *args, **options):
        student_file = options['path']
        project_file = options['project_path']

        # --- Import Students --- 
        if not os.path.exists(student_file):
            self.stdout.write(self.style.ERROR(f"File not found: {student_file}"))
            return 
        
        with open(student_file, newline='', encoding='utf-8') as csvfile: 
            reader = csv.DictReader(csvfile)
            count = 0

            for row in reader: 
                student_id = row['student_id']
                name = row['name']
                cwa = row['cwa']
                major = row['major']

                student, created = Student.objects.update_or_create(
                    student_id=student_id,
                    defaults={
                        'name': name,
                        'cwa': cwa if cwa else None, 
                        'major': major, 
                        'application_submitted': False
                    }
                )
                if created: 
                    count += 1 

            self.stdout.write(self.style.SUCCESS(f"Successfully imported or updated {count} students."))

        # --- Import Projects --- 
        if not os.path.exists(project_file):
            self.stdout.write(self.style.ERROR(f"Project file not found: {project_file}"))
        else: 
            with open(project_file, newline='', encoding='utf-8') as csvfile: 
                reader = csv.DictReader(csvfile)
                count = 0

                for row in reader: 
                    title = row['title']
                    capacity = int(row['capacity'])
                    host_name = row['host_name']
                    host_email = row['host_email']
                    host_phone = row['host_phone']

                    project = Project.objects.update_or_create(
                        title=title,
                        capacity=capacity, 
                        host_name=host_name, 
                        host_email=host_email,
                        host_phone=host_phone
                    )
                    count += 1 

                self.stdout.write(self.style.SUCCESS(f"Successfully created {count} projects."))
