var express = require('express');
var router = express.Router();
var axios = require('axios');
const utils = require('../utils');

/* GET users listing. */
router.get('/', async function (req, res, next) {
  const token = req.cookies['token'];
  const auth = 'Bearer ' + token;
  // 200 OK if token is valid and I have permissions
  // 403 Forbidden if token is valid and I do not have permissions
  // 500 Internal Server Error if something bad happened server side
  let response = null;
  try {
    response = await axios.get('/users', { headers: { 'Authorization': auth } });
    if (response.status === 401) {
      utils.redirectToLogin(res);
      return;
    } else if (response.status === 200) {
      res.render('users', { title: 'Users', users: response.data });
    } else {
      res.render('error', { message: 'Something went wrong', error: {} });
    }
  } catch (e) {
    res.render('error', { message: e.message, error: { status: response.status } });
  }
});

module.exports = router;
