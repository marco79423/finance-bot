import React from 'react'
import dynamic from 'next/dynamic'
import {useTranslation} from 'next-i18next'
import {IconButton, Table, TableCell, TableRow} from '@mui/material'
import {css, useTheme} from '@emotion/react'
import SettingsIcon from '@mui/icons-material/Settings'
import QuestionMarkIcon from '@mui/icons-material/QuestionMark'

import LocaleSelect from '../LocaleSelect'
import DarkModeToggle from '../DarkModeToggle'
import BasicDialog from '../../elements/BasicDialog'
import Paper from '../../elements/Paper'
import {useDeveloperMode} from '../../../contexts/developerMode'
import LoginControl from './LoginControl'


const Tour = dynamic(() => import('./Tour'))


function SettingsControl({title, tourSteps, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
    `,

    desktopContent: css`
      display: flex;
      gap: 8px;
      align-items: center;

      @media (max-width: ${theme.breakpoints.sm}px) {
        display: none;
      }
    `,

    mobileContent: css`
      display: none;

      @media (max-width: ${theme.breakpoints.sm}px) {
        display: inherit;
      }
    `,

    dialogContent: css`
      background: ${theme.palette.primary.lightest};
      color: ${theme.palette.onSurface.dark};

      padding: 8px;
      height: 100%;
    `,

    label: css`
      font-size: 1.2rem;
      font-weight: 600;
    `,

    tour: css`
      @media (max-width: ${theme.breakpoints.sm}px) {
        display: none;
      }
    `
  }

  const {t} = useTranslation('base')

  const [controlDialogOpen, setShareDialog] = React.useState(false)
  const onControlButtonClick = () => {
    setShareDialog(true)
  }

  const onCloseControlDialog = () => {
    setShareDialog(false)
  }

  const [tourRunning, onTourRunningChange] = React.useState(false)
  const developMode = useDeveloperMode()

  return (
    <>
      <div css={styles.root} {...props}>
        <div css={styles.desktopContent}>
          {developMode && <DarkModeToggle aria-label={t('Appearance')}/>}
          <LocaleSelect aria-label={t('Language')}/>
          <IconButton aria-label={t('Tour')} css={styles.tour} onClick={() => onTourRunningChange(runTour => !runTour)}>
            <QuestionMarkIcon/>
          </IconButton>
          {tourRunning && <Tour steps={tourSteps} running={tourRunning} onChange={onTourRunningChange}/>}
          {false && developMode && <LoginControl/>}
        </div>
        <div css={styles.mobileContent}>
          <IconButton aria-label={title} onClick={onControlButtonClick}>
            <SettingsIcon/>
          </IconButton>
        </div>
      </div>

      <BasicDialog
        title={title}
        open={controlDialogOpen}
        onClose={onCloseControlDialog}
      >
        <Paper css={styles.dialogContent}>
          <Table size="small">
            {developMode && <TableRow>
              <TableCell css={styles.label}>{t('Appearance')}</TableCell>
              <TableCell align="right"><DarkModeToggle aria-label={t('Appearance')}/></TableCell>
            </TableRow>}
            <TableRow>
              <TableCell css={styles.label}>{t('Language')}</TableCell>
              <TableCell align="right"><LocaleSelect aria-label={t('Language')}/></TableCell>
            </TableRow>
          </Table>
        </Paper>
      </BasicDialog>
    </>
  )
}

export default React.memo(SettingsControl)
