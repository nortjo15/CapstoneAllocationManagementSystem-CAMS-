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
            help='Path to CSV file to import',
            default=os.path.join(settings.BASE_DIR, 'project_app', 'fixtures', 'test_students.csv')
        )


    def handle(self, *args, **options):
        file_path = options['path']

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return 
        
        with open(file_path, newline='', encoding='utf-8') as csvfile: 
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