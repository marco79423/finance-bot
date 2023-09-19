import React from 'react'
import {useTranslation} from 'next-i18next'

import Select from '../../../components/elements/Select'

export default function TimeUnitSelect({
                                         timeUnit = 'seconds',
                                         onTimeUnitChange,
                                         ...props
                                       }) {
  const {t} = useTranslation()

  const timeUnitSelections = React.useMemo(() => [
    {key: 'seconds', value: 'seconds', label: t('timestamp-converter.time-unit-seconds')},
    {key: 'milliseconds', value: 'milliseconds', label: t('timestamp-converter.time-unit-milliseconds')},
    {key: 'microseconds', value: 'microseconds', label: t('timestamp-converter.time-unit-microseconds')},
    {key: 'nanoseconds', value: 'nanoseconds', label: t('timestamp-converter.time-unit-nanoseconds')},
  ], [t])

  return (
    <Select
      currentValue={timeUnit}
      selections={timeUnitSelections}
      onSelectionChange={onTimeUnitChange}

      {...props}
    />
  )
}
