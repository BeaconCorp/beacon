import React, { PropTypes } from 'react';
import { Input, ButtonInput, Row, Col } from 'react-bootstrap';

const NewBeacon = React.createClass({
  submitBeacon: function (e) {
  },

  titleUpdate: function (e) {
    this.setState({ title: e.target.value });
  },

  descriptionUpdate: function (e) {
    this.setState({ title: e.target.value });
  },

  topicsUpdate: function (e) {
    this.setState({ title: e.target.value });
  },

  render: function () {
    return (
      <form className="new-beacon" onSubmit={this.submitBeacon}>
        <h1>Create New Beacon</h1>
        <Input type="text" onChange={ this.titleUpdate } placeholder="Title" />
        <Input type="textarea" onChange={ this.descriptionUpdate }
          placeholder="Description" />
        <Input type="text" onChange={this.descriptionUpdate }
          placeholder="Topics" />
        <Row>
          <Col xs={6}>
            <ButtonInput type="reset" value="Reset Button" />
          </Col>
          <Col xs={6}>
            <ButtonInput type="submit" value="Submit Button" />
          </Col>
        </Row>
      </form>
    );
  },
});

export default NewBeacon;
