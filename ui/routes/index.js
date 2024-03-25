var express = require('express');
var router = express.Router();
var axios = require('axios');
const FormData = require('form-data');

axios.defaults.baseURL = process.env.API_URL;

router.use(express.urlencoded({ extended: true }));

/* GET home page. */
router.get('/', function (req, res, next) {
  res.render('index', { title: 'Demo' });
});

/* GET login page. */
router.get('/login', function (req, res, next) {
  res.render('login', { title: 'Sign In' });
});

/* POST login page. */
router.post('/login', async function (req, res, next) {
  const email = req.body.email;
  const password = req.body.password;
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);
  // TODO: handle errors
  const response = await axios.post('/token', formData, { headers: formData.getHeaders() });
  res.cookie('token', response.data.access_token);
  res.redirect('/');
});

module.exports = router;
