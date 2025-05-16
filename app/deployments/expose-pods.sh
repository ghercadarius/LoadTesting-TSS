#!/bin/bash

NAMESPACE="default"
APP_LABEL="app=summary-app"
BASE_PORT=30001  
TARGET_PORT=5050 

echo "[*] Finding pods with label: $APP_LABEL in namespace: $NAMESPACE..."
PODS=$(kubectl get pods -n $NAMESPACE -l "$APP_LABEL" -o jsonpath='{.items[*].metadata.name}')

if [ -z "$PODS" ]; then
  echo "[!] No pods found with label '$APP_LABEL'."
  exit 1
fi

i=0
for POD in $PODS; do
  POD_NAME="$POD"
  NODE_PORT=$((BASE_PORT + i))
  SERVICE_NAME="${POD_NAME}-service"

  echo "[*] Exposing pod $POD_NAME as service $SERVICE_NAME on NodePort $NODE_PORT..."

  kubectl label pod "$POD_NAME" -n "$NAMESPACE" unique=pod-$i --overwrite

  cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: $SERVICE_NAME
  namespace: $NAMESPACE
spec:
  selector:
    unique: pod-$i
  type: NodePort
  ports:
    - port: $TARGET_PORT
      targetPort: $TARGET_PORT
      nodePort: $NODE_PORT
EOF

  echo "→ Pod $POD_NAME exposed at http://<node-ip>:$NODE_PORT/"
  i=$((i + 1))
done

echo "[✓] All pods have been exposed via individual NodePort services."
