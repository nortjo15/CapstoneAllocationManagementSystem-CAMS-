import csv 
import datetime
import os 
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from student_app.models import Student, GroupPreference 
from admin_app.models import (
    Project,
    ProjectPreference, 
    SuggestedGroup, 
    SuggestedGroupMember,
    FinalGroup,
    FinalGroupMember,
    Major,
    Degree,
    Round,
)

# Generate test data from specified or default files
# - Stored in admin_app/fixtues 
class Command(BaseCommand):
    help = "Generate test data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Path to CSV file to import student data',
            default=os.path.join(settings.BASE_DIR, 'admin_app', 'fixtures', 'test_students.csv')
        )
        parser.add_argument(
            '--project-path',
            type=str, 
            help='Path to CSV file to import project data',
            default=os.path.join(settings.BASE_DIR, 'admin_app', 'fixtures', 'test_projects.csv')
        )
        parser.add_argument(
            '--memberpref-path',
            type=str, 
            help='Path to CSV file to import member preference data',
            default=os.path.join(settings.BASE_DIR, 'admin_app', 'fixtures', 'test_group_pref.csv')
        )
        parser.add_argument(
            '--projectpref-path',
            type=str, 
            help='Path to CSV file to import project preference data',
            default=os.path.join(settings.BASE_DIR, 'admin_app', 'fixtures', 'test_project_pref.csv')
        )
        parser.add_argument(
            '--round-path',
            type=str,
            help='Path to CSV file to import round data',
            default=os.path.join(settings.BASE_DIR, 'admin_app', 'fixtures', 'test_rounds.csv')
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Clear tables' 
        )


    def handle(self, *args, **options):
        student_file = options['path']
        project_file = options['project_path']
        member_pref_file = options['memberpref_path']
        project_pref_file = options['projectpref_path']
        round_file = options['round_path']

        # --- Reset Flag Enabled --- 
        if options['reset']:
            self.stdout.write("Resetting database tables...")
            ProjectPreference.objects.all().delete()
            GroupPreference.objects.all().delete()
            Project.objects.all().delete()
            Student.objects.all().delete()
            Round.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Database tables cleared."))
            return 
        
        # Add Degrees & Majors, hard coded test data
        degrees_and_majors = {
            "Computing": [
                "Cybersecurity", 
                "Information Technology", 
                "Computer Science", 
                "Software Engineering"
            ],
            "Arts": [
                "Visual",
                "Creative",
                "Digital"
            ],
        }

        self.stdout.write("Adding Degrees and Majors...")

        for degree_name, majors_list in degrees_and_majors.items():
            degree_obj, created = Degree.objects.get_or_create(name=degree_name)
            if created: 
                self.stdout.write(f"Created Degree: {degree_name}")

            for major_name in majors_list:
                major_obj, created = Major.objects.get_or_create(degree=degree_obj, name=major_name)
                if created:
                    self.stdout.write(f"  Created Major: {major_name} under Degree: {degree_name}")

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

                try:
                    major_instance = Major.objects.get(name=major)
                except Major.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Major '{major}' not found, skipping student {student_id}"))
                    continue 

                student, created = Student.objects.update_or_create(
                    student_id=student_id,
                    defaults={
                        'name': name,
                        'cwa': cwa if cwa else None, 
                        'major': major_instance, 
                        'application_submitted': False,
                    }
                )
                if created: 
                    count += 1 

            self.stdout.write(self.style.SUCCESS(f"Successfully imported or updated {count} students."))

        # --- Import Projects --- 
        if not os.path.exists(project_file):
            self.stdout.write(self.style.ERROR(f"Project file not found: {project_file}"))
            return 
        
        with open(project_file, newline='', encoding='utf-8') as csvfile: 
            reader = csv.DictReader(csvfile)
            count = 0

            for row in reader: 
                title = row['title']
                capacity = int(row['capacity'])
                host_name = row['host_name']
                host_email = row['host_email']
                host_phone = row['host_phone']

                project, created = Project.objects.update_or_create(
                    title=title,
                    capacity=capacity, 
                    host_name=host_name, 
                    host_email=host_email,
                    host_phone=host_phone
                )
                if created: 
                    count += 1 

            self.stdout.write(self.style.SUCCESS(f"Successfully created {count} projects."))

        # -- Import Member Preferences --
        if not os.path.exists(member_pref_file):
            self.stdout.write(self.style.ERROR(f"Member preference file not found: {member_pref_file}"))
            return 
        
        students = {s.student_id: s for s in Student.objects.all()}

        with open(member_pref_file, newline='', encoding='utf-8') as csvfile: 
            reader = csv.DictReader(csvfile)
            count = 0

            # Deleting all existing preferences due to FK constraints 
            GroupPreference.objects.all().delete()

            for row in reader: 
                student_id = row['student_id']
                target_student_id = row['target_student_id']
                preference_type = row['preference_type']

                # Get the actual student reference from the model, not string
                student = students.get(student_id)
                target_student = students.get(target_student_id)

                # Skip student if they don't exist
                if not student or not target_student:
                    self.stdout.write(self.style.WARNING(
                        f"Skipping preference with missing student: {student_id}, {target_student_id}"
                    ))
                    continue

                member_pref, created = GroupPreference.objects.update_or_create(
                    student=student, 
                    target_student=target_student, 
                    preference_type=preference_type
                )
                if created: 
                    count += 1
                
            self.stdout.write(self.style.SUCCESS(f"Successfully added or updated {count} member preferences."))

        # Import Project Preferences
        if not os.path.exists(project_pref_file):
            self.stdout.write(self.style.ERROR(f"Project preference file not found: {project_pref_file}"))
            return 

        with open(project_pref_file, newline='', encoding='utf-8') as csvfile: 
            reader = csv.DictReader(csvfile)
            count = 0

            for row in reader:
                student_id = row['student_id']
                project_name = row['projectName']
                rank = int(row['rank'])

                try: 
                    student = Student.objects.get(student_id=student_id)
                except Student.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Stuent {student_id} not found. Skipping"))
                    continue 

                try: 
                    project = Project.objects.get(title=project_name)
                except Project.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Project '{project_name} not found. Skipping"))
                    continue 

                pref, created = ProjectPreference.objects.update_or_create(
                    student=student, 
                    rank=rank, 
                    defaults={'project':project},
                )
                if created: 
                    count += 1

        # --- Import Rounds ---
        # Matt HK: This is from Gemini with little refactoring
        # Ill test and make sure it works
        if not os.path.exists(round_file):
            self.stdout.write(self.style.ERROR(f"Round file not found: {round_file}"))
            return

        with open(round_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0

            for row in reader:
                round_name = row['round_name']
                open_date_str = row['open_date']
                close_date_str = row['close_date']
                projects_titles = row['projects'].split(';')
                is_internal = row['is_internal']

                # Convert string dates to timezone-aware datetime objects
                try:
                    naive_open_date = datetime.datetime.fromisoformat(open_date_str)
                    naive_close_date = datetime.datetime.fromisoformat(close_date_str)
                    open_date = timezone.make_aware(naive_open_date, timezone.get_current_timezone())
                    close_date = timezone.make_aware(naive_close_date, timezone.get_current_timezone())
                    # open_date = open_date_str
                    # close_date = close_date_str
                except ValueError:
                    self.stdout.write(self.style.ERROR(
                        f"Invalid date format for round on row {reader.line_num}. Skipping."
                    ))
                    continue

                # Create the Round instance
                current_round, created = Round.objects.update_or_create(
                    round_name =round_name,
                    open_date=open_date,
                    close_date=close_date,
                    is_internal=is_internal,
                    defaults={'status': 'upcoming', 'is_active': False}
                )

                # Retrieve project objects and link them to the round
                projects_to_add = []
                for title in projects_titles:
                    title = title.strip() # Remove any leading/trailing whitespace
                    if title:
                        try:
                            project = Project.objects.get(title=title)
                            projects_to_add.append(project)
                        except Project.DoesNotExist:
                            self.stdout.write(self.style.WARNING(
                                f"Project '{title}' not found. It will not be added to the round."
                            ))
                
                # Use the add() method on the ManyToManyField to link the projects
                # This is done after the Round object is saved (created or updated)
                if projects_to_add:
                    current_round.projects.add(*projects_to_add)
                
                if created:
                    count += 1

            self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} project preferences."))