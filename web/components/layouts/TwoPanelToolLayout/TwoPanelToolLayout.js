import React from 'react'
import {css} from '@emotion/react'

import {useAppCtx} from '../../../contexts/appCtx'
import TabsPanel from './TabsPanel'
import GenericPanel from './GenericPanel'
import GenericTabPanel from './GenericTabPanel'
import ToolLayout from '../ToolLayout'


export default function TwoPanelToolLayout({
                                             leftPanelName,
                                             leftPanelTop,
                                             leftPanelControl,
                                             leftPanelContent,
                                             leftPanelBottom,

                                             rightPanelName,
                                             rightPanelTop,
                                             rightPanelControl,
                                             rightPanelContent,
                                             rightPanelBottom,
                                           }) {
  const styles = {
    content: css`
      height: 100%;
      display: flex;
      gap: 8px;
      position: relative;

      > * {
        flex: 1;
        width: 0; // 確保兩邊同寬
      }
    `,
  }

  const appCtx = useAppCtx()

  return (
    <ToolLayout>
      {/* Desktop Mode */}
      {!appCtx.isMobile && <div css={styles.content}>
        <GenericPanel
          top={leftPanelTop}
          control={leftPanelControl}
          content={leftPanelContent}
          bottom={leftPanelBottom}
        />
        <GenericPanel
          top={rightPanelTop}
          control={rightPanelControl}
          content={rightPanelContent}
          bottom={rightPanelBottom}
        />
      </div>}

      {/* Mobile Mode */}
      {appCtx.isMobile && <div css={styles.content}>
        <TabsPanel>
          <GenericTabPanel
            tabKey="left-panel"
            tabLabel={leftPanelName}
            top={leftPanelTop}
            control={leftPanelControl}
            content={leftPanelContent}
            bottom={leftPanelBottom}
          />
          <GenericTabPanel
            tabKey="right-panel"
            tabLabel={rightPanelName}
            top={rightPanelTop}
            control={rightPanelControl}
            content={rightPanelContent}
            bottom={rightPanelBottom}
          />
        </TabsPanel>
      </div>}
    </ToolLayout>
  )
}
