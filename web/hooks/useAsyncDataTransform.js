import React from 'react'
import {ProcessStatus} from '../constants'
import delay from '../utils/delay'


export const DefaultOptions = {
  defaultOutput: '',
  delayTime: 500,
  skipEmpty: true
}

export default function useAsyncDataTransform(input, transform, options = {}) {
  const {defaultOutput, delayTime, skipEmpty} = {...DefaultOptions, ...options}

  const [output, setOutput] = React.useState(defaultOutput)
  const [processStatus, setProcessStatus] = React.useState(ProcessStatus.Idle)

  React.useEffect(() => {
    let isSubscribed = true
    if (!skipEmpty || input) {
      setProcessStatus(ProcessStatus.Processing)
      Promise.resolve()
        .then(() => delay(delayTime))
        .then(() => transform(input))
        .then(output => {
          if (isSubscribed) {
            setOutput(output)
            setProcessStatus(ProcessStatus.Success)
          }
        })
        .catch(error => {
          if (isSubscribed) {
            setOutput(error)
            setProcessStatus(ProcessStatus.Failed)
          }
        })
    }

    return () => {
      isSubscribed = false
    }
  }, [input, transform, delayTime])

  return [processStatus, output]
}