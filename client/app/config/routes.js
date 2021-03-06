import React from 'react';
import { Route, IndexRoute } from 'react-router';
import Main from '../components/Main';

import MapPage from '../components/MapPage';
import GroupsPage from '../components/GroupsPage';
import ProfilePage from '../components/ProfilePage';
import SettingsPage from '../components/SettingsPage';
import NewBeacon from '../components/beacon/NewBeacon';
import Login from '../components/auth/Login';

import auth from '../components/auth/helpers';

function requireAuth(nextState, replace) {
  console.log('requireAuth', auth.loggedIn);
  if (!auth.loggedIn()) {
    replace({
      pathname: '/login',
      state: { nextPathname: nextState.location.pathname },
    });
  }
}

module.exports = (
  <Route path="/" component={Main}>
    <IndexRoute component={MapPage} onEnter={requireAuth} />
    <Route path="group" component={GroupsPage} onEnter={requireAuth}></Route>
    <Route path="profile" component={ProfilePage} onEnter={requireAuth}></Route>
    <Route path="settings" component={SettingsPage} onEnter={requireAuth}></Route>
    <Route path="new-beacon" component={NewBeacon} onEnter={requireAuth}></Route>
    <Route path="login" component={Login}></Route>
  </Route>
);
