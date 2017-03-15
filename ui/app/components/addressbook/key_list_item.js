//
// A key in the list of keys
//

import React from 'react'
import { Glyphicon, Button, ButtonToolbar, Label } from 'react-bootstrap'
import bitmask from 'lib/bitmask'

export default class KeyListItem extends React.Component {

  static get defaultProps() {return{
    data: null,             // the key as an Object 
    account: null           // the account as an Account
  }}

  constructor(props) {
    super(props)
    this.state = {
      expanded: false,
      hidden: false,
      deleting: false,
      error: null
    }
    this.toggle = this.toggle.bind(this)
    this.delete = this.delete.bind(this)
  }

  toggle() {
    this.setState({expanded: !this.state.expanded})
  }

  delete() {
    if (this.props.account.address == this.props.data.address) {
      return  // please do not delete your own key
    }

    bitmask.keys.del(this.props.account.id, this.props.data.address, false).then(
      key => {
        this.setState({hidden: true})
      },
      error => {
        this.setState({error: error})
      }
    )
  }

  render() {
    if (this.state.hidden) {
      return <div></div>
    } else if (!this.props.data) {
      return (
        <div className="key-list-item">
          NO KEY
        </div>
      )
    }

    let details = null
    let expander = null
    let alert = null
    let deleteButton = null
    let labelArray = []
    let labels = null
    let glyph = this.state.expanded ? 'triangle-bottom' : 'triangle-right'

    if (this.state.error) {
      alert = (
        <Alert bsStyle="danger">{this.state.error}</Alert>
      )
    }

    if (this.props.account.address != this.props.data.address) {
      deleteButton = <Button onClick={this.delete}>Delete</Button>
    } else {
      labelArray.push(<Label key="owner" bsStyle="primary">Mine</Label>)
      labelArray.push(<Label key="level" bsStyle="success">Verified</Label>)
    }

    if (!this.props.data.encr_used) {
      labelArray.push(<Label key="used" bsStyle="default">Never Used</Label>)
    }

    if (this.state.expanded) {
      details = (
        <div className="details">
          {alert}
          Security Identifier: {this.props.data.fingerprint}<br />
          Last Updated: {this.props.data.refreshed_at}<br />
          Expires On: {this.props.data.expiry_date}<br />
          <ButtonToolbar>
            <Button onClick={this.toggle}>Close</Button>
            {deleteButton}
          </ButtonToolbar>
        </div>
      )
    }

    expander = (
      <div className="expander">
        <Glyphicon glyph={glyph} />
      </div>
    )

    return (
      <div className="key-list-item">
        <div className="top-row clickable" onClick={this.toggle} >
          <div className="labels pull-right">
            {labelArray}
          </div>
          {expander}
          <div className="address">
            {this.props.data.address}
          </div>
        </div>
        {details}
      </div>
    )
  }
}
