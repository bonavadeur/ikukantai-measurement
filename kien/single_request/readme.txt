worst_case(sig_edge):
    Gateway in Cloud, Fx in Edge    

middle_case(sig_default):
    Gateway in Cloud, Fx in Cloud

best_case:
    Gateway in Edge, Fx in Edge

in all case:
    req from Edge, every 2s
    coreDNS has two, all in Cloud
    ignore Activator (default of Knative)
    latency = 10+-5, 20+-10, 30+-10, 50+-20, 70+-20, 100+-30 (ms)
    throughput from datatrace

filename: result/{CASE}_{delay}_{jitter}.csv
