#!/bin/bash

gateways=($(kubectl -n kourier-system get pod -o wide | grep 3scale | grep Running | awk '{print $8}'))
activators=($(kubectl -n knative-serving get pod -o wide | grep activator | grep Running | awk '{print $8}'))

echo "http && (ip.src==${gateways[0]} || ip.src==${gateways[1]} || ip.src==${gateways[2]}) && (ip.dst==${activators[0]} || ip.dst==${activators[1]} || ip.dst==${activators[2]})"
