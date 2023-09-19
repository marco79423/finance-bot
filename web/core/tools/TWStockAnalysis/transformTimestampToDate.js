import {DateTime} from 'luxon'

export default function transformTimestampToDate(input, {unit} = {}) {
  let timestamp = +input
  if (isNaN(timestamp)) {
    throw new Error('Expected a number.')
  }

  let timestampUnit = ''
  if (unit === 'nanoseconds' || ((timestamp >= 1E16) || (timestamp <= -1E16))) {
    timestampUnit = 'nanoseconds'
    timestamp = Math.floor(input / 1000000)
  } else if (unit === 'microseconds' || ((timestamp >= 1E14) || (timestamp <= -1E14))) {
    timestampUnit = 'microseconds'
    timestamp = Math.floor(timestamp / 1000)
  } else if (unit === 'milliseconds' || ((timestamp >= 1E11) || (timestamp <= -3E10))) {
    timestampUnit = 'milliseconds'
  } else {
    timestampUnit = 'seconds'
    timestamp = (timestamp * 1000)
  }

  return [DateTime.fromMillis(timestamp), timestampUnit]
}
