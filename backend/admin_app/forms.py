from django import forms 
from student_app.models import Student 

class addStudentForm(forms.ModelForm):
    class Meta: 
        model = Student 
        fields = [
            'student_id', 'name', 'cwa', 'major', 'email', 'notes'
        ]
        widgets = {
            'cwa': forms.NumberInput(attrs={'step':'1', 'min':'0', 'max':'100'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # student_id & name are required fields 
        # the others can be left blank - filled in by students 
        self.fields['student_id'].required = True
        self.fields['name'].required = True
        
        for field_name in ['cwa', 'major', 'email', 'notes']:
            self.fields[field_name].required = False