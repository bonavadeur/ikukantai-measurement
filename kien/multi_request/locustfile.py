#!/root/.kn-measure-venv/bin/python3

from locust import HttpUser, TaskSet, task, between, events
import time
from locust.env import Environment
from locust.log import setup_logging
from locust.runners import LocalRunner
import gevent
import os

class UserBehavior(TaskSet):
    @task
    def hello_world(self):
        with self.client.get("/sleep/1000", catch_response=True) as response:
            response_time = int(response.elapsed.total_seconds() * 1000)
            response_body = response.text.strip()
            log_line = f"{response_time} {response_body}\n"
            with open("llog.txt", "a") as log_file:
                log_file.write(log_line)

class WebsiteUser(HttpUser):
    host = "http://hello.default.svc.cluster.local"
    tasks = [UserBehavior]
    wait_time = between(1, 1)



# Event hook to set up the logging before the test starts
@events.init.add_listener
def on_locust_init(environment, **kwargs):
    with open("llog.txt", "w") as log_file:
        log_file.write("")



if __name__ == "__main__":
    setup_logging("INFO", None)
    
    env = Environment(user_classes=[WebsiteUser])
    env.create_local_runner()

    env.events.init.fire(environment=env)

    runner = env.runner

    user_count = 3
    max_users = 50  # Adjust as needed
    spawn_rate = 0.5
    step_time = 1

    # runner.start(user_count=1, spawn_rate=0.5)
    # gevent.sleep(step_time)
    # user_count += 5
    # runner.quit()

    os.system("echo > llog.txt")

    print(f"Spawning {user_count} users")
    runner.start(user_count, spawn_rate=user_count)
    gevent.sleep(step_time)
    runner.quit()
    os.system("sleep 1")
    os.system("clear")

    # while user_count <= max_users:
    #     print(f"Spawning {user_count} users")
    #     os.system("echo > llog.txt")
    #     runner.start(user_count, spawn_rate=30)
    #     gevent.sleep(step_time)
    #     runner.quit()
    #     os.system(f"mv llog.txt result/24_07_09_13h_tue/node3_proposal_{user_count}.txt")
    #     user_count += 40
    #     os.system("sleep 20")

    env.events.quitting.fire(environment=env, reverse=True)
