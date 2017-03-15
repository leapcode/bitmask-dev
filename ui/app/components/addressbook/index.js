//
// Interface to the key manager
//

import React from 'react'
import App from 'app'
import { Button, Glyphicon, Alert } from 'react-bootstrap'

import {VerticalLayout, Row} from 'components/layout'
import Spinner from 'components/spinner'
import KeyListItem from './key_list_item'
import './addressbook.less'
import bitmask from 'lib/bitmask'

export default class Addressbook extends React.Component {

  static get defaultProps() {return{
    account: null
  }}

  constructor(props) {
    super(props)
    this.state = {
      keys: null,
      loading: true,
      errorMsg: ""
    }
    this.close = this.close.bind(this)
  }

  componentWillMount() {
    bitmask.keys.list(this.props.account.id, false).then(keys => {
      this.setState({keys: keys, loading: false})
    }, error => {
      this.setState({keys: null, loading: false, errorMsg: error})
    })
  }

  close() {
    App.show('main', {initialAccount: this.props.account})
  }

  render() {
    let alert = null
    let keyList = null
    let spinner = null

    if (this.state.loading) {
      spinner = <Spinner />
    }

    if (this.state.errorMsg) {
      alert = (
        <Alert bsStyle="danger">{this.state.errorMsg}</Alert>
      )
    }

    if (this.state.keys) {
      keyList = this.state.keys.map((theKey, i) => {
        return <KeyListItem key={i} data={theKey} account={this.props.account} />
      })
    }

    let buttons = (
      <Button onClick={this.close} className="btn-inverse">
        <Glyphicon glyph="menu-left" />&nbsp;
        Close
      </Button>
    )

    let page = (
      <VerticalLayout className="darkBg">
        <Row className="header" size="shrink" gutter="8px">
          <div className="pull-left">
            {buttons}
          </div>
          <div className="title">
            {this.props.account.address} / Addressbook
          </div>
        </Row>
        <Row className="lightFg" size="expand">
          {alert}
          {spinner}
          <div className="key-list">
            {keyList}
          </div>
        </Row>
      </VerticalLayout>
    )
    return page
  }

}
