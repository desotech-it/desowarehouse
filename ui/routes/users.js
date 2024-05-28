var express = require('express');
var router = express.Router();
var axios = require('axios');
const utils = require('../utils');
async function getMetadata(token, title){
  const role = await utils.getUserRole(token);
  if(role=="admin")
    return { title: title, show_labels: false, show_orders: true, show_users: true, change_status: true, role:role};
  else if(role=="warehouse")
    return {title: title, show_labels: true, show_orders: false, show_users: false, change_status: true, role:role}
  else
    return {title: title, show_labels: false, show_orders: false, show_users: false, change_status: false, role:role}
  }
/* GET users listing. */
router.get('/', async function (req, res, next) {
  const token = req.cookies['token'];
  const auth = 'Bearer ' + token;
  // 200 OK if token is valid and I have permissions
  // 403 Forbidden if token is valid and I do not have permissions
  // 500 Internal Server Error if something bad happened server side
  let response = null;
  let user = null;
  try {
    response = await utils.getUserInfo(token);
    user=response;
    response = await axios.get('/users', { headers: { 'Authorization': auth } });
    if (response.status === 401) {
      utils.redirectToLogin(res);
      return;
    } else if (response.status === 200) {
      const metadata = await getMetadata(token, "Users");
      res.render('users', Object.assign({}, metadata, {users: response.data, user:user }));
    } else {
      res.render('error', { message: 'Something went wrong', error: {} });
    }
  } catch (e) {
    res.render('error', { message: e.message, error: { status: response.status } });
  }
});

module.exports = router;
