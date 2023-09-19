import React from 'react'
import {css, useTheme} from '@emotion/react'
import {Tab, Tabs} from '@mui/material'


export default function TabsPanel({children, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
    `,
    tabs: css`
      button {
        background: ${theme.palette.surface.dark};
        color: ${theme.palette.onSurface.main};
        
        font-size: 1rem;
        text-transform: initial;
        border-top-left-radius: 0.3rem;
        border-top-right-radius: 0.3rem;
        
        &.Mui-selected {
          color: ${theme.palette.onSurface.main};
        }

        &:not(:first-of-type) {
          margin-left: 0.2rem;
        }
      }
    `,

    tabPanel: css`
      background: ${theme.palette.surface.main};
      
      height: calc(100% - 48px);
      position: relative;
    `,
  }

  const tabs = React.useMemo(() => {
    return React.Children.map(children, child => {
      if (React.isValidElement(child)) {
        if (!child.props.tabKey) {
          console.error('tabKey 是必填欄位')
        }

        if (!child.props.tabLabel) {
          console.error('tabLabel 是必填欄位')
        }

        return (
          <Tab
            key={child.props.tabKey}
            value={child.props.tabKey}
            label={child.props.tabLabel}
          />
        )
      }

      return null
    })
  }, [children])

  const [currentTab, setCurrentTab] = React.useState(tabs[0].props.value)
  const onCurrentTabChange = (event, newValue) => {
    setCurrentTab(newValue)
  }

  const currentTabNode = React.useMemo(() => {
    return React.Children.map(children, child => {
      if (React.isValidElement(child) && child.props.tabKey === currentTab) {
        return child
      }
      return null
    })
  }, [children, currentTab])

  return (
    <div css={styles.root} {...props}>
      <Tabs css={styles.tabs} value={currentTab} onChange={onCurrentTabChange}>
        {tabs}
      </Tabs>
      <div css={styles.tabPanel}>
        {currentTabNode}
      </div>
    </div>
  )
}

TabsPanel.Tab = Tab
