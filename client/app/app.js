import React from 'react';
import ReactDOM from 'react-dom';
import { Router } from 'react-router';
import routes from './config/routes';
import { hashHistory } from 'react-router';

function start() {
  console.log('start');
  ReactDOM.render(
    <Router history={hashHistory}>{routes}</Router>,
    document.getElementById('app')
  );
}

start();
document.addEventListener('deviceready', start, false);
