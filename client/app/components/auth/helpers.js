import axios from 'axios';
import sha256 from 'js-sha256';

module.exports = {
  login(email, pass, cb) {
    console.log(pass);
    let hash = sha256(pass);
    $.ajax({
      url: 'http://localhost:6543/api/users/login',
      type: 'POST',
      data: JSON.stringify({
        email: email,
        password: hash,
      }),
    })
    .success((response) => {
      console.log(response);
      cb(true);
    })
    .error((response) => {
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
