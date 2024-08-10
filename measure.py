#!/root/.kn-measure-venv/bin/python3

from typing import List
import os, subprocess, datetime
import utils as ut
import scenarios



########## CONFIG HERE ##########
INTERVAL="60s" # e.g. 60s
WARMUP_TIME="60s" # e.g. 60s
DOMAIN="http://hello.default.svc.cluster.local" # full format, e.g. protocol + FQDN
RESULTFILE="result" # file extensions will be added in specific cases
RESULTFOLDER="alpha"
N_POINTS=-1
STEP=1
#################################


########## BONALOG ############################################################
COLOR_RED = "\e[31m"
COLOR_GREEN = "\e[32m"
COLOR_BLUE = "\e[34m"
COLOR_YELLOW = "\e[33m"
COLOR_VIOLET = "\e[35m"
COLOR_NONE = "\e[0m"
REDBGR='\033[0;41m'
NCBGR='\033[0m'
def logStage(message):
    os.system(f'echo "{COLOR_GREEN}-----{message}-----{COLOR_NONE}";')
def logNormal(message):
    os.system(f'echo "{COLOR_YELLOW}-----{message}-----{COLOR_NONE}";')
def logInfo(message):
    os.system(f'echo "{COLOR_BLUE}-----{message}-----{COLOR_NONE}";')
def logVio(message):
    os.system(f'echo "{COLOR_VIOLET}-----{message}-----{COLOR_NONE}";')
def logWarn(message):
    os.system(f'echo "{COLOR_RED}-----{message}-----{COLOR_NONE}";')
################################################################################



def initPoints() -> List[int]:
    if N_POINTS == -1:
        concurrentUsers=[STEP]
    else:
        concurrentUsers = [1]
        for x in range(1, N_POINTS + 1):
            concurrentUsers.append(x * STEP)
    return concurrentUsers



def stressTest(arch: str) -> None:
    concurrentUsers = initPoints()
    writeFile(arch+"\n")
    writeFile("[")
    for c in concurrentUsers:
        warmup(c)
        os.system("sleep 1")
        logInfo("concurrent Users = " + str(c))
        result = subprocess.check_output(f'hey -c {c} -z {INTERVAL} {DOMAIN} \
                                         | grep Average \
                                         | cut -d: -f2 \
                                         | tr -d "\t" \
                                         | cut -d" " -f1', shell=True
                            ).decode("utf-8")
        try:
            result = str(round(float(result) * 1000, 1))
        except:
            print(result)
        writeFile(result + ",\t")
        ut.waitPod("default", "hello", "terminating")
    writeFile("]")
    writeFile("\n")



def stressTestAndRecord(arch: str) -> None:
    concurrentUsers = initPoints()
    for cu in concurrentUsers:
        warmup(cu)
        os.system("sleep 1")
        logInfo("concurrent Users = " + str(cu))
        os.system(f"hey -c {cu} -z {INTERVAL} -o csv {DOMAIN} > result/{RESULTFOLDER}/{arch}_{cu}.csv")
        ut.waitPod("default", "hello", "terminating")



def warmup(concurrentUser: int):
    logInfo("Warmup start")
    result = subprocess.call(f'hey -c {concurrentUser} -z {WARMUP_TIME} {DOMAIN}',
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL,
                                 shell=True)
    logInfo("Warmup done")



def writeFile(record):
    f = open("result/" + RESULTFILE + ".txt", "a")
    f.write(record)
    f.close()





def main_test():
    ut.setLatencyWithDataset(50, 30)
    os.system("sleep 10")
    ut.unsetLatency()



def main():
    open("result/" + RESULTFILE + ".txt", 'w').close() # clean output file
    # os.system(f"cd result && rm -rf {RESULTFOLDER} && mkdir {RESULTFOLDER}")

    # # KSCs on Cloud, Function on Edge
    # logWarn("Vanilla_Edge")
    # scenarios.VanillaEdge()
    # ut.setLatencyWithDataset(50, 20)
    # stressTestAndRecord("vanilla_edge")

    # # KSCs on Cloud, Function on Cloud
    # logWarn("Vanilla_Cloud")
    # scenarios.VanillaCloud()
    # ut.setLatencyWithDataset(50, 20)
    # stressTestAndRecord("vanilla_cloud")

    # # KSCs on Cloud, Function on All Side
    # logWarn("Vanilla")
    # scenarios.Vanilla()
    # ut.setLatencyWithDataset(50, 20)
    # stressTestAndRecord("vanilla")

    # # Serving traffic in the same Region
    # logWarn("Proposal")
    # scenarios.Proposal("release-v1")
    # ut.setLatencyWithDataset(50, 20)
    # stressTestAndRecord("proposal")




    logWarn("Vanilla - Traffic from Edge - KSCs on the same side")
    scenarios.VanillaAllOnEdge()
    ut.setLatencyWithDataset(50, 20)
    stressTestAndRecord("VanillaEdgeEdge")

    logWarn("Vanilla - Traffic from Edge - KSCs on the diff side")
    scenarios.VanillaAllOnCloud()
    ut.setLatencyWithDataset(50, 20)
    stressTestAndRecord("VanillaEdgeCloud")



    # logWarn("Vanilla")
    # scenarios.Vanilla()
    # ut.setLatencyWithDataset(50, 20)
    # stressTest("vanilla")

    # logWarn("Proposal")
    # scenarios.Proposal("release-v1")
    # ut.setLatencyWithDataset(50, 20)
    # stressTest("proposal")
#
#
#
#
#
if __name__ == "__main__":
    os.system(f'clear && echo "{REDBGR} このスクリプトはボナちゃんによって書かれています {NCBGR}"')
    startTime = datetime.datetime.now()
    main()
    endTime = datetime.datetime.now()
    print(f'Measure time: {endTime - startTime}')
    # main_test()
