import React from 'react';
import { Navbar, Nav, NavItem, NavDropdown, MenuItem } from 'react-bootstrap';

var Main = React.createClass({
  render: function () {
    const formStyle = { margin: '10px 0' };
    return (
      <div className="main-container full-height">
        <Navbar default>
          <Navbar.Header>
            <Navbar.Brand>
              <a href="#">Beacon</a>
            </Navbar.Brand>
            <Navbar.Toggle />
          </Navbar.Header>
          <Navbar.Collapse>
            <Nav>
              <form className="navbar-form navbar-right" style={formStyle}>
                <div className="form-group">
                  <input className="form-control col-md-8" placeholder="Search" type="text"/>
                </div>
              </form>
            </Nav>
            <Nav pullRight>
              <NavItem eventKey={1} href="#/group">Group</NavItem>
              <NavItem eventKey={2} href="#/profile">Profile</NavItem>
              <NavItem eventKey={3} href="#/settings">Settings</NavItem>
            </Nav>
          </Navbar.Collapse>
        </Navbar>
        {this.props.children}
      </div>
    );
  },
});

module.exports = Main;
