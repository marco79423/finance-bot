import React from 'react'
import {useRouter} from 'next/router'
import {useTranslation} from 'next-i18next'
import {DateTime} from 'luxon'
import {css, useTheme} from '@emotion/react'
import {Typography} from '@mui/material'

import {ProcessStatus} from '../../../constants'
import delay from '../../../utils/delay'
import transformTimestampToDate from './transformTimestampToDate'
import ProcessStatusInfo from '../../../components/modules/ProcessStatusInfo'
import TextField from '../../../components/elements/TextField'
import Button from '../../../components/elements/Button'
import Paper from '../../../components/elements/Paper'
import TimeUnitSelect from './TimeUnitSelect'
import TimeTable from './TimeTable'
import {useAppCtx} from '../../../contexts/appCtx'
import InputResultPanelToolLayout from '../../../components/layouts/InputResultPanelToolLayout'


export default function TWStockAnalysis() {
  const theme = useTheme()
  const styles = {
    // panel
    content: css`
      background: ${theme.palette.surface.main};

      padding: 16px;

      @media (max-width: ${theme.breakpoints.sm}px) {
        padding: 16px;
      }
    `,

    description: css`
      margin-bottom: 8px;
    `,

    textField: css`
      max-width: 500px;
    `,

    button: css`
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
    `,

    hint: css`
      margin-top: 8px;
      font-size: 0.9em;
    `,

    processStatus: css`
      position: absolute;
      top: 8px;
      right: 8px;
    `,

    timeTableList: css`
      margin-top: 16px;

      display: flex;
      flex-direction: column;
      gap: 12px;
    `,
  }

  const appCtx = useAppCtx()
  const {t} = useTranslation()

  const router = useRouter()
  const locale = router.locale

  const {timestamp: defaultTimestamp, timestampUnit: defaultTimestampUnit, isoTime: defaultISOTime} = appCtx.defaultData

  const [checkTime, setCheckTime] = React.useState(DateTime.fromISO(defaultISOTime))
  const [processStatus, setProcessStatus] = React.useState(ProcessStatus.Idle)
  const [timestampUnit, setTimestampUnit] = React.useState(defaultTimestampUnit)
  const [targetDateTime, setTargetDateTime] = React.useState(DateTime.fromISO(defaultISOTime))
  const [errorMessage, setErrorMessage] = React.useState('')

  const [textInput, setTextInput] = React.useState(defaultTimestamp)
  const onTextInputChange = (textInput) => {
    setTextInput(textInput)
  }

  const onCurrentSelectionChange = async (value) => {
    const [targetDateTime, timestampUnit] = transformTimestampToDate(textInput, {unit: value})
    setTargetDateTime(targetDateTime)
    setTimestampUnit(timestampUnit)
  }

  const onButtonClicked = async () => {
    setProcessStatus(ProcessStatus.Processing)
    await delay(500)
    try {
      const [targetDateTime, timestampUnit] = transformTimestampToDate(textInput)
      setCheckTime(DateTime.now())
      setTargetDateTime(targetDateTime)
      setTimestampUnit(timestampUnit)
      setProcessStatus(ProcessStatus.Success)
    } catch (e) {
      setTimestampUnit('seconds')
      setProcessStatus(ProcessStatus.Failed)
      setErrorMessage('error-hint')
    }
  }

  const localTimeStr = React.useMemo(() => targetDateTime ? targetDateTime.toLocaleString(DateTime.DATETIME_FULL, {locale}) : '', [targetDateTime, locale])
  const localTimeISOStr = React.useMemo(() => targetDateTime ? targetDateTime.toISO() : '', [targetDateTime])
  const localTimeRFC2882Str = React.useMemo(() => targetDateTime ? targetDateTime.toRFC2822() : '', [targetDateTime])

  const utcTimeStr = React.useMemo(() => targetDateTime ? targetDateTime.toUTC().toLocaleString(DateTime.DATETIME_FULL, {locale}) : '', [targetDateTime, locale])
  const utcTimeISOStr = React.useMemo(() => targetDateTime ? targetDateTime.toUTC().toISO() : '', [targetDateTime])
  const utcTimeRFC2882Str = React.useMemo(() => targetDateTime ? targetDateTime.toUTC().toRFC2822() : '', [targetDateTime])

  const relativeTimeStr = React.useMemo(() => targetDateTime ? targetDateTime.diff(checkTime, undefined, {locale}).toHuman(locale) : '', [checkTime, targetDateTime, locale])
  const relativeDaysStr = React.useMemo(() => targetDateTime ? targetDateTime.diff(checkTime, 'days', {locale}).toHuman(locale) : '', [checkTime, targetDateTime])
  const relativeMinutesStr = React.useMemo(() => targetDateTime ? targetDateTime.diff(checkTime, 'minutes', {locale}).toHuman(locale) : '', [checkTime, targetDateTime])

  return (
    <InputResultPanelToolLayout
      inputContent={(
        <Paper css={styles.content}>
          <div>
            <Typography css={styles.description}>{t('timestamp-converter.input-box-description')}</Typography>

            <TextField
              placeholder={t('timestamp-converter.Timestamp')}
              value={textInput}
              onChange={onTextInputChange}

              css={styles.textField}
              action={
                <Button
                  css={styles.button}
                  onClick={onButtonClicked}
                >{t('timestamp-converter.transform-button')}</Button>
              }
            />

            <Typography
              css={styles.hint}
              dangerouslySetInnerHTML={
                {__html: t('timestamp-converter.input-hint', {interpolation: {escapeValue: false}})}
              }/>
          </div>
        </Paper>
      )}
      inputBottom={(
        appCtx.isMobile ? (
          <div css={css`
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
          `}>
            <ProcessStatusInfo id="process-status" enableProgressing processStatus={processStatus}/>
          </div>
        ) : (
          <div/>
        )
      )}

      resultContent={(
        <Paper css={styles.content}>
          <ProcessStatusInfo css={styles.processStatus} enableProgressing processStatus={processStatus}/>

          {processStatus !== ProcessStatus.Failed ? (
            <>
              <div css={{display: 'flex', alignItems: 'center'}}>
                <Typography>{t('timestamp-converter.assume-description')}</Typography>
                <TimeUnitSelect
                  css={{marginLeft: 8}}
                  timeUnit={timestampUnit}
                  onTimeUnitChange={onCurrentSelectionChange}
                />
              </div>
              <div css={styles.timeTableList}>
                <TimeTable rows={[
                  {label: t('timestamp-converter.your-time-zone-title'), value: localTimeStr},
                  {label: 'ISO 8601', value: localTimeISOStr},
                  {label: 'RFC 2822', value: localTimeRFC2882Str},
                ]}/>

                <TimeTable rows={[
                  {label: 'UTC', value: utcTimeStr},
                  {label: 'ISO 8601', value: utcTimeISOStr},
                  {label: 'RFC 2822', value: utcTimeRFC2882Str},
                ]}/>

                <TimeTable rows={[
                  {label: t('timestamp-converter.relative-time-title'), value: relativeTimeStr},
                  {label: t('timestamp-converter.time-unit-days'), value: relativeDaysStr},
                  {label: t('timestamp-converter.time-unit-minutes'), value: relativeMinutesStr},
                ]}/>
              </div>
            </>
          ) : (
            <Typography>{tt(errorMessage)}</Typography>
          )}
        </Paper>
      )}
    />
  )
}
