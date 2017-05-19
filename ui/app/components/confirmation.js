//
// A simple diagon that asks if you are sure.
//

import React from 'react'
import {Button, ButtonToolbar, Modal} from 'react-bootstrap'
import PropTypes from 'prop-types'

const Confirmation = props => (
  <Modal>
    <Modal.Header closeButton>
      <Modal.Title>
        {props.title}
      </Modal.Title>
    </Modal.Header>
    <Modal.Body>
      <ButtonToolbar>
        <Button onClick={props.onAccept} bsStyle="success">
          {props.acceptStr}
        </Button>
        <Button onClick={props.onCancel}>
          {props.cancelStr}
        </Button>
      </ButtonToolbar>
    </Modal.Body>
  </Modal>
)

Confirmation.defaultProps = {
  title: "Are you sure?",
  onCancel: null,
  onAccept: null,
  acceptStr: 'Accept',
  cancelStr: 'Cancel'
}

Confirmation.propTypes = {
  className: PropTypes.string,
  onCancel: PropTypes.func.isRequired,
  onAccept: PropTypes.func.isRequired,
  acceptStr: PropTypes.string,
  cancelStr:  PropTypes.string
}

export default Confirmation
