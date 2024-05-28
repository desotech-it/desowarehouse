var express = require('express');
var router = express.Router();
var axios = require('axios');
var PDFDocument = require('pdfkit');
var fs = require('fs');
const utils = require('../utils');
const FormData = require('form-data');

router.use(express.urlencoded({ extended: true }));
async function getMetadata(token, title){
  const role = await utils.getUserRole(token);
  if(role=="admin")
    return { title: title, show_labels: false, show_orders: true, show_users: true, change_status: true, role: role};
  else if(role=="warehouse")
    return {title: title, show_labels: true, show_orders: true, show_users: false, change_status: true, role:role}
  else
    return {title: title, show_labels: false, show_orders: false, show_users: false, change_status: false, role: role}
  }

/* GET home page. */
router.get('/', async function (req, res, next) {
  let userData=null;
  let orderData = null;
  let numNotShippedOrders=0;
  let numOrders=0;
  const token = req.cookies['token'];
  const auth = 'Bearer ' + token;
  try{
    let response = await axios.get('auth/me', {headers: {'Authorization': auth}});
    if (response.status === 401) {
      utils.redirectToLogin(res);
      return;
    }
    userData = response.data;
    response = await axios.get(`users/${userData.id}/orders`, {headers: {'Authorization': auth}});
    if (response.status === 401) {
      utils.redirectToLogin(res);
      return;
    }
    orderData = response.data;
    for(let order of orderData){
      numOrders=numOrders+1;
      if(order['status']=="NOT_SHIPPED")
        numNotShippedOrders=numNotShippedOrders+1;
    }
    console.log(orderData);
  }catch(e){
    res.render('error', { message: e.message, error: { status: res.status } });
  }
  utils.userIsLoggedIn(token)
    .then(async (isLoggedIn) => {
      if (isLoggedIn){
        const metadata = await getMetadata(token, "Home");
        res.render('index', Object.assign({}, metadata, {user: userData, numOrders:numOrders, numNotShippedOrders:numNotShippedOrders }));
      }
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
  let user = null;
  //call to get user data
  try{
    response = await axios.get('auth/me', {headers: {'Authorization': auth}});
    if (response.status === 401) {
      utils.redirectToLogin(res);
      return;
    }
    user = response.data;
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
      res.render('allOrders', Object.assign({}, metadata, {orders:response.data, user:user}));
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
  let user = null;
  //call to get user data
  try{
    response = await axios.get('auth/me', {headers: {'Authorization': auth}});
    if (response.status === 401) {
      utils.redirectToLogin(res);
      return;
    }
    user=response.data;
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
      res.render('orders', Object.assign({}, metadata, {orders: response.data, user: user}));
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
  let user = null;
  try {
    response = await utils.getUserInfo(token);
    user=response;
    response = await axios.get('/shipments', { headers: { 'Authorization': auth } });
    if (response.status === 401) {
      utils.redirectToLogin(res);
      return;
    } else if (response.status === 200) {
      const metadata = await getMetadata(token, "Labels");
      res.render('labels', Object.assign({}, metadata, {shipments: response.data, user: user}));
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

router.get('/pdf', async function (req, res, next){
  let user = null;
  const id = req.query.id;
  const datetime = req.query.datetime;
  const order_id = req.query.order_id;
  const token = req.cookies['token'];
  const auth = 'Bearer ' + token;
  try{
    response = await axios.get('/orders/'+order_id, {headers: {'Authorization': auth}});
    if (response.status === 401) {
      utils.redirectToLogin(res);
      return;
    }
    orderData=response.data;
    const userId = orderData.user_id;
    response = await axios.get('/users/'+userId, {headers: {'Authorization': auth}});
    if (response.status === 401) {
      utils.redirectToLogin(res);
      return;
    }
    user=response.data;
  }catch(e){
    res.render('error', { message: e.message, error: { status: response.status } });
  }
  
  var myDoc = new PDFDocument({bufferPages: true, size: [550, 900]});

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
myDoc.image('public/example.png', 0, 0, {fit: [550, 900], align: 'center'});

myDoc
    .fontSize(24)
    .text(`SHIPMENT DETAILS`, 25, 250, {align: "left"})

myDoc
    .fontSize(12)
    .text(`
    Shipment Id: ${id}\n\n
    Order Id: ${order_id}\n\n
    Date: ${datetime.split('T')[0]}\n\n
    Time: ${datetime.split('T')[1]}\n\n
    `, 12, 275, {align: 'left'});

myDoc
    .fontSize(24)
    .text(`SHIP TO`, 175, 250, {align: "right"})

myDoc
    .fontSize(12)
    .text(`
    First Name: ${user.first_name}\n\n
    Last Name: ${user.last_name}\n\n
    Mail: ${user.mail}\n\n
    Birthdate: ${user.birthdate}\n\n
    `,200, 275, {align: 'right'});


myDoc.end();
});
