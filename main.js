/*
- testna skripta ne prepozna praznega responsa
- ko TS pošlje JSON na server (post) ne pove, da gre za JSON
- katere verzije orodij so sploh aktualne? v express4 nekatere stvari manjkajo (body parser)
- express4 body parser pri POST zahteva "Content-Type: application/json"
- tukaj je vidno, da vrne taske sortirane po datumu od najmlajšega do najstarejšega, vendar test kljub temu pade:
 >> ali python na win parsa datume razlièno kot na linux??
	------------------------------------------------------------------
	‹[95m‹[1mTest GET request order‹[0m
	------------------------------------------------------------------
	‹[95m[‹[4mINFO‹[0m‹[95m]‹[0m Request url=http://localhost:7000/tasks.json
	‹[95m[‹[4mINFO‹[0m‹[95m]‹[0m Request method=GET
	‹[95m[‹[4mINFO‹[0m‹[95m]‹[0m Response code=200
	‹[95m[‹[4mINFO‹[0m‹[95m]‹[0m Response body=[
	{"id":3,"title":"Task3","description":"",                  "deadline":"2015-09-13T09:00:00+01:00"},
	{"id":2,"title":"Task2","description":"Task description 2","deadline":"2015-09-12T09:00:00+01:00"},
	{"id":1,"title":"Task1","description":"Task description 1","deadline":"2015-09-11T09:00:00+01:00"}
	]
	‹[95m[‹[4mINFO‹[0m‹[95m]‹[0m Response headers={'Content-Length': '280', 'X-Count
	': '3', 'X-Powered-By': 'Express', 'Connection': 'keep-alive', 'ETag': 'W/"118-J
	90IVdzzJHbvtdY1mijvPQ"', 'Date': 'Sun, 24 Jan 2016 17:25:41 GMT', 'Content-Type'
	: 'application/json; charset=utf-8'}
	Status: ‹[91mFail‹[0m
	Reason: Task array out of order



https://www.npmjs.com/package/validator
npm install validator
npm install body-parser
*/

// because test script does not add content-type to requests, body-parser does not fire
function defaultContentTypeMiddleware (req, res, next) {
  //req.headers['content-type'] = req.headers['content-type'] || 'application/json';
  req.headers['content-type'] = 'application/json';
  next();
}


var m = {
  "id": 42,
  "title": "Put on pants 1",
  "description": "When you wake up make sure to put on some pants.",
  "deadline": "2015-09-14T07:00:00+01:00"
};
// var e = {
  // "errorCode": 400,
  // "errorMessages": [
    // // "Title can't be empty",
    // // "Deadline isn't an ISO8601 date string"
  // ]
// }
var error = function(errNum, errMsg) {
  this.errorCode = errNum;
  this.errorMessages = [ errMsg ];
}

// required
var url = require('url');
var sqlite3 = require('sqlite3').verbose();
var express = require('express');

// extra
var validator = require('validator');
var bodyParser = require('body-parser')

// init database
var db = new sqlite3.Database('mydb.db');
db.serialize(function() {
	db.run("DROP TABLE tasks");
	db.run("CREATE TABLE if not exists tasks (id INTEGER PRIMARY KEY, title TEXT, description TEXT, deadline TEXT)");
});


var app = express();
app.use(defaultContentTypeMiddleware);
app.use(bodyParser.json());

// this will validate task and return a valid task or an error object
var validate = function(task) {
	var er = new error(400, '');
	er.errorMessages = [];
	var q = { body : task };
	// validate
	if (q.body.title == undefined || q.body.title == null || q.body.title.length < 4 || q.body.title.length >= 64) 
		er.errorMessages.push("Title must be a string between 4 and 64 characters");
	if (q.body.description == undefined || q.body.description == null || q.body.description.length < 0 || q.body.description.length >= 255) 
		er.errorMessages.push("Description must be a string between 0 and 255 characters");
	if (!validator.isISO8601(q.body.deadline)) 
		er.errorMessages.push("Date must be ISO8601 formatted string!");

	return (er.errorMessages.length > 0) ? er : task;
}

app.head('/tasks.json', function(q, s) {
	//s.send('Returns the number of tasks in the database as a header variable _X-Count_. The response doesn\'t return any body and returns 204 response code.');
	db.get("SELECT COUNT(*) len FROM tasks", function(err, row) {
		if (err != undefined) console.log(err);
		var i = parseInt(row.len);
		console.log("HEAD /tasks.json :: X-Count: " + i);
		console.log("Body: " + s.body);
		console.log("");
		s.setHeader('X-Count', i);
		s.status(204);
		s.end();
		//s.send(new Buffer(0));
	});
});

app.options('/tasks.json', function(q, s) {
	//s.send('Returns the supported methods for the current path as a header variable _Allow_. The response doesn\'t return any body and returns 204 response code. For more information check [RFC2616 Section 14](http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html).');
	console.log('OPTIONS /tasks.json');
	console.log("");
	//s.setHeader('Allow', 'GET,HEAD,OPTIONS,POST,PUT,PATCH,DELETE');
	s.setHeader('Allow', 'GET,HEAD,OPTIONS,POST');
	s.status(204);
	s.end();
});

app.get('/tasks.json', function(q, s) {
	//s.send('Returns an array of task JSON objects ordered by deadline. If no tasks are in database it needs to return an empty array.The response also needs to return a header with the number of all tasks in database named _X-Count_ and a response code of 200. The path also needs to implement two mechanisms. First mechanism is pagination. It\'s controlled using two query parameters _page_ and _pageSize_. Default value for _page_ is 1 and default value for _pageSize_ is 10. For example if a client would request the following path `GET /tasks.json?page=2&pageSize=15` the server would return tasks 15 to 30 after ordering by deadline. If the database would have less than 15 tasks the server would return an empty array. The second mechanism is search. It\'s controlled using the query parameter _q_. By default if _q_ isn\'t defined no search is executed. For instance if a client would request the following path `GET /tasks.json?q=this+that` the server would return at most 10 tasks that contain `this that` in their title and/or description. Again if there aren\'t any tasks with that search term the server returns an empty array. The search mechanism also needs to update the _X-Count_ header to represent the number of all tasks that contain the search term.');

	var url_parts = url.parse(q.url, true);

  // get page
	var page = parseInt(url_parts.query.page);
	if (!page) page = 1;

	// get pageSize
	var pageSize = parseInt(url_parts.query.pageSize);
	if (!pageSize) pageSize = 10;

	// get q
	var qry = "";
	console.log("Q: " + url_parts.query.q);
	if (url_parts.query.q != undefined) {
		//qry = url_parts.query.q.replace('\'', '\\\'');
		qry = url_parts.query.q.replace(/'/g, ''); // attempt escape injection
		console.log("Q:> " + qry);
	}

	// build queries
	var where = qry != "" ? " WHERE title LIKE '%" + qry + "%' OR description LIKE '%" + qry + "%'" : " ";
	var limit = " LIMIT " + pageSize + " OFFSET " + ((page-1) * pageSize);
	var sql = "SELECT id, title, description, deadline FROM tasks " + where + " ORDER BY date(deadline) DESC " + limit;
	var sql_all = "SELECT COUNT(*) len FROM tasks " + where;
	//returnValue.push({ q : sql, q_all : sql_all });

	// get "meta"data
	db.get(sql_all, function(err, row) {
		if (err != undefined) console.log(err);
		var i = parseInt(row.len);
		console.log("GET /tasks.json :: X-Count: " + i);
		console.log("");

		// set headers acc. to metadata
		s.setHeader('X-Count', i);
		s.status(200);

		// get data
		db.all(sql, function(err1, row1) {
			if (err1) {
				s.send(err1);
				return;
			}
			s.json(row1);
		});
	});
});

app.post('/tasks.json', function(q, s) {
	//s.send('This path needs to add a new task into the database. The request will contain a JSON task object. The server needs to validate that all properties are there and in the correct format. Title needs to be a string between 4 and 64 characters in length. Description also needs to be a string between 0 and 255 characters in length. Deadline needs to be a date string in the [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format. The path needs to return an error if the object requirements aren\'t met. Upon successful insertion into the database the path returns the new object back to the client.');
	// log position
	console.log("POST /tasks.json");
	console.log("Task title: " + q.body.title);
	//console.log(q.headers);

	// validate
	var err = new validate(q.body);
	// process error
	if (err.errorMessages != undefined) s.status(400).json(err);
	// process data
	else { 
		var a = { title : q.body.title, description : q.body.description, deadline : q.body.deadline };
		db.run("INSERT INTO tasks (title, description, deadline) VALUES (?, ?, ?)", a.title, a.description, a.deadline, function(e, r) {
			if (e) console.log(e);
			console.log("Inserted with ID: " + this.lastID);
			console.log("");
			// this.changes !!!
			a.id = this.lastID;
			s.status(200).json(a);
		});
	}
});

app.options('/tasks/:taskid.json', function(q, s) {
	// q.query.key
	//s.send('Returns the supported methods for the current path as a header variable _Allow_. The response doesn\'t return any body and returns 204 response code. For more information check [RFC2616 Section 14](http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html).');
	console.log('OPTIONS /tasks/' + q.params.taskid + '.json');
	console.log("");
	//s.setHeader('Allow', 'GET,HEAD,OPTIONS,POST,PUT,PATCH,DELETE');

	var taskId = parseInt(q.params.taskid);
	var sql = "SELECT id, title, description, deadline FROM tasks WHERE id = ?";
	db.get(sql, taskId, function(er, r) {
		if (er) console.log(er);
		console.log(r);

		if (r != undefined) { // return task if found
			s.setHeader('Allow', 'OPTIONS,GET,PUT,PATCH,DELETE');
			s.status(204);
			s.end();
		}
		else { // return error if not found
			var retVal = new error(404, "Task " + taskId + " does not exist!");
			s.status(404);
			s.json(retVal);
		}
	});

});

app.get('/tasks/:taskid.json', function(q, s) {
	//s.send('The path returns the object with task id that was specified by the client in the request url. For example if the client would request the following url: `GET /tasks/13.json` the server would return the following JSON object. If the requested task doesn\'t exist the server needs to return an appropriate error.');
	console.log("GET /tasks/" + q.params.taskid + ".json");
	var taskId = parseInt(q.params.taskid);
	var sql = "SELECT id, title, description, deadline FROM tasks WHERE id = ?";
	db.get(sql, taskId, function(er, r) {
		if (er) console.log(er);
		console.log(r);
		var retVal = {};
		
		if (r != undefined) { // return task if found
			retVal = r;
			s.status(200);
		}
		else { // return error if not found
			// e.errorMessages = ["Task " + taskId + " does not exist!"];
			// e.errorCode = 404;
			retVal = new error(404, "Task " + taskId + " does not exist!");
			s.status(404);
		}
		s.json(retVal);
	});
});

app.put('/tasks/:taskid.json', function(q, s) {
	//s.send('This path enables the client to update a task that is already in the database. PUT method requires the client to send all three task properties. After task properties are validated and the task item is updated the server returns the updated JSON object. ');
	var taskId = parseInt(q.params.taskid);
	console.log("PUT /tasks/" + taskId + ".json");
	var val = validate(q.body);
	//console.log(val.errorCode);
	if (val.errorCode != undefined) s.status(400).json(val);
	else {
		// check if exists
		var check = "SELECT COUNT(*) len FROM tasks WHERE id = ?";
		db.get(check, taskId, function(er2, re2) {
			if (er2 == null && re2.len == 1) {
				// if exists then update
				var sql = "UPDATE tasks SET title = ?, description = ?, deadline = ? WHERE id = ?";
				db.run(sql, q.body.title, q.body.description, q.body.deadline, taskId, function(err, res) {
					if (err) console.log(err);
					// and return updated
					db.get("SELECT id, title, description, deadline FROM tasks WHERE id = ?", q.params.taskid, function(er1, re1) {
						if (er1 == null) s.json(re1);
					});
				});
			}
			// if not exists return error
			else s.status(404).json(new error(404, "Task " + taskId + " not found."));
		});
	}
});

app.patch('/tasks/:taskid.json', function(q, s) {
	//s.send('This path is the same as the previous except that it allows the client to only send the properties it wants to update.');
	var taskId = parseInt(q.params.taskid);
	console.log("PATCH /tasks/" + taskId + ".json");

	// check if exists
	var check = "SELECT title, description, deadline FROM tasks WHERE id = ?";
	db.get(check, taskId, function(er2, re2) {
		if (er2 == null && re2 != null) {
			// if exists then update with present values
			re2.title = q.body.title != undefined ? q.body.title : re2.title;
			re2.description = q.body.description != undefined ? q.body.description : re2.description;
			re2.deadline = q.body.deadline != undefined ? q.body.deadline : re2.deadline;
			// validate new values
			var validated = validate(re2);
			// if new object is valid
			if (validated.errorMessages == undefined) {
				// save it
				var sql = "UPDATE tasks SET title = ?, description = ?, deadline = ? WHERE id = ?";
				db.run(sql, re2.title, re2.description, re2.deadline, taskId, function(err, res) {
					if (err) console.log(err);
					// and return updated
					db.get("SELECT id, title, description, deadline FROM tasks WHERE id = ?", q.params.taskid, function(er1, re1) {
						if (er1 == null) s.json(re1);
					});
				});
			}
			// else return error
			else s.status(400).json(validated);
		}
		// if not exists return error
		else s.status(404).json(new error(404, "Task " + taskId + " not found."));
	});
});

app.delete('/tasks/:taskid.json', function(q, s) {
	//s.send('This path enables the client to delete a task from database. After the task is successfully deleted the server needs to return it to the client.');
	var taskId = q.params.taskid;
	console.log("DELETE /tasks/" + taskId + ".json");
	
	var sql = "SELECT id, title, description, deadline FROM tasks WHERE id = ?";
	db.get(sql, taskId, function(err, row) {
		if (!err && !row) {
			s.status(404).json(new error(404, "Task " + taskId + " not found."));
		} else {
			var sql_del = "DELETE FROM tasks WHERE id = ?";
			db.run(sql_del, taskId, function(er1, ro1) {
				if (er1 == null) s.json(row);
			});
		}
	});
});


app.listen(8080, function () {
  console.log('Example app listening on port 8080!');
});




//db.close();
