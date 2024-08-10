#!/root/.kn-measure-venv/bin/python3

from typing import List
import os, subprocess, datetime
import bonalog



########## CONFIG HERE ##########
INTERVAL="60s" # e.g. 60s
WARMUP_TIME="10s" # e.g. 60s
DOMAIN="http://hello.default.svc.cluster.local" # full format, e.g. protocol + FQDN
RESULTFOLDER="result/24_07_01_23h_mon"
N_POINTS=-1
STEP=35
MOTHER_MACHINE_IP="192.168.101.11"
HOSTNAME="node3"
#################################



def setLatencyWithDataset(delay: int, jitter: int) -> None:
    unsetLatency()
    subprocess.Popen(["ssh", f"root@{MOTHER_MACHINE_IP}", f'cd ~/netemu && ./netem.sh {delay} {jitter}'])



def unsetLatency() -> None:
    os.system(f"ssh root@{MOTHER_MACHINE_IP} bash ~/netemu/undelay.sh")



def initPoints() -> List[int]:
    if N_POINTS == -1:
        concurrentUsers=[STEP]
    else:
        concurrentUsers = [1]
        for x in range(1, N_POINTS + 1):
            concurrentUsers.append(x * STEP)
    return concurrentUsers



def waitPod(namespace: str, grepName: str, desiredStatus: str) -> None: # desiredStatus = ["running", "terminating"]
    _TIME_SLEEP_INTERVAL = 5
    os.system(f"sleep {_TIME_SLEEP_INTERVAL}")
    if desiredStatus == "running":
        bonalog.logNormal(f"Waiting for Running Pods: {grepName}")
        while True:
            nTotalPods = int(subprocess.check_output(f"kubectl get pod -n {namespace} | grep {grepName} | wc -l", shell=True).decode("utf-8"))
            nRunningPods = int(subprocess.check_output(f"kubectl get pod -n {namespace} | grep {grepName} | grep Running | wc -l", shell=True).decode("utf-8"))
            if nRunningPods == nTotalPods:
                break
            else:
                os.system(f"sleep {_TIME_SLEEP_INTERVAL}")
    if desiredStatus == "terminating":
        bonalog.logNormal(f"Waiting for Terminating Pods: {grepName}")
        while True:
            nTotalPods = int(subprocess.check_output(f"kubectl get pod -n {namespace} | grep {grepName} | wc -l", shell=True).decode("utf-8"))
            if nTotalPods == 0:
                break
            else:
                os.system(f"sleep {_TIME_SLEEP_INTERVAL}")



def stressTestAndRecord(scenario: str) -> None:
    concurrentUsers = initPoints()
    for cu in concurrentUsers:
        warmup(cu)
        # warmup(1)
        os.system("sleep 1")
        bonalog.logInfo(f"concurrent Users = {cu}")
        os.system(f"hey -c {cu} -z {INTERVAL} -o csv {DOMAIN} > {RESULTFOLDER}/{HOSTNAME}_{scenario}_{cu}.csv")
        os.system("sleep 2")
        # waitPod("default", "hello", "terminating")



def warmup(concurrentUser: int):
    bonalog.logInfo("Warmup start")
    result = subprocess.call(f'hey -c {concurrentUser} -z {WARMUP_TIME} {DOMAIN}',
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL,
                                 shell=True)
    bonalog.logInfo("Warmup done")
    



def measure(scenario: str) -> None:
    bonalog.logWarn(scenario)
    # os.system(f"kubectl delete -f manifest/{scenario}.yaml")
    # waitPod("default", "hello", "terminating")
    # os.system(f"kubectl apply -f manifest/{scenario}.yaml")
    # waitPod("default", "hello", "running")
    # setLatencyWithDataset(50, 20)
    stressTestAndRecord(scenario)
    # os.system("sleep 60")



def main():
    measure("mul_edge_au")
    measure("mul_edge_nonau")
    os.system("./utils/patch.sh")
    os.system("sleep 100")
    measure("mul_edge_opt_au")
    measure("mul_edge_opt_nonau")

    measure("vanilla")

    # unsetLatency()
#
#
#
#
#
if __name__ == "__main__":
    os.system(f'clear && echo "{bonalog.REDBGR} このスクリプトはボナちゃんによって書かれています {bonalog.NCBGR}"')
    startTime = datetime.datetime.now()
    main()
    endTime = datetime.datetime.now()
    print(f'Measure time: {endTime - startTime}')
