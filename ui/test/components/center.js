import React from 'react';
import {shallow} from 'enzyme';
import chaiEnzyme from 'chai-enzyme'
import chai, { expect } from 'chai'
import Center from '../../app/components/center';


describe('Center Component', () => {

  chai.use(chaiEnzyme())

  it('has reasonable defaults', () => {
    const center = shallow(
      <Center>
        test
      </Center>
    )

    expect(center.hasClass("center-both"))

    expect(center.find(".center-item")).to.not.have.style('width')
  })

  it('has a width parameter on the inner div', () => {
    const center = shallow(
      <Center width="10">
        test
      </Center>
    )

    expect(center.find(".center-item")).to.have.style('width').equal('10px')
  })

  it('sets direction parameter in the class name', () => {
    const center = shallow(
      <Center direction="vertically">
        test
      </Center>
    )

    expect(center).to.have.className("center-vertically")
  })
})
