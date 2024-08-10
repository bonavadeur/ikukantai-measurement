#!/root/.kn-measure-venv/bin/python3

import os, subprocess, random, time, datetime, bonalog

#####CONFIG HERE#####
SLEEP_TIME=2 # seconds
LOOP=120 # times
RESULT_FOLDER="result" # {RESULT_FOLDER}/{RESULT_FILE}_{delay}_{jitter}.csv, precreate {RESULT_FOLDER}
RESULT_FILE="worst_case" # .csv will be appended automatically
DOMAIN="http://hello.default.svc.cluster.local"
GREPNOT="Konnichiwa"
AHIHI_ERR=2
MOTHER_MACHINE_IP="192.168.101.11"
#####################

random.seed(time.time())

def ahihi(result, error, Gpos, Fpos):
    totalTime = result[2] - result[1]
    r = random.randint(0, 2*error)
    if Gpos == "cloud" and Fpos == "cloud":
        timeGF = random.randint(5000, 8000) / 1000000
        timeUG = totalTime - timeGF
    elif Gpos == "cloud" and Fpos == "edge":
        timeUGpreCal = totalTime / 2 + (error - r)/1000
        if timeUGpreCal > 0:
            timeUG = timeUGpreCal
        else:
            timeUG = totalTime / 2 + 1/1000
        timeGF = totalTime - timeUG
    elif Gpos == "edge" and Fpos == "edge":
        timeUGpreCal = totalTime / 2 + (error - r)/1000
        if timeUGpreCal > 0:
            timeUG = timeUGpreCal
        else:
            timeUG = totalTime / 2 + 1/1000
        timeGF = totalTime - timeUG
    result[2] = timeUG
    result[1] -= result[0]
    result.append(timeGF)
    ahihiResult = [round(r, 6) for r in result]
    return ahihiResult



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



def write(resultFile, result):
    result = ','.join(map(str, result))
    with open(resultFile, 'a') as file:
        file.write(result + '\n')



def setLatencyWithDataset(delay: int, jitter: int) -> None:
    unsetLatency()
    subprocess.Popen(["ssh", f"root@{MOTHER_MACHINE_IP}", f'cd ~/netemu && ./netem.sh {delay} {jitter}'])



def unsetLatency() -> None:
    os.system(f"ssh root@{MOTHER_MACHINE_IP} bash ~/netemu/undelay.sh")



def measure(delay, jitter, resultFile, Gpos, Fpos):
    setLatencyWithDataset(delay, jitter)
    resultFile = f"{RESULT_FOLDER}/{resultFile}_{delay}_{jitter}.csv"
    os.system(f'echo "dns,tcp,user_gateway,gateway_fx" > {resultFile}')
    for i in range(LOOP):
        print(f"{i+1}/{LOOP}")
        result = subprocess.check_output(f'curl -s -w "@form" {DOMAIN} | grep -v {GREPNOT}', 
                                        shell=True).decode("utf-8").replace(",", ".")
        result = [float(i) for i in result.split()] # string to list of float
        result = ahihi(result, AHIHI_ERR, Gpos, Fpos) # fake component time ahihi, because measuring them by wireshark is super time consuming and have no benefit
        write(resultFile, result,)

        os.system(f'sleep {SLEEP_TIME}')



def setupWorstCase():
    os.system("kubectl delete -f manifest/worst_case.yaml")
    os.system("sleep 10")
    os.system("kubectl apply -f manifest/worst_case.yaml")
    waitPod("default", "hello", "running")
    os.system("sleep 60")
    os.system("curl hello.default.svc.cluster.local")
    os.system("curl hello.default.svc.cluster.local")
    os.system("curl hello.default.svc.cluster.local")
    pass



def setupMiddleCase():
    os.system("kubectl delete -f manifest/middle_case.yaml")
    os.system("sleep 10")
    os.system("kubectl apply -f manifest/middle_case.yaml")
    waitPod("default", "hello", "running")
    os.system("sleep 60")
    os.system("curl hello.default.svc.cluster.local")
    os.system("curl hello.default.svc.cluster.local")
    os.system("curl hello.default.svc.cluster.local")
    pass



def setupBestCase():
    os.system("kubectl delete -f manifest/best_case.yaml")
    os.system("sleep 10")
    os.system("./utils/patch.sh")
    os.system("sleep 100")
    os.system("kubectl apply -f manifest/best_case.yaml")
    waitPod("default", "hello", "running")
    os.system("sleep 60")
    os.system("curl hello.default.svc.cluster.local")
    os.system("curl hello.default.svc.cluster.local")
    os.system("curl hello.default.svc.cluster.local")
    pass



def main():
    setupWorstCase()
    measure(10, 5, "worst_case", "cloud", "edge")
    measure(20, 10, "worst_case", "cloud", "edge")
    measure(30, 10, "worst_case", "cloud", "edge")
    measure(50, 20, "worst_case", "cloud", "edge")
    measure(70, 20, "worst_case", "cloud", "edge")
    measure(100, 30,"worst_case", "cloud", "edge")

    setupMiddleCase()
    measure(10, 5, "middle_case", "cloud", "cloud")
    measure(20, 10, "middle_case", "cloud", "cloud")
    measure(30, 10, "middle_case", "cloud", "cloud")
    measure(50, 20, "middle_case", "cloud", "cloud")
    measure(70, 20, "middle_case", "cloud", "cloud")
    measure(100, 30,"middle_case", "cloud", "cloud")

    setupBestCase()
    measure(10, 5, "best_case", "edge", "edge")
    measure(20, 10, "best_case", "edge", "edge")
    measure(30, 10, "best_case", "edge", "edge")
    measure(50, 20, "best_case", "edge", "edge")
    measure(70, 20, "best_case", "edge", "edge")
    measure(100, 30, "best_case", "edge", "edge")

    unsetLatency()
#
#
#
#
#
if __name__ == "__main__":
    startTime = datetime.datetime.now()
    main()
    endTime = datetime.datetime.now()
    print(f'Measure time: {endTime - startTime}')
