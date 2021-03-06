import axios from 'axios';
import sha256 from 'js-sha256';

module.exports = {
  login(email, pass, cb) {
    console.log(pass);
    let hash = sha256(pass);
    axios.post('http://raisethebeacon.com/api/users/login', {
      email: email,
      password: hash,
    })
    .then((response) => {
      console.log(response);
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', response.data);
      cb(true);
    })
    .catch((response) => {
      console.log(response);
      cb(false);
    });
  },

  getToken() {
    return localStorage.token;
  },

  logout(cb) {
    delete localStorage.token;
    if (cb) cb();
    this.onChange(false);
  },

  loggedIn() {
    return !!localStorage.token;
  },

  onChange() {},
};
