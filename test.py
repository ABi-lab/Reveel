#! /usr/bin/python

""" Test client for node-challenge server. """

__author__ = "Rok Ajdnik"
__copyright__ = "Copyright 2015 Reveel Technologies and contributors"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "rok@reveelapp.io"

import argparse
import dateutil.parser
import json
import requests
import sys
import urlparse

# Terminal colors
TERMINAL_HEADER = "\033[95m"
TERMINAL_TEST_SUCCEEDED = "\033[92m"
TERMINAL_TEST_FAIL = "\033[91m"
TERMINAL_INFO = "\033[95m"
TERMINAL_ERROR = "\033[91m"
TERMINAL_ENDC = "\033[0m"
TERMINAL_BOLD = "\033[1m"
TERMINAL_UNDERLINE = "\033[4m"

def print_header(text):
    """
    Print test header.
    """
    print "------------------------------------------------------------------"
    print TERMINAL_HEADER + TERMINAL_BOLD + text + TERMINAL_ENDC
    print "------------------------------------------------------------------"

def print_fail(reason):
    """
    Print fail status with reason for failure.
    """
    print "Status: " + TERMINAL_TEST_FAIL + "Fail" + TERMINAL_ENDC
    print "Reason: " + reason

def print_success():
    """
    Print success status.
    """
    print "Status: " + TERMINAL_TEST_SUCCEEDED + "Success" + TERMINAL_ENDC

def print_info(text):
    """
    Prints text with info prefix.
    """
    print TERMINAL_INFO + "[" + TERMINAL_UNDERLINE + \
        "INFO" + TERMINAL_ENDC + TERMINAL_INFO + "]" + \
        TERMINAL_ENDC + " " + text

def print_error(text):
    """
    Prints text with error prefix.
    """
    print TERMINAL_ERROR + "[" + TERMINAL_UNDERLINE + \
        "ERROR" + TERMINAL_ENDC + TERMINAL_ERROR + "]" + \
        TERMINAL_ENDC + " " + text

def print_test_summary(failed, succeeded):
    """
    Print test summary.
    """
    print "------------------------------------------------------------------"
    print TERMINAL_BOLD + TERMINAL_TEST_FAIL + "Failed: " + str(failed) + \
        TERMINAL_TEST_SUCCEEDED + " Succeeded: " + str(succeeded) + \
        TERMINAL_ENDC
    print "------------------------------------------------------------------"

def run_request(base_url, url, method="GET", data=None, verbose=False):
    """
    Run HTTP request and return the result.
    """
    if method not in ("GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH", \
        "DELETE"):
        if verbose:
            print_error("Unknown method")
        return None
    full_url = urlparse.urljoin(base_url, url)
    if verbose:
        print_info("Request url=%s" % (full_url))
        print_info("Request method=%s" % (method))
        if data is not None:
            print_info("Request body=%s" % (data))
    try:
        response = None
        if method == "DELETE":
            response = requests.delete(full_url, data=data)
        elif method == "HEAD":
            response = requests.head(full_url, data=data)
        elif method == "OPTIONS":
            response = requests.options(full_url, data=data)
        elif method == "POST":
            response = requests.post(full_url, data=data)
        elif method == "PUT":
            response = requests.put(full_url, data=data)
        elif method == "PATCH":
            response = requests.patch(full_url, data=data)
        else:
            response = requests.get(full_url, data=data)
        if verbose:
            print_info("Response code=%d" % (response.status_code))
            print_info("Response body=%s" % (response.content))
            print_info("Response headers=%s" % (response.headers))
        return response
    except requests.exceptions.ConnectionError:
        if verbose:
            print_error("Network problem occurred")
        return None
    except requests.exceptions.HTTPError:
        if verbose:
            print_error("Invalid HTTP response")
        return None
    except requests.exceptions.URLRequired:
        if verbose:
            print_error("Invalid request URL")
        return None
    except requests.exceptions.TooManyRedirects:
        if verbose:
            print_error("Too many redirects")
        return None
    except requests.exceptions.Timeout:
        if verbose:
            print_error("Connection timed out")
        return None
    except requests.exceptions.MissingSchema:
        if verbose:
            print_error("Invalid request URL")
        return None

def verify_allow(value, expected):
    """
    Verify Allow header methods.
    """
    if value is None:
        return False
    if value[-1] == ",":
        value = value[:-1]
    methods = value.split(",")
    methods = [m.strip() for m in methods]
    if len(expected) != len(methods):
        return False
    for exp in expected:
        if exp not in methods:
            return False
    return True

def verify_order(tasks):
    """
    Verify tasks array order.
    """
    if len(tasks) < 2:
        return True
    for i, task in enumerate(tasks[1:]):
        previous_date = dateutil.parser.parse(tasks[i-1]["deadline"])
        current_date = dateutil.parser.parse(task["deadline"])
        if previous_date < current_date:
            return False
    return True

def verify_ids(tasks, ids):
    """
    Verify task ids are in order.
    """
    task_ids = []
    for task in tasks:
        task_ids.append(task["id"])
    if task_ids == ids:
        return True
    return False

def head_test(title, base_url, url, count=0, verbose=False):
    """
    Test HEAD request.
    """
    print_header(title)
    response = run_request(base_url, url, method="HEAD", verbose=verbose)
    if response is None:
        print_fail("HTTP request didn't succeed")
        return (1, 0)
    elif response.status_code != 204:
        print_fail("Status code %d != 204" % (response.status_code))
        return (1, 0)
    # elif response.content is not None: # !!!
        # print_fail("response body not empty: " + response.content.decode("utf-8")  + "..")
        # return (1, 0)
    elif response.headers["x-count"] is None:
        print_fail("X-Count value is undefined")
        return (1, 0)
    elif int(response.headers["x-count"]) != count:
        #print_fail("Count %s" % response.headers["x-count"])
        #print_fail("Count %d" % response.headers["x-count"])
        #print_fail("Count %d" % count)
        print_fail("X-Count value %s != %d" % \
            (int(response.headers["x-count"]), count))
        return (1, 0)
    else:
        print_success()
        return (0, 1)

def test_fail(title, base_url, url, messages=1, code=404, method="GET", \
    data=None, verbose=False):
    """
    Test failed request.
    """
    print_header(title)
    response = run_request(base_url, url, method=method, data=data, \
        verbose=verbose)
    if response is None:
        print_fail("HTTP request didn't succeed")
        return (1, 0)
    elif response.status_code != code:
        print_fail("Status code %d != %d" % (response.status_code, code))
        return (1, 0)
    elif not isinstance(response.json(), dict):
        print_fail("Response body is not a JSON object. Body=%s" % \
            (json.dumps(response.json())))
        return (1, 0)
    elif "errorCode" not in response.json():
        print_fail("ErrorCode property doesn't exist in response")
        return (1, 0)
    elif "errorMessages" not in response.json():
        print_fail("ErrorMessages property doesn't exist in response")
        return (1, 0)
    elif response.json()["errorCode"] != code:
        print_fail("ErrorCode %d != %d" % (response.json()["errorCode"], code))
        return (1, 0)
    elif not isinstance(response.json()["errorMessages"], list):
        print_fail("ErrorMessages is not an array. errorMessages=%s" % \
            (json.dumps(response.json()["errorMessages"])))
        return (1, 0)
    elif len(response.json()["errorMessages"]) != messages:
        print_fail("Unexpected number of errors. %d != %d" % \
            (len(response.json()["errorMessages"]), messages))
        return (1, 0)
    else:
        print_success()
        return (0, 1)

def options_test(title, base_url, url, allow_value, verbose=False):
    """
    Test OPTIONS request.
    """
    print_header(title)
    response = run_request(base_url, url, method="OPTIONS", verbose=verbose)
    if response is None:
        print_fail("HTTP request didn't succeed")
        return (1, 0)
    elif response.status_code != 204:
        print_fail("Status code %d != 204" % (response.status_code))
        return (1, 0)
    # elif response.content is not None:
        # print_fail("Response body not empty")
        # return (1, 0)
    elif response.headers["allow"] is None:
        print_fail("Allow value is undefined")
        return (1, 0)
    elif not verify_allow(response.headers["allow"], allow_value):
        print_fail("Allow value is incorrect. Value=%s" % \
            (response.headers["allow"]))
        return (1, 0)
    else:
        print_success()
        return (0, 1)

def get_test(title, base_url, url, x_count, tasks_count, ids=None, \
    verbose=False):
    """
    Test GET request.
    """
    print_header(title)
    response = run_request(base_url, url, method="GET", verbose=verbose)
    if response is None:
        print_fail("HTTP request didn't succeed")
        return (1, 0)
    elif response.status_code != 200:
        print_fail("Status code %d != 200" % (response.status_code))
        return (1, 0)
    elif not isinstance(response.json(), list):
        print_fail("Response body is not an array. Body=%s" % \
            (json.dumps(response.json())))
        return (1, 0)
    elif len(response.json()) != tasks_count:
        print_fail("JSON array length missmatch %d != %d" % \
            (tasks_count, len(response.json())))
        return (1, 0)
    elif response.headers["x-count"] is None:
        print_fail("X-Count value is undefined")
        return (1, 0)
    elif int(response.headers["x-count"]) != x_count:
        print_fail("X-Count value %d != %d" % \
            (int(response.headers["x-count"]), x_count))
        return (1, 0)
    elif len(response.json()) != 0 and not verify_order(response.json()):
        print_fail("Task array out of order")
        return (1, 0)
    elif ids is not None and not verify_ids(response.json(), ids):
        print_fail("Task array content not as expected")
        return (1, 0)
    else:
        print_success()
        return (0, 1)

def post_test(title, base_url, url, task, verbose=False):
    """
    Test POST request.
    """
    print_header(title)
    response = run_request(base_url, url, method="POST", \
        data=json.dumps(task), verbose=verbose)
    if response is None:
        print_fail("HTTP request didn't succeed")
        return (1, 0, None)
    elif response.status_code != 200:
        print_fail("Status code %d != 200" % (response.status_code))
        return (1, 0, None)
    elif not isinstance(response.json(), dict):
        print_fail("Response body is not a JSON object. Body=%s" % \
            (json.dumps(response.json())))
        return (1, 0, None)
    elif "id" not in response.json():
        print_fail("Id property doesn't exist in response")
        return (1, 0, None)
    elif "title" not in response.json():
        print_fail("Title property doesn't exist in response")
        return (1, 0, None)
    elif "description" not in response.json():
        print_fail("Description property doesn't exist in response")
        return (1, 0, None)
    elif "deadline" not in response.json():
        print_fail("Deadline property doesn't exist in response")
        return (1, 0, None)
    elif response.json()["title"] != task["title"]:
        print_fail("Title doesn't match '%s' != '%s'" % \
            (response.json()["title"], task["title"]))
        return (1, 0, None)
    elif response.json()["description"] != task["description"]:
        print_fail("Description doesn't match '%s' != '%s'" % \
            (response.json()["description"], task["description"]))
        return (1, 0, None)
    elif response.json()["deadline"] != task["deadline"]:
        print_fail("Deadline doesn't match '%s' != '%s'" % \
            (response.json()["deadline"], task["deadline"]))
        return (1, 0, None)
    else:
        print_success()
        return (0, 1, response.json()["id"])

def index_test(title, base_url, url, task_id, verbose=False):
    """
    Test GET request for specific task.
    """
    print_header(title)
    response = run_request(base_url, url, method="GET", verbose=verbose)
    if response is None:
        print_fail("HTTP request didn't succeed")
        return (1, 0)
    elif response.status_code != 200:
        print_fail("Status code %d != 200" % (response.status_code))
        return (1, 0)
    elif not isinstance(response.json(), dict):
        print_fail("Response body is not a JSON object. Body=%s" % \
            (json.dumps(response.json())))
        return (1, 0)
    elif "id" not in response.json():
        print_fail("Id property doesn't exist in response")
        return (1, 0)
    elif "title" not in response.json():
        print_fail("Title property doesn't exist in response")
        return (1, 0)
    elif "description" not in response.json():
        print_fail("Description property doesn't exist in response")
        return (1, 0)
    elif "deadline" not in response.json():
        print_fail("Deadline property doesn't exist in response")
        return (1, 0)
    elif response.json()["id"] != task_id:
        print_fail("Task id missmatch %d != %d" % \
            (response.json()["id"], task_id))
        return (1, 0)
    else:
        print_success()
        return (0, 1)

def put_test(title, base_url, url, task, task_id, verbose=False):
    """
    Test PUT request.
    """
    print_header(title)
    response = run_request(base_url, url, method="PUT", \
        data=json.dumps(task), verbose=verbose)
    if response is None:
        print_fail("HTTP request didn't succeed")
        return (1, 0)
    elif response.status_code != 200:
        print_fail("Status code %d != 200" % (response.status_code))
        return (1, 0)
    elif not isinstance(response.json(), dict):
        print_fail("Response body is not a JSON object. Body=%s" % \
            (json.dumps(response.json())))
        return (1, 0)
    elif "id" not in response.json():
        print_fail("Id property doesn't exist in response")
        return (1, 0)
    elif "title" not in response.json():
        print_fail("Title property doesn't exist in response")
        return (1, 0)
    elif "description" not in response.json():
        print_fail("Description property doesn't exist in response")
        return (1, 0)
    elif "deadline" not in response.json():
        print_fail("Deadline property doesn't exist in response")
        return (1, 0)
    elif response.json()["title"] != task["title"]:
        print_fail("Title doesn't match '%s' != '%s'" % \
            (response.json()["title"], task["title"]))
        return (1, 0)
    elif response.json()["description"] != task["description"]:
        print_fail("Description doesn't match '%s' != '%s'" % \
            (response.json()["description"], task["description"]))
        return (1, 0)
    elif response.json()["deadline"] != task["deadline"]:
        print_fail("Deadline doesn't match '%s' != '%s'" % \
            (response.json()["deadline"], task["deadline"]))
        return (1, 0)
    elif response.json()["id"] != task_id:
        print_fail("Id doesn't match '%s' != '%s'" % \
            (response.json()["id"], task_id))
        return (1, 0)
    else:
        print_success()
        return (0, 1)

def patch_test(title, base_url, url, task, task_id, verbose=False):
    """
    Test PATCH request.
    """
    print_header(title)
    response = run_request(base_url, url, method="PATCH", \
        data=json.dumps(task), verbose=verbose)
    if response is None:
        print_fail("HTTP request didn't succeed")
        return (1, 0)
    elif response.status_code != 200:
        print_fail("Status code %d != 200" % (response.status_code))
        return (1, 0)
    elif not isinstance(response.json(), dict):
        print_fail("Response body is not a JSON object. Body=%s" % \
            (json.dumps(response.json())))
        return (1, 0)
    elif "id" not in response.json():
        print_fail("Id property doesn't exist in response")
        return (1, 0)
    elif "title" not in response.json():
        print_fail("Title property doesn't exist in response")
        return (1, 0)
    elif "description" not in response.json():
        print_fail("Description property doesn't exist in response")
        return (1, 0)
    elif "deadline" not in response.json():
        print_fail("Deadline property doesn't exist in response")
        return (1, 0)
    elif "title" in task and response.json()["title"] != task["title"]:
        print_fail("Title doesn't match '%s' != '%s'" % \
            (response.json()["title"], task["title"]))
        return (1, 0)
    elif "description" in task and \
        response.json()["description"] != task["description"]:
        print_fail("Description doesn't match '%s' != '%s'" % \
            (response.json()["description"], task["description"]))
        return (1, 0)
    elif "deadline" in task and \
        response.json()["deadline"] != task["deadline"]:
        print_fail("Deadline doesn't match '%s' != '%s'" % \
            (response.json()["deadline"], task["deadline"]))
        return (1, 0)
    elif response.json()["id"] != task_id:
        print_fail("Id doesn't match '%s' != '%s'" % \
            (response.json()["id"], task_id))
        return (1, 0)
    else:
        print_success()
        return (0, 1)

def delete_test(title, base_url, url, task_id, verbose=False):
    """
    Test DELETE request.
    """
    print_header(title)
    response = run_request(base_url, url, method="DELETE", verbose=verbose)
    if response is None:
        print_fail("HTTP request didn't succeed")
        return (1, 0)
    elif response.status_code != 200:
        print_fail("Status code %d != 200" % (response.status_code))
        return (1, 0)
    elif not isinstance(response.json(), dict):
        print_fail("Response body is not a JSON object. Body=%s" % \
            (json.dumps(response.json())))
        return (1, 0)
    elif "id" not in response.json():
        print_fail("Id property doesn't exist in response")
        return (1, 0)
    elif "title" not in response.json():
        print_fail("Title property doesn't exist in response")
        return (1, 0)
    elif "description" not in response.json():
        print_fail("Description property doesn't exist in response")
        return (1, 0)
    elif "deadline" not in response.json():
        print_fail("Deadline property doesn't exist in response")
        return (1, 0)
    elif response.json()["id"] != task_id:
        print_fail("Id doesn't match '%s' != '%s'" % \
            (response.json()["id"], task_id))
        return (1, 0)
    else:
        response = run_request(base_url, url, method="GET", verbose=verbose)
        if response.status_code != 404:
            print_fail("GET request found task")
            return (1, 0)
        else:
            print_success()
            return (0, 1)

def main():
    """
    Main function for test client.
    """
    # Setup flags
    parser = argparse.ArgumentParser(description='node-challenge test client', \
        epilog='Example: ./test.py http://127.0.0.1:8080/')
    parser.add_argument('endpoint', help='server endpoint')
    parser.add_argument('--verbose', '-v', \
        help='print verbose information during execution', action='store_true')
    parser.add_argument('--version', action='version', \
        version='%(prog)s ' + __version__, help='display version information')
    # Parse command line arguments
    args = parser.parse_args(sys.argv[1:])
    # Test counters
    failed_tests = 0
    succeeded_tests = 0
    # Test HEAD with empty database
    fail, succeed = head_test("Empty database HEAD request", args.endpoint, \
        "/tasks.json", verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test OPTIONS with /tasks.json path
    fail, succeed = options_test("OPTIONS request for /tasks.json", \
        args.endpoint, "/tasks.json", ["GET", "HEAD", "OPTIONS", "POST"], \
        verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test GET /tasks.json with no entries
    fail, succeed = get_test("Empty GET request for /tasks.json", \
        args.endpoint, "/tasks.json", 0, 0, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test GET /tasks.json?q=test with no entries
    fail, succeed = get_test("Empty GET request for /tasks.json?q=test", \
        args.endpoint, "/tasks.json?q=test", 0, 0, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test GET /tasks.json?pageSize=13 with no entries
    fail, succeed = get_test("Empty GET request for /tasks.json?pageSize=13", \
        args.endpoint, "/tasks.json?pageSize=13", 0, 0, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test POST /tasks.json with a valid object
    valid_task = {
        "title": "Task1",
        "description": "Task description 1",
        "deadline": "2015-09-11T09:00:00+01:00"
    }
    fail, succeed, task_id = post_test("Valid POST request", args.endpoint, \
        "/tasks.json", valid_task, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    valid_task["id"] = task_id
    # Test POST /tasks.json with an invalid objects
    invalid_task1 = {
        "title": "Tas",
        "description": "Task description 1",
        "deadline": "2015-09-11T09:00:00+01:00"
    }
    fail, succeed = test_fail("Invalid POST request 1", args.endpoint, \
        "/tasks.json", data=json.dumps(invalid_task1), method="POST", \
        messages=1, code=400, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    invalid_task2 = {
        "title": "A very long title that doesn't repeat in order to " + \
            "be bigger than 64 characters.",
        "description": "Task description 1",
        "deadline": "2015-09-11T09:00:00+01:00"
    }
    fail, succeed = test_fail("Invalid POST request 2", args.endpoint, \
        "/tasks.json", data=json.dumps(invalid_task2), method="POST", \
        messages=1, code=400, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    invalid_task3 = {
        "title": "Task1",
        "deadline": "2015-09-11T09:00:00+01:00"
    }
    fail, succeed = test_fail("Invalid POST request 3", args.endpoint, \
        "/tasks.json", data=json.dumps(invalid_task3), method="POST", \
        messages=1, code=400, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    invalid_task4 = {
        "title": "Task1",
        "description": "A very long task description that repeats in " + \
            "order to be bigger than 255 characters. A very long task " + \
            "description that repeats in order to be bigger than 255 " + \
            "characters. A very long task description that repeats in order" + \
            " to be bigger than 255 characters. A very long task " + \
            "description that repeats in order to be bigger than 255" + \
            " characters.",
        "deadline": "2015-09-11T09:00:00+01:00"
    }
    fail, succeed = test_fail("Invalid POST request 4", args.endpoint, \
        "/tasks.json", data=json.dumps(invalid_task4), method="POST", \
        messages=1, code=400, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    invalid_task5 = {
        "title": "Task1",
        "description": "Task description 1",
        "deadline": "2015/09/11"
    }
    fail, succeed = test_fail("Invalid POST request 5", args.endpoint, \
        "/tasks.json", data=json.dumps(invalid_task5), method="POST", \
        messages=1, code=400, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    invalid_task6 = {
        "title": "Task1",
        "description": "Task description 1",
        "deadline": ""
    }
    fail, succeed = test_fail("Invalid POST request 6", args.endpoint, \
        "/tasks.json", data=json.dumps(invalid_task6), method="POST", \
        messages=1, code=400, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test POST /tasks.json with two additional tasks
    valid_task2 = {
        "title": "Task2",
        "description": "Task description 2",
        "deadline": "2015-09-12T09:00:00+01:00"
    }
    fail, succeed, task_id = post_test("Valid POST request 2", \
        args.endpoint, "/tasks.json", valid_task2, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    valid_task2["id"] = task_id
    valid_task3 = {
        "title": "Task3",
        "description": "",
        "deadline": "2015-09-13T09:00:00+01:00"
    }
    fail, succeed, task_id = post_test("POST request with empty description", \
        args.endpoint, "/tasks.json", valid_task3, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    valid_task3["id"] = task_id
    # Test HEAD /tasks.json with 3 tasks
    fail, succeed = head_test("HEAD request with 3 tasks", args.endpoint, \
        "/tasks.json", count=3, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test GET /tasks.json deadline order
    fail, succeed = get_test("Test GET request order", args.endpoint, \
        "/tasks.json", 3, 3, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test GET /tasks.json?page=2&pageSize=1 pagination
    fail, succeed = get_test("Test GET pagination", args.endpoint, \
        "/tasks.json?page=2&pageSize=1", 3, 1, ids=[valid_task2["id"]], \
        verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test GET /tasks.json?q=task1 search
    fail, succeed = get_test("Test GET search", args.endpoint, \
        "/tasks.json?q=task1", 1, 1, ids=[valid_task["id"]], \
        verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test GET /tasks/ID.json
    fail, succeed = index_test("Task GET request", args.endpoint, \
        "/tasks/" + str(valid_task3["id"]) + ".json", valid_task3["id"], \
        verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test GET /tasks/BAD_ID.json
    fail, succeed = test_fail("Task GET with bad id", args.endpoint, \
        "/tasks/982.json", method="GET", messages=1, code=404, \
        verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test OPTIONS /tasks/ID.json
    fail, succeed = options_test("Task OPTIONS request", args.endpoint, \
        "/tasks/" + str(valid_task["id"]) + ".json", \
        ["GET", "OPTIONS", "PUT", "PATCH", "DELETE"], verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test OPTIONS /tasks/BAD_ID.json
    fail, succeed = test_fail("Task OPTIONS with bad id", args.endpoint, \
        "/tasks/88.json", method="OPTIONS", messages=1, code=404, \
        verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test PUT /tasks/ID.json
    put_task = {
        "title": "Task3.1",
        "description": "",
        "deadline": "2015-09-13T09:00:00+01:00"
    }
    fail, succeed = put_test("Valid PUT request", args.endpoint, \
        "/tasks/" + str(valid_task3["id"]) + ".json", put_task, \
        valid_task3["id"], verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test PUT /tasks/ID.json with missing property
    invalid_put = {
        "title": "Task3.1",
        "deadline": "2015-09-13T09:00:00+01:00"
    }
    fail, succeed = test_fail("Task PUT with missing property", \
        args.endpoint, "/tasks/" + str(valid_task3["id"]) + ".json", \
        data=json.dumps(invalid_put), method="PUT", messages=1, code=400, \
        verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test PUT /tasks/ID.json with invalid property
    invalid_put2 = {
        "title": "T",
        "description": "",
        "deadline": "2015-09-13T09:00:00+01:00"
    }
    fail, succeed = test_fail("Task PUT with invalid property", \
        args.endpoint, "/tasks/" + str(valid_task3["id"]) + ".json", \
        data=json.dumps(invalid_put2), method="PUT", messages=1, code=400, \
        verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test PUT /tasks/BAD_ID.json
    fail, succeed = test_fail("Task PUT with bad id", args.endpoint, \
        "/tasks/88.json", data=json.dumps(put_task), method="PUT", \
        messages=1, code=404, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test PATCH /tasks/ID.json
    patch_task = {
        "title": "Task2.1"
    }
    fail, succeed = patch_test("Valid PATCH request", args.endpoint, \
        "/tasks/" + str(valid_task2["id"]) + ".json", patch_task, \
        valid_task2["id"], verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test PATCH /tasks/ID.json with invalid property
    invalid_patch = {
        "title": "T"
    }
    fail, succeed = test_fail("Task PATCH with invalid property", \
        args.endpoint, "/tasks/" + str(valid_task2["id"]) + ".json", \
        data=json.dumps(invalid_patch), method="PATCH", messages=1, \
        code=400, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test PATCH /tasks/BAD_ID.json
    fail, succeed = test_fail("Task PATCH with bad id", args.endpoint, \
        "/tasks/88.json", data=json.dumps(patch_task), method="PATCH", \
        messages=1, code=404, verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test DELETE /tasks/ID.json
    fail, succeed = delete_test("Valid DELETE request", args.endpoint, \
        "/tasks/" + str(valid_task2["id"]) + ".json", valid_task2["id"], \
        verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Test DELETE /tasks/BAD_ID.json
    fail, succeed = test_fail("Task DELETE with bad id", args.endpoint, \
        "/tasks/88.json", method="DELETE", messages=1, code=404, \
        verbose=args.verbose)
    failed_tests += fail
    succeeded_tests += succeed
    # Print summary
    print_test_summary(failed_tests, succeeded_tests)
    return 0

if __name__ == "__main__":
    RET = main()
    sys.exit(RET)
