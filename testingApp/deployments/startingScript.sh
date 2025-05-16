#!/bin/bash

echo "Deploying the testing application pods"

helm install backend-deployment helmCharts --set replicaCount=3

echo "Waiting for pods to be ready..."



START_PORT=5005
NAMESPACE="default"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Script directory: $SCRIPT_DIR"

PODS=$(kubectl get pods -o jsonpath='{.items[*].metadata.name}')

if [ -z "$PODS" ]; then
  echo "No pods found"
  exit 1
fi

echo "Waiting for pods to be ready"

while true; do
  ALL_HEALTHY=1
    for POD in $PODS; do
        STATUS=$(kubectl get pod $POD -o jsonpath='{.status.phase}')
        if [ "$STATUS" != "Running" ]; then
            echo "Pod $POD is not running yet."
            ALL_HEALTHY=0
        else
            echo "Pod $POD is running."
        fi
    done
   if [ $ALL_HEALTHY -eq 1 ]; then
    echo "All pods are ready."
    break
  else
    echo "Not all pods are ready, retrying in 2 seconds..."
    sleep 2
  fi 
done

echo "Starting port-forwards..."
i=0
for POD in $PODS; do
  LOCAL_PORT=$((START_PORT + i))
  echo "Forwarding $POD to localhost:$LOCAL_PORT"
  
  kubectl port-forward -n "$NAMESPACE" pod/"$POD" "$LOCAL_PORT":5005 > /dev/null 2>&1 &
  
  echo "Access with: curl http://localhost:$LOCAL_PORT/"
  i=$((i + 1))
done

echo "Done. All port-forwards are running in the background."
echo "Uploading the test file to all the pods..."

echo "Waiting for pods to be healthy..."
while true; do
  ALL_HEALTHY=1
  i=0
  for POD in $PODS; do
    LOCAL_PORT=$((START_PORT + i))
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$LOCAL_PORT/health-check)
    if [ "$HTTP_CODE" != "200" ]; then
      echo "Pod $POD on port $LOCAL_PORT is not healthy (HTTP: $HTTP_CODE)."
      ALL_HEALTHY=0
    else
      echo "Pod $POD on port $LOCAL_PORT is healthy (HTTP: $HTTP_CODE)."
    fi
    i=$((i + 1))
  done

  if [ $ALL_HEALTHY -eq 1 ]; then
    echo "All pods are healthy."
    break
  else
    echo "Not all pods are healthy, retrying in 2 seconds..."
    sleep 2
  fi
done

JMX_PATH="$SCRIPT_DIR/../../testingFiles/PythonServerSimulatingUsers.jmx"

i=0
for POD in $PODS; do
  LOCAL_PORT=$((START_PORT + i))
  echo "starting upload to $POD on localhost:$LOCAL_PORT"
  
  curl -X POST http://localhost:$LOCAL_PORT/upload_test -F "file=@${JMX_PATH}"
  echo "Upload complete for localhost:$LOCAL_PORT"
  i=$((i + 1))
done

echo "All uploads complete."
echo "Starting tests..."
i=0
for POD in $PODS; do
  LOCAL_PORT=$((START_PORT + i))
  echo "starting test on localhost:$LOCAL_PORT"
  
  curl -X POST http://localhost:$LOCAL_PORT/run &
  echo "Test started on localhost:$LOCAL_PORT"
  i=$((i + 1))
done
echo "All tests started."