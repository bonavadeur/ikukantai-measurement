mul_edge
    Gateway in AllNode
    1 Fx in Cloud, 1 Fx in Edge
    TrafficPolicy: LoadBalance

mul_edge_opt
    Gateway in All
    2 Fx in Edge
    TrafficPolicy: ServingLocal

in all case:
    req from Edge, using hey
    coreDNS has two, all in Cloud
    ignore Activator (default of Knative)
    latency = 50+-20 (ms)
    throughput from datatrace
    cus = {1, 5, 10, 15, ..., 100} (21 points)
    limitResource: 500 mCPU, 640MB RAM
    autoscaling is
        off (because if on, Fx will be create randomly, traffic will not be divide evenly into two sides)
        on
    no cold-start, 100% warm-start

NOTE:
    Both != AllNode:
        Both: one in Cloud and one in Edge
        AllNode: two in Cloud (because Cloud has two nodes), one in Edge

filename:
    detail result from hey command: result/{CASE}_{cus}.
        CASE in {
            mul_edge_autoscaling
            mul_edge_opt_autoscaling
            mul_edge_nonautoscaling
            mul_edge_opt_nonautoscaling
        }
    count number of request in mul_edge: result/count.txt
