from django.shortcuts import render

import models as solum_models
import json
import subprocess
import tempfile

def apps(req):
    apps_ = solum_models.Plan.objects.all()
    context = {'apps': apps_}
    response = render(req, 'apps.json.template', context)
    response["Access-Control-Allow-Origin"] = "*"
    return response

def app(req, app_id):
    app_ = solum_models.Plan.objects.get(uuid=app_id)
    get_app_uri = '~/get-app-uri.sh %s' % app_.uuid
    out, err = subprocess.Popen(['bash', '-c', get_app_uri],
                                stdout=subprocess.PIPE).communicate()
    app_.uri = out.strip()
    context = {
        'app': app_,
    }
    response = render(req, 'app.json.template', context)
    response["Access-Control-Allow-Origin"] = "*"
    return response

def new_app(req):
    plantext = ''
    planfile = req.FILES.get('planfile')
    if planfile is not None:
        print "Planfile from file upload."
        plantext = planfile.read()
    elif req.method == 'POST':
        planfile = req.POST.get('planfile')
        print "Planfile from form data."
        plantext = planfile
    if plantext:
        print "Plantext:"
        print plantext
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(plantext)
        tmp.close()
        new_app = '~/new-app.sh %s' % tmp.name
        out, err = subprocess.Popen(['bash', '-c', new_app],
                                    stdout=subprocess.PIPE).communicate()
        uuid = out.strip()
        return app(req, uuid)

def assemblies(req):
    assemblies = solum_models.Assembly.objects.all()
    context = {'assemblies': assemblies}
    response = render(req, 'assemblies.json.template', context)
    response["Access-Control-Allow-Origin"] = "*"
    return response

def assembly(req, assembly_id):
    context = {
        'assembly': solum_models.Assembly.objects.get(uuid=assembly_id),
    }
    response = render(req, 'assembly.json.template', context)
    response["Access-Control-Allow-Origin"] = "*"
    return response

def new_assembly(req):
    plan_uri = req.POST.get('plan_uri')
    assembly_name = req.POST.get('assembly')
    new_assembly = '~/new-assembly.sh %s %s' % (plan_uri, assembly_name)
    out, err = subprocess.Popen(['bash', '-c', new_assembly],
                                stdout=subprocess.PIPE).communicate()
    uuid = out.strip()
    return assembly(req, uuid)