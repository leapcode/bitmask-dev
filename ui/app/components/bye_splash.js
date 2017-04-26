/*
 * a parting window
 */

import React from 'react'
import Center from 'components/center'
import bitmask from 'lib/bitmask'

export default class ByeSplash extends React.Component {

  static get defaultProps() {return{
    delay: 1000
  }}

  constructor(props) {
    super(props)
    this.state = {
      errorMessage: null,
      readyToQuit: false
    }
    this.tick = this.tick.bind(this)
  }

  componentDidMount() {
    this.interval = setInterval(this.tick, this.props.delay)
    bitmask.core.stop().then(msg => {
      console.log(msg)
      this.setState({readyToQuit: true})
    }, error => {
      console.log(error)
      this.setState({errorMessage: error})
    })
  }

  componentWillUnmount() {
    clearInterval(this.interval)
  }

  tick() {
    if (this.state.readyToQuit) {
      if (typeof(bitmaskApp) == 'undefined') {
        window.close()
      } else {
        bitmaskApp.shutdown()
      }
    } else {
      clearInterval(this.interval)
      this.interval = setInterval(this.tick, 200)
    }
  }

  render () {
    let message = null
    let messageClass = "ok"
    if (this.state.errorMessage) {
      messageClass = "error"
      message = this.state.errorMessage
    }

    let backgroundStyle = {
      position: "absolute",
      width: "100%",
      height: "100%",
      backgroundColor: "#333"
    }
    let foregroundStyle = {
      marginTop: "10px",
      color: "#999",
      textAlign: "center"
    }
    let style = `
      .mask, .ok {
        animation: fadeout 2s infinite ease-in-out;
        -webkit-animation: fadeout 2s infinite ease-in-out;
      }
      @keyframes fadeout {
        0% {opacity: 1}
        50% {opacity: 0}
        100% {opacity: 1}
      }
      @-webkit-keyframes fadeout {
        0% {opacity: 1}
        50% {opacity: 0}
        100% {opacity: 1}
      }
    `
    return (
      <div style={backgroundStyle}>
        <style>{style}</style>
        <Center>
          <img className="mask" src='img/mask.svg' width='200px' />
          <div className={messageClass} style={foregroundStyle}>
            {message}
          </div>
        </Center>
      </div>
    )
  }
}