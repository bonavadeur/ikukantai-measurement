#!/root/.kn-measure-venv/bin/python3

import os

# os.system("kubectl -n kourier-system patch deploy 3scale-kourier-gateway --patch \'{\"spec\":{\"replicas\":3}}\'")
# os.system("sleep 5")
# os.system("kubectl -n kourier-system patch deploy 3scale-kourier-gateway --patch \'{\"spec\":{\"template\":{\"spec\":{\"affinity\":{\"nodeAffinity\":{\"requiredDuringSchedulingIgnoredDuringExecution\":{\"nodeSelectorTerms\":[{\"matchExpressions\":[{\"key\":\"kubernetes.io/hostname\",\"operator\":\"In\",\"values\":[\"node1\",\"node2\",\"node3\"]}]}]}}}}}}}\'")
# os.system("sleep 5")

os.system("kubectl -n default patch seika hello --patch \'{\"spec\":{\"repurika\":[\"node1\":1,\"node2\":1,\"node3\":1]}}\'")
