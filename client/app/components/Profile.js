var React = require('react');
var Repos = require('./github/Repos');
var UserProfile = require('./github/UserProfile');
var Notes = require('./notes/Notes');

var Profile = React.createClass({
  getInitialState: function () {
    return {
      notes: [1, 2, 3],
      repos: ['a', 'b', 'c'],
      bio: {},
    };
  },

  handleAddNote: function (newNote) {
    // update server

    // update ui
    console.log(this.ref);
    this.ref
      .child(this.props.params.username)
      .child(this.state.notes.length)
      .set(newNote);
  },

  render: function () {
    console.log(this.props);
    return (
        <div className="row">
          <div className="col-md-4">
            <UserProfile
              username={this.props.params.username}
              bio={this.state.bio}/>
          </div>
          <div className="col-md-4">
            <Repos
              username={this.props.params.username}
              repos={this.state.repos}/>
            Repos Component
          </div>
          <div className="col-md-4">
            <Notes
              username={this.props.params.username}
              notes={this.state.notes}
              addNote={this.handleAddNote}/>
            Notes Component
          </div>
      </div>
    );
  },
});

module.exports = Profile;
