import React, { PropTypes } from 'react';
import { Input, ButtonInput, Row, Col } from 'react-bootstrap';
import { Notification } from 'react-notification';
import { Form } from 'formsy-react';

import createBeacon from '../../utils/helpers';

const NewBeacon = React.createClass({
  componentDidMount: function () {
    console.log('NewBeacon.componentDidMount()');
    navigator.geolocation.getCurrentPosition((data) => {
      this.setState({
        lat: data.coords.latitude,
        lng: data.coords.longitude,
      });
    });
    /*this.setState({
      isActive: false,
    });*/
  },

  submitBeacon: function (e) {
    e.preventDefault();
    console.log('NewBeacon.submitBeacon()');
    var options = {
      title: this.state.title,
      description: 'WHAT!?', //this.state.description,
      topics: this.state.topics,
      lat: this.state.lat,
      lng: this.state.lng,
    };
    createBeacon(
      options
    )
    .then((response) => {
      console.log('success', response);
      this.toggleNotification("Your beacon has been lit!");
    })
    .catch((response) => {
      console.log('error', response);
      this.toggleNotification("Yikes, there was an error");
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

  toggleNotification: function(message) {
    console.log('NewBeacon.toggleNotification()');
    this.setState({
      isActive: !this.state.isActive,
      notification_message: message,
    })
  },

  render: function () {

    console.log('NewBeacon.render()');

    //const { isActive } = this.state;

    /*this.setState({
      isActive: false,
    });*/

    console.log(this.state);

    return (
      <div>
        <form className="new-beacon" onSubmit={this.submitBeacon}>
          <h1>Create New Beacon</h1>
          <Input type="text" onChange={ this.titleUpdate } placeholder="Title" 
            required/>
          <Input type="textarea" onChange={ this.descriptionUpdate }
            placeholder="Description" required/>
          <Input type="text" onChange={this.topicsUpdate }
            placeholder="Topics" required/>
          <Row>
            <Col xs={6}>
              <ButtonInput type="reset" value="Reset Button" />
            </Col>
            <Col xs={6}>
              <ButtonInput type="submit" value="Submit Button" />
            </Col>
          </Row>
        </form>
        <Notification
          isActive={this.state == null ? false : this.state.isActive}
          message={this.state == null ? '' : this.state.notification_message}
          action="Dismiss"
          onDismiss={this.toggleNotification}
          onClick={() =>  this.setState({ isActive: false })}
        /> 
      </div>
    );
  },
});

export default NewBeacon;
