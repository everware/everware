import nose2

import sys
import os

import normal_scenarios
import nonstop_scenarios
import commons
from settings import *

# Test matrix
SCENARIOS = [
    normal_scenarios.scenario_timeout,
    normal_scenarios.scenario_full,
    normal_scenarios.scenario_short,
    normal_scenarios.scenario_no_jupyter,
    normal_scenarios.scenario_no_dockerfile,
    normal_scenarios.scenario_default_dockerfile, # should go after no_dockerfile
    normal_scenarios.scenario_default_private_repos,
    nonstop_scenarios.scenario_simple
]

USERS = ["user1", "user2"]

def make_screenshot(driver, name):
    os.makedirs(UPLOADDIR, exist_ok=True)
    driver.save_screenshot(os.path.join(UPLOADDIR, name))


def test_generator():
    module_name = '%s_scenarios' % os.environ['EVERWARE_MODULE']
    method_name = os.environ['EVERWARE_SCENARIO']
    scenario = getattr(sys.modules[module_name], method_name)

    if scenario == normal_scenarios.scenario_default_private_repos:
        return run_scenario("everware-test", scenario)

    for username in USERS:
        yield run_scenario, username, scenario


def run_scenario(username, scenario):
    user = commons.User(username)
    try:
        scenario(user)
    except Exception as e:
        print(user.get_driver().get_log('browser'), file=sys.stderr)
        make_screenshot(user.driver, "{}-{}.png".format(username, scenario.__name__))
        raise
    finally:
        user.tearDown()

if __name__ == '__main__':
    run_type = sys.argv[1]
    print(' '.join(
        cur.__name__
        for cur in SCENARIOS
        if cur.__module__ == '%s_scenarios' % run_type
    ))
