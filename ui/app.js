var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');

const axios = require('axios');

var app = express();

// bootstrap paths
app.use('/stylesheets', express.static(path.join(__dirname, 'node_modules/bootstrap/dist/css')))
app.use('/stylesheets', express.static(path.join(__dirname, 'node_modules/@fortawesome/fontawesome-free/css')))
app.use('/stylesheets', express.static(path.join(__dirname, 'node_modules/startbootstrap-sb-admin-2/css')))

app.use('/javascripts', express.static(path.join(__dirname, 'node_modules/bootstrap/dist/js')))
app.use('/javascripts', express.static(path.join(__dirname, 'node_modules/jquery/dist')))
app.use('/javascripts', express.static(path.join(__dirname, 'node_modules/jquery.easing')))
app.use('/javascripts', express.static(path.join(__dirname, 'node_modules/startbootstrap-sb-admin-2/js')))

app.use('/fonts', express.static(path.join(__dirname, 'node_modules/@fontsource')))
app.use('/webfonts', express.static(path.join(__dirname, 'node_modules/@fortawesome/fontawesome-free/webfonts')))

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', indexRouter);
app.use('/users', usersRouter);

// catch 404 and forward to error handler
app.use(function (req, res, next) {
  next(createError(404));
});

// error handler
app.use(function (err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

axios.defaults.baseURL = process.env.API_URL;
axios.defaults.validateStatus = status => status >= 200 && status <= 499;

module.exports = app;
