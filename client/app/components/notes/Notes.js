var AddNote = require('./AddNote');
var NotesList = require('./NotesList');
var React = require('react');
var PropTypes = React.PropTypes;

var Notes = React.createClass({
  propTypes: {
    username: PropTypes.string.isRequired,
    notes: PropTypes.array.isRequired,
    addNote: PropTypes.func.isRequired,
  },

  render: function () {
    return (
      <div>
        <h2>Notes</h2>
        <AddNote
          username={this.props.username}
          addNote={this.props.addNote}/>
        <NotesList notes={this.props.notes} />
      </div>
    );
  },
});

module.exports = Notes;
