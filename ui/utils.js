const axios = require('axios');

async function userIsLoggedIn(token) {
	const response = await axios.get('/auth/me', { headers: { Authorization: 'Bearer ' + token } });
	return response.status === 200;
}

function redirectToLogin(res) {
	res.redirect('/login');
}

module.exports = {
	userIsLoggedIn,
	redirectToLogin,
};
