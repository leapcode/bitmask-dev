import React from 'react'
import { Button, Glyphicon, Alert, ButtonToolbar } from 'react-bootstrap'

import SectionLayout from './section_layout'
import IMAPButton from './imap_button'

import Account from 'models/account'
import Spinner from 'components/spinner'
import bitmask from 'lib/bitmask'
import App from 'app'

export default class EmailSection extends React.Component {

  static get defaultProps() {return{
    account: null
  }}

  constructor(props) {
    super(props)
    this.state = {
      status: 'unknown', // API produces: on, off, starting, stopping, failed
      keys: null,        // API produces: null, sync, generating, found
      message: null,
      expanded: false
    }
    this.expand       = this.expand.bind(this)
    this.openKeys     = this.openKeys.bind(this)
    this.updateStatus = this.updateStatus.bind(this)
  }

  componentWillMount() {
    this.updateStatus(this.props.account.address)
    bitmask.events.register("MAIL_STATUS_CHANGED", 'email section update', this.updateStatus)
  }

  componentWillUnmount() {
    bitmask.events.unregister("MAIL_STATUS_CHANGED", 'email section update', this.updateStatus)
  }

  updateStatus(address) {
    bitmask.mail.status(this.props.account.id).then(
      status => {
        console.log("STATUS CHANGED", status)
        this.setState({
          keys: status.keys,
          status: status.status,
          error: status.error
        })
      },
      error => {
        this.setState({
          error: error,
          status: "error"
        })
      }
    )
  }

  openKeys() {
    App.show('addressbook', {account: this.props.account})
  }

  openPixelated() {
    if(typeof bitmaskBrowser !== 'undefined') {
      // we are inside a qtwebkit page that exports the object
      bitmaskBrowser.openPixelated();
    } else {
      window.open("http://localhost:9090");
    }
  }

  expand() {
    this.setState({expanded: !this.state.expanded})
  }

  render () {
    let message = null
    let keyMessage = null
    let expanded = this.state.expanded

    if (this.state.error) {
      // style may be: success, warning, danger, info
      message = (
        <Alert bsStyle="danger">{this.state.error}</Alert>
      )
      expanded = true
    }
    if (this.state.keys) {
      if (this.state.keys == "sync") {
        keyMessage = <Alert bsStyle="info">Downloading identity files</Alert>
        expanded = true
      } else if (this.state.keys == "generating") {
        keyMessage = <Alert bsStyle="info">Preparing your identity (this may take a long time)</Alert>
        expanded = true
      }
    }
    let addyButton = <Button disabled={this.state.status != 'on'} onClick={this.openKeys}>Addressbook</Button>
    let mailButton = <Button disabled={this.state.status != 'on'} onClick={this.openPixelated}>Open Mail</Button>
    let imapButton = <IMAPButton account={this.props.account} />
    let body = null
    let header = <h1>Mail</h1>

    if (this.state.status == 'disabled') {
      header = <h1>Mail Disabled</h1>
    }
    if (expanded || keyMessage || message) {
      body = (<div>
        {message}
        {keyMessage}
        <ButtonToolbar>
          {addyButton}
          {imapButton}
        </ButtonToolbar>
      </div>)
    }
    return (
      <SectionLayout icon="envelope" status={this.state.status}
        onExpand={this.expand} buttons={mailButton} header={header} body={body} />
    )
  }
}
