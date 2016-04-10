import React from 'react';
import { Route, IndexRoute } from 'react-router';
import Main from '../components/Main';
import MapPage from '../components/MapPage';
import GroupsPage from '../components/GroupsPage';
import ProfilePage from '../components/ProfilePage';
import SettingsPage from '../components/SettingsPage';

module.exports = (
  <Route path="/" component={Main}>
    <IndexRoute component={MapPage} />
    <Route path="group" component={GroupsPage}></Route>
    <Route path="profile" component={ProfilePage}></Route>
    <Route path="settings" component={SettingsPage}></Route>
  </Route>
);
