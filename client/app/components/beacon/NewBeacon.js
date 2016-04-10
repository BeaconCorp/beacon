import React, { PropTypes } from 'react';
import { Input, ButtonInput, Row, Col } from 'react-bootstrap';
import createBeacon from '../../utils/helpers';

const NewBeacon = React.createClass({
  componentDidMount: function () {
    navigator.geolocation.getCurrentPosition((data) => {
      this.setState({
        lat: data.coords.latitude,
        lng: data.coords.longitude,
      });
    });
  },

  submitBeacon: function (e) {
    e.preventDefault();
    console.log('submit beacon');
    createBeacon({
      title: this.state.title,
      description: this.state.description,
      topics: this.state.topics,
      lat: this.state.lat,
      lng: this.state.lng,
    })
    .then((response) => {
      console.log('success', response);
    })
    .catch((response) => {
      console.log('error', response);
    });
  },

  titleUpdate: function (e) {
    this.setState({ title: e.target.value });
  },

  descriptionUpdate: function (e) {
    this.setState({ description: e.target.value });
  },

  topicsUpdate: function (e) {
    this.setState({ topics: e.target.value });
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
