import json

SECRETFILE = "secrets_example.json"

with open(SECRETFILE) as f:
    secrets = json.loads(f.read())

def get_secret(setting,secrets = secrets):
    try:
        return secrets[setting]
    except Exception as e:
        return ""


USERNAME = get_secret("USERNAME")
PASSWORD = get_secret("PASSWORD")

LMSURL = "https://courses.edx.org/"
CMSURL = "https://studio.edx.org/"
COURSELOCATOR = "course-v1:UPValenciaX+BSP102x+2T2017"
FILENAME = 'glosario.html'
