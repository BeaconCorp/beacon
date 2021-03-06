import React from 'react';
import { Link } from 'react-router';
import { Map, Marker, Popup, TileLayer } from 'react-leaflet';

import { getAllBeacons } from '../utils/helpers';

var MapPage = React.createClass({
  getInitialState: () => {
    console.log('MapPage.getInitialState()');
    return {
      beacons: [],
    };
  },

  componentDidMount: function () {
    console.log('MapPage.componentDidMount()');
    navigator.geolocation.getCurrentPosition((data) => {
      getAllBeacons(data.coords.latitude, data.coords.longitude)
      .then((response) => {
        console.log('MapPage.componentDidMount(), got location successfully.',
          response);
        this.setState({ beacons: response.data });
        this.renderBeacons();
      });
    });
  },

  renderBeacons: function () {
    console.log('MapPage.renderBeacons()', this.state.beacons);
    let beacons = this.state.beacons.map((beacon, index) => {
      let position = [beacon.lat, beacon.lng];
      return (
        <Marker position={position} key={index}>
          <Popup>
            <div>
              <h3>{beacon.title}</h3>
              <p>{beacon.description}</p>
              <p>{beacon.topics}</p>
            </div>
          </Popup>
        </Marker>
      );
    });
    return beacons;
  },

  render: function () {
    const position = [43.044591, -76.150566]; // tech garden
    const mapStyle = { height: '100%' };
    return (
      <div className="map">
        <Map center={position} zoom={12} style={mapStyle}>
          <TileLayer
            url='http://{s}.tile.osm.org/{z}/{x}/{y}.png'
            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          />
        { this.renderBeacons() }
        </Map>
        <Link to='new-beacon' className="btn btn-primary btn-fab add-beacon">
          <i className="material-icons">+</i>
        </Link>
      </div>
    );
  },
});

module.exports = MapPage;
