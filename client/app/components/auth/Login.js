import React from 'react';
import {Row, Col, Input, Button} from 'react-bootstrap';

import auth from './helpers';

const Login = React.createClass({

  contextTypes: {
    router: React.PropTypes.object.isRequired,
  },

  getInitialState() {
    return {
      error: false,
    };
  },

  handleSubmit(event) {
    event.preventDefault();

    const email = this.refs.email.refs.input.value;
    const pass = this.refs.pass.refs.input.value;
    console.log('info', email, pass, this.refs);

    auth.login(email, pass, (loggedIn) => {
      if (!loggedIn)
        return this.setState({ error: true });

      const { location } = this.props;

      if (location.state && location.state.nextPathname) {
        this.context.router.replace(location.state.nextPathname);
      } else {
        this.context.router.replace('/');
      }
    });
  },

  render() {
    return (
      <form onSubmit={this.handleSubmit} className="container login">
        <Row>
          <Col xs={12}>
            <Input type="text" ref="email" bsSize="large" placeholder="Username" />
            <Input type="password" ref="pass" bsSize="large" placeholder="Password" />

            <Button type="submit" bsSize="large" block>Login</Button>
          </Col>
          {this.state.error && (
            <p>Bad login information</p>
          )}
        </Row>
      </form>
    );
  },
});

export default Login;
