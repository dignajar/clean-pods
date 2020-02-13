import requests
import json
import os
from datetime import timedelta, datetime

# --- Variables ---------------------------------------------------------------
# Get the token for authenticate via the API
if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount"):
    token = open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r").read().replace('\n', '')
else:
    token = os.environ["TOKEN"]

# API URL. Ex. https://kubernetes.default.svc/api/
apiURL = os.environ["API_URL"]

# Namespace where the pods are running
namespace = os.environ["NAMESPACE"]

# Expiration time in days, the pods older than "maxDays" are going to be deleted
maxDays = int(os.environ["MAX_DAYS"])

# Only pods with the following status are going to be deleted
# You can send a list of string separate by comma, Ex. "Pending, Running, Succeeded, Failed, Unknown"
podStatus = os.environ["POD_STATUS"].replace(' ','').split(",")

# --- Functions ---------------------------------------------------------------
def callAPI(url):
    headers = {"Authorization": "Bearer "+token}
    requests.packages.urllib3.disable_warnings()
    request = requests.get(url, headers=headers, verify=False)
    return request.json()

def getPods(namespace):
    url = apiURL+"v1/namespaces/"+namespace+"/pods"
    response = callAPI(url)
    return response["items"]

def deletePod(podName, namespace):
    url = apiURL+"v1/namespaces/"+namespace+"/pods/"+podName
    response = callAPI(url)
    return response

# --- Main --------------------------------------------------------------------
# Get all pods running in a namespace and delete older than "maxDays"
pods = getPods(namespace)
for pod in pods:
    if pod["status"]["phase"] in podStatus:
        podStartTime = datetime.strptime(pod["status"]["startTime"], "%Y-%m-%dT%H:%M:%SZ")
        todayDate = datetime.today()
        if ((podStartTime + timedelta(days=maxDays)) < todayDate):
            print("Deleting pod ("+pod["metadata"]["name"]+"). Status ("+pod["status"]["phase"]+"). Start time ("+str(podStartTime)+")")
            #deletePod(pod["metadata"]["name"], namespace)

