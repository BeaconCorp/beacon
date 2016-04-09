var React = require('react');
var PropTypes = React.PropTypes;

var UserProfile = React.createClass({
  propTypes: {
    username: PropTypes.string.isRequired,
    bio: PropTypes.object.isRequired,
  },

  render: function () {
    return (
      <div>
        <h2>This is UserProfile</h2>
        <p>{this.props.username}</p>
      </div>
    );
  },
});

module.exports = UserProfile;
