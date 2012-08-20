var nano = require('nano')('http://localhost:5984');
/*
 * GET home page.
 */

exports.index = function(req, res){
  res.render('index', { title: 'Symfopi' });
};
/*
* Respond to POSTed form, adding user to CouchDB and reloading with the authed user.
*/
exports.indexPost = function(req, res) {
	var spot_users = nano.use('spotify_users');
	console.log(req.body.user);
	spot_users.insert({ user: req.body.user, pass: req.body.pwd}, function(err, body) {
  	if (!err)
    	console.log(body);
	});
	res.render('index', { title: 'Symfopi', user: req.body.user });
};
