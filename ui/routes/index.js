var express = require('express');
var router = express.Router();
var axios = require('axios');
var PDFDocument = require('pdfkit');

const utils = require('../utils');
const FormData = require('form-data');

router.use(express.urlencoded({ extended: true }));
async function getMetadata(token, title){
  const role = await utils.getUserRole(token);
  if(role=="admin")
    return { title: title, show_labels: false, show_orders: true, show_users: true, change_status: true};
  else if(role=="warehouse")
    return {title: title, show_labels: true, show_orders: false, show_users: false, change_status: true}
  else
    return {title: title, show_labels: false, show_orders: false, show_users: false, change_status: false}
  }

/* GET home page. */
router.get('/', function (req, res, next) {
  const token = req.cookies['token'];
  
  utils.userIsLoggedIn(token)
    .then(async (isLoggedIn) => {
      if (isLoggedIn)
        res.render('index', await getMetadata(token, 'Home'));
      else
        res.redirect('/login');
    })
    .catch(err => res.render('error', { message: err, error: { status: err.status } }));
});

/* GET login page. */
router.get('/login', function (req, res, next) {
  res.render('login', { title: 'Sign In' });
});

/* GET all orders */
router.get('/allOrders', async function (req, res) {
  
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
    response = await axios.get('/orders', { headers: { 'Authorization': auth } });
    if (response.status === 401) {
      utils.redirectToLogin(res);
      return;
    } else if (response.status === 200) {
      const metadata = await getMetadata(token, "Orders");
      console.log(response.data)
      res.render('allOrders', Object.assign({}, metadata, {orders:response.data}));
    } else {
      res.render('error', { message: 'Something went wrong', error: {} });
    }
  } catch (e) {
    res.render('error', { message: e.message, error: { status: response.status } });
  }
  // res.render('orders', { title: 'Orders' });
})

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
      const metadata = await getMetadata(token, 'Orders');
      res.render('orders', Object.assign({}, metadata, {orders: response.data }));
    } else {
      res.render('error', { message: 'Something went wrong', error: {} });
    }
  } catch (e) {
    res.render('error', { message: e.message, error: { status: response.status } });
  }
  // res.render('orders', { title: 'Orders' });
})

/* GET labels */
router.get('/labels', async function (req, res) {
  const token = req.cookies['token'];
  const auth = 'Bearer ' + token;
  let response = null;
  try {
    response = await axios.get('/shipments', { headers: { 'Authorization': auth } });
    if (response.status === 401) {
      utils.redirectToLogin(res);
      return;
    } else if (response.status === 200) {
      const metadata = await getMetadata(token, "Labels");
      res.render('labels', Object.assign({}, metadata, {shipments: response.data}));
    } else {
      res.render('error', { message: 'Something went wrong', error: {} });
    }
  } catch (e) {
    res.render('error', { message: e.message, error: { status: response.status } });
  }
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

router.patch('/modifyOrder', async function (req, res, next){
  const status = req.query.status;
  const id = req.query.id;
  const token = req.cookies['token'];
  const auth = 'Bearer ' + token;
  try{
    if(status=="SHIPPED")
      await axios.post('/shipments', {id: id})
    let response = await axios.patch('/orders/'+id+'?status='+status);
    if (response.status==400)
      res.render('error', { message: 'Something went wrong', error: {} });
    res.json({"message": "Successful", "status": status})
  }catch(e){
    res.render('error', { message: 'Something went wrong', error: {} });
  }
});
module.exports = router;

router.get('/pdf', function (req, res, next){
  const id = req.query.id;
  const datetime = req.query.datetime;
  const order_id = req.query.order_id;
  var myDoc = new PDFDocument({bufferPages: true});

let buffers = [];
myDoc.on('data', buffers.push.bind(buffers));
myDoc.on('end', () => {

    let pdfData = Buffer.concat(buffers);
    res.writeHead(200, {
    'Content-Length': Buffer.byteLength(pdfData),
    'Content-Type': 'application/pdf',
    'Content-disposition': 'attachment;filename=DETAILS.pdf',})
    .end(pdfData);

});

myDoc.font('Times-Roman')
     .fontSize(26)
     .text(`SHIPMENT DETAILS`);

myDoc
    .fontSize(15)
    .text(`
    SHIPMENT ID: ${id}\n\n
    ORDER ID: ${order_id}\n\n
    DATETIME: ${datetime}
    `);
myDoc.end();
});
