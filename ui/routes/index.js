var express = require('express');
var router = express.Router();
var axios = require('axios');

const utils = require('../utils');
const FormData = require('form-data');

router.use(express.urlencoded({ extended: true }));

/* GET home page. */
router.get('/', function (req, res, next) {
  const token = req.cookies['token'];
  utils.userIsLoggedIn(token)
    .then(isLoggedIn => {
      if (isLoggedIn)
        res.render('index', { title: 'Home' });
      else
        res.redirect('/login');
    })
    .catch(err => res.render('error', { message: err, error: { status: err.status } }));
});

/* GET login page. */
router.get('/login', function (req, res, next) {
  res.render('login', { title: 'Sign In' });
});

/* GET orders */
router.get('/orders', async function (req, res) {
  
  const token = req.cookies['token'];
  const auth = 'Bearer ' + token;
  // 200 OK if token is valid and I have permissions
  // 403 Forbidden if token is valid and I do not have permissions
  // 500 Internal Server Error if something bad happened server side
  let response = null;
  let id = null;
  //call to get user data
  try{
    response = await axios.get('auth/me', {headers: {'Authorization': auth}});
    if (response.status === 401) {
      utils.redirectToLogin(res);
      return;
    }
    id=response.data['id'];
  }catch(e){
    res.render('error', { message: e.message, error: { status: response.status } });
  }
  try {
    response = await axios.get('/users/'+id+'/orders', { headers: { 'Authorization': auth } });
    if (response.status === 401) {
      utils.redirectToLogin(res);
      return;
    } else if (response.status === 200) {
      res.render('orders', { title: 'Orders', orders: response.data });
    } else {
      res.render('error', { message: 'Something went wrong', error: {} });
    }
  } catch (e) {
    res.render('error', { message: e.message, error: { status: response.status } });
  }
  // res.render('orders', { title: 'Orders' });
})

/* GET labels */
router.get('/labels', function (req, res) {
  res.render('labels', { title: 'Labels' });
})

/* POST login page. */
router.post('/login', async function (req, res, next) {
  const email = req.body.email;
  const password = req.body.password;
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);
  // TODO: handle errors
  const response = await axios.post('/auth/token', formData, { headers: formData.getHeaders() });
  res.cookie('token', response.data.access_token);
  res.redirect('/');
});

module.exports = router;
