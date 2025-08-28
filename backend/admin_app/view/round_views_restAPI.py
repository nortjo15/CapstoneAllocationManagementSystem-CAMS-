from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from admin_app.models import *
from django.forms.models import model_to_dict

@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def rounds_api(request, round_id=None):
    if request.method == 'GET':
        if round_id:
            try:
                round_obj = Round.objects.get(pk=round_id)
                data = model_to_dict(round_obj, exclude=['projects'])
                data['projects'] = [p.project_id for p in round_obj.projects.all()]
                return JsonResponse(data)
            except Round.DoesNotExist:
                return JsonResponse({'error': 'Round not found'}, status=404)
        
        rounds = Round.objects.all()
        rounds_list = []
        for r in rounds:
            round_data = model_to_dict(r, exclude=['projects'])
            # Include project IDs for the front end to use
            round_data['projects'] = [p.project_id for p in r.projects.all()]
            rounds_list.append(round_data)
        return JsonResponse(rounds_list, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        projects = Project.objects.filter(project_id__in=data.get('projects', []))
        

        new_round = Round(
            round_name=data.get('round_name'),
            open_date=data.get('open_date'),
            close_date=data.get('close_date'),
            status='upcoming'
        )
        new_round.save()
        new_round.projects.set(projects) # Set the ManyToMany relationship
        
        return JsonResponse(model_to_dict(new_round), status=201)

    elif request.method == 'PUT':
        if not round_id:
            return JsonResponse({'error': 'Round ID required for PUT'}, status=400)
        
        try:
            round_obj = Round.objects.get(pk=round_id)
            data = json.loads(request.body)
            
            round_obj.round_name = data.get('round_name', round_obj.round_name)
            round_obj.open_date = data.get('open_date', round_obj.open_date)
            round_obj.close_date = data.get('close_date', round_obj.close_date)
            round_obj.status = data.get('status', round_obj.status)
            round_obj.save()
            
            if 'projects' in data:
                projects = Project.objects.filter(project_id__in=data['projects'])
                round_obj.projects.set(projects)
            
            return JsonResponse(model_to_dict(round_obj))
        except Round.DoesNotExist:
            return JsonResponse({'error': 'Round not found'}, status=404)

    elif request.method == 'DELETE':
        if not round_id:
            return JsonResponse({'error': 'Round ID required for DELETE'}, status=400)
        
        try:
            round_obj = Round.objects.get(pk=round_id)
            round_obj.delete()
            return JsonResponse({'message': 'Round deleted successfully'}, status=204)
        except Round.DoesNotExist:
            return JsonResponse({'error': 'Round not found'}, status=404)