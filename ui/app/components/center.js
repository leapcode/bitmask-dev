//
// puts a block right in the center of the window
//

import React from 'react'
import PropTypes from 'prop-types'

const Center = props => (
  <div className={"center-container center-" + props.direction}>
    <div className="center-item" style={props.width ? {width: props.width + 'px'} : null}>
      {props.children}
    </div>
  </div>
)

Center.defaultProps = {
  width: null,
  direction: 'both'
}

Center.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.element,
    PropTypes.arrayOf(
      PropTypes.element
    )
  ])
}

export default Center
