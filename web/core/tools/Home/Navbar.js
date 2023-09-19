import React from 'react'
import {css, useTheme} from '@emotion/react'
import {List, ListItemButton} from '@mui/material'

import NavbarContainer from '../../../components/modules/NavbarContainer'


function Navbar({items, currentItem, setItem, ...props}) {
  const theme = useTheme()
  const styles = {
    list: css`
      padding: 0;
      border-radius: 3px;
      background: ${theme.palette.surface.light};
      color: ${theme.palette.onSurface.dark};
    `,

    item: css`
      font-size: 1.2rem;
      font-weight: 600;
      padding: 12px 16px;
    `,
  }

  return (
    <NavbarContainer {...props}>
      <List id="home-category" css={styles.list}>
        {items.map(item => (
          <li key={item.key}>
            <ListItemButton
              css={styles.item}
              selected={item.value === currentItem}
              onClick={() => setItem(item.value)}
              divider={true}
            >
              <span dangerouslySetInnerHTML={{__html: item.label}}/>
            </ListItemButton>
          </li>
        ))}
      </List>
    </NavbarContainer>
  )
}

export default React.memo(Navbar)