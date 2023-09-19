import React from 'react'
import LeaveSiteDialogBase from './LeaveSiteDialogBase'

export default function useLeaveSiteDetect() {
  const [leaveSiteDialogOpen, setLeaveSiteDialogOpen] = React.useState(false)
  const onLeaveSiteDialogClose = () => {
    setLeaveSiteDialogOpen(false)
  }

  const [targetLink, setTargetLink] = React.useState()
  const handleLink = React.useCallback((e, link) => {
    // 針對外連頁面跳視窗
    if (link.startsWith('http')) {
      e.preventDefault()
      setTargetLink(link)
      setLeaveSiteDialogOpen(true)
    }
  }, [])

  const LeaveSiteDialog = (props) => {
    return (
      <LeaveSiteDialogBase
        open={leaveSiteDialogOpen}
        onClose={onLeaveSiteDialogClose}
        targetLink={targetLink}
        {...props}
      />
    )
  }

  return [handleLink, LeaveSiteDialog]
}