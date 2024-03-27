const axios = require('axios');

async function userIsLoggedIn(token) {
	const response = await axios.get('/auth/me', {
		headers: { Authorization: 'Bearer ' + token },
		validateStatus: (status) => status >= 200 && status <= 499,
	});
	return response.status === 200;
}

module.exports = {
	userIsLoggedIn
};
