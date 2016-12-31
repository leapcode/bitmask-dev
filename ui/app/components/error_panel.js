import React from 'react'
import Center from './center'
import Area from './area'
import { Modal } from 'react-bootstrap'

import App from 'app'

class ErrorMessage extends React.Component {
  static get defaultProps() {return{
    message: null,
    stack: null
  }}

  constructor(props) {
    super(props)
  }

  render() {
    let stack = null
    if (this.props.stack) {
      stack = <ul>
        {this.props.stack.split("\n").slice(0,10).map(i =>
          <li>{i}</li>
        )}
      </ul>
    }
    return(
      <div>
        <p>{this.props.message}</p>
        {stack}
      </div>
    )
  }
}

export default class ErrorPanel extends React.Component {

  constructor(props) {
    super(props)
  }

  hide() {
    App.hideError()
  }

  render () {
    var error_msg = null
    var error = this.props.error

    console.log(error)

    if (error.error) {
      error = error
    } else if (error.reason) {
      error = error.reason
    }

    if (error.stack && error.message) {
      error_msg = <ErrorMessage message={error.message} stack={error.stack} />
    } else if (error.message) {
      error_msg = <ErrorMessage message={error.message} />
    } else {
      error_msg = <ErrorMessage message={error.toString()} />
    }

    return (
      <Modal show={true} onHide={this.hide.bind(this)}>
        <Modal.Header closeButton>
          <Modal.Title>Error</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {error_msg}
        </Modal.Body>
      </Modal>
    )
  }
}
