# node-challenge

This challenge requires you to write a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer) server using [Node.JS](https://nodejs.org/) and [Express](http://expressjs.com/) framework. The server needs to implement requirements and paths defined in the sections below. The code needs to run on a [Ubuntu 14.04](http://www.ubuntu.com/) server.

#### Challenge requirements
- Use [Node.JS](https://nodejs.org/) environment
- Use [Express](http://expressjs.com/) framework
- Use [RESTful](https://en.wikipedia.org/wiki/Representational_state_transfer) approach to API building
- Use [JSON](https://en.wikipedia.org/wiki/JSON) as input and output
- Use [SQLite](http://sqlite.org/) database
- Write run instructions into the [SETUP.md](SETUP.md) file

#### Bonus requirements
- Use [mocha](https://mochajs.org/) library for unit tests
- Adhere to [JSLint](https://github.com/douglascrockford/JSLint) code style guide

#### Task model
Task model needs to contain a unique identifier, title string, description string and deadline that contains date and time. An example of the model in JSON format:
```
{
  "id": 42,
  "title": "Put on pants",
  "description": "When you wake up make sure to put on some pants.",
  "deadline": "2015-09-14T06:00:00+01:00"
}
```
#### Paths
###### HEAD /tasks.json
Returns the number of tasks in the database as a header variable _X-Count_. The response doesn't return any body and returns 204 response code.
###### OPTIONS /tasks.json
Returns the supported methods for the current path as a header variable _Allow_. The response doesn't return any body and returns 204 response code. For more information check [RFC2616 Section 14](http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html).
###### GET /tasks.json
Returns an array of task JSON objects ordered by deadline. If no tasks are in database it needs to return an empty array. An example response would look like so:
```
[
  {
    "id": 12,
    "title": "Task1",
    "description": "Some description",
    "deadline": "2015-09-12T06:00:00+01:00"
  },
  {
    "id": 13,
    "title": "Task2",
    "description": "Some description 2",
    "deadline": "2015-09-12T09:00:00+01:00"
  }
]
```
The response also needs to return a header with the number of all tasks in database named _X-Count_ and a response code of 200.
The path also needs to implement two mechanisms. First mechanism is pagination. It's controlled using two query parameters _page_ and _pageSize_. Default value for _page_ is 1 and default value for _pageSize_ is 10. For example if a client would request the following path `GET /tasks.json?page=2&pageSize=15` the server would return tasks 15 to 30 after ordering by deadline. If the database would have less than 15 tasks the server would return an empty array. The second mechanism is search. It's controlled using the query parameter _q_. By default if _q_ isn't defined no search is executed. For instance if a client would request the following path `GET /tasks.json?q=this+that` the server would return at most 10 tasks that contain `this that` in their title and/or description. Again if there aren't any tasks with that search term the server returns an empty array. The search mechanism also needs to update the _X-Count_ header to represent the number of all tasks that contain the search term.
###### POST /tasks.json
This path needs to add a new task into the database. The request will contain a JSON task object like so:
```
{
  "title": "Task3",
  "description": "Some description 3",
  "deadline": "2015-09-12T12:00:00+01:00"
}
```
The server needs to validate that all properties are there and in the correct format. Title needs to be a string between 4 and 64 characters in length. Description also needs to be a string between 0 and 255 characters in length. Deadline needs to be a date string in the [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format. The path needs to return an error if the object requirements aren't met. For example:
```
{
  "errorCode": 400,
  "errorMessages": [
    "Title can't be empty",
    "Deadline isn't an ISO8601 date string"
  ]
}
```
Upon successful insertion into the database the path returns the new object back to the client:
```
{
  "id": 14,
  "title": "Task3",
  "description": "Some description 3",
  "deadline": "2015-09-12T12:00:00+01:00"
}
```
###### OPTIONS /tasks/[TASK_ID].json
Returns the supported methods for the current path as a header variable _Allow_. The response doesn't return any body and returns 204 response code. For more information check [RFC2616 Section 14](http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html).
###### GET /tasks/[TASK_ID].json
The path returns the object with task id that was specified by the client in the request url. For example if the client would request the following url: `GET /tasks/13.json` the server would return the following JSON object:
```
{
  "id": 13,
  "title": "Task2",
  "description": "Some description 2",
  "deadline": "2015-09-12T09:00:00+01:00"
}
```
If the requested task doesn't exist the server needs to return an appropriate error.
###### PUT /tasks/[TASK_ID].json
This path enables the client to update a task that is already in the database. PUT method requires the client to send all three task properties. An example PUT request would look like this:
```
{
  "title": "Task3.1",
  "description": "Some description 3",
  "deadline": "2015-09-12T12:00:00+01:00"
}
```
After task properties are validated and the task item is updated the server returns the updated JSON object:
```
{
  "id": 14,
  "title": "Task3.1",
  "description": "Some description 3",
  "deadline": "2015-09-12T12:00:00+01:00"
}
```
###### PATCH /tasks/[TASK_ID].json
This path is the same as the previous except that it allows the client to only send the properties it wants to update. For instance:
```
{
  "description": "Some description 3.1",
  "deadline": "2015-10-12T12:00:00+01:00"
}
```
And after a successful update the server returns the updated JSON object:
```
{
  "id": 14,
  "title": "Task3.1",
  "description": "Some description 3.1",
  "deadline": "2015-10-12T12:00:00+01:00"
}
```
###### DELETE /tasks/[TASK_ID].json
This path enables the client to delete a task from database. After the task is successfully deleted the server needs to return it to the client. For instance a response to `DELETE /tasks/14.json` would be:
```
{
  "id": 14,
  "title": "Task3.1",
  "description": "Some description 3.1",
  "deadline": "2015-10-12T12:00:00+01:00"
}
```
###### Error handling
As shown in previous paths the format for error reporting is as follows:
```
{
  "errorCode": NUM,
  "errorMessages": [
    STRING,
    STRING
  ]
}
```
Of course you need to return the error code as a response code as well.
### Test client setup
In order to run the test script provided you need to install python and some additional libraries. The instructions below are for a Ubuntu 14.04 server if you are running the script on another platform you might need to use a different method to install the needed libraries and binaries.
```
sudo apt-get install -y python python-dateutil
```
To run the test script against your server call it like so:
```
python test.py http://127.0.0.1:8080/
```
The script will test every aspect of the API and print out the report. If the script reports no failed tests then your server meets the requirements. If you need additional debug information to fix your problems you can call the test script with
a verbose flag.
```
python test.py http://127.0.0.1:8080/ -v
```
### Change Log
###### 1.0
- Python test client
- Readme with instructions
- Empty setup file
