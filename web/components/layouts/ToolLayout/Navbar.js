import React from 'react'
import {useRouter} from 'next/router'
import {useTranslation} from 'next-i18next'
import fp from 'lodash/fp'
import lodash from 'lodash'
import Fuse from 'fuse.js'
import {useDebounce} from 'use-debounce'
import {css, useTheme} from '@emotion/react'
import {Accordion, AccordionDetails, AccordionSummary, Divider, Typography} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'

import {ToolCategories, ToolGroups} from '../../../config/categories.config'
import useAllToolInfos from '../../../hooks/useAllToolInfos'
import SearchField from '../../elements/SearchField'
import Paper from '../../elements/Paper'
import NavbarContainer from '../../modules/NavbarContainer'
import ToolList from '../../modules/ToolList'

const MaxToolCount = 5

function Navbar({group, ...props}) {
  const styles = {
    searchField: css`
      margin: 8px 0;
    `,
  }

  const {t} = useTranslation()

  const router = useRouter()

  const [searchText, setSearchText] = React.useState('')
  const onSearchTextChange = async (searchText) => {
    setSearchText(searchText)
    await router.replace({
      query: {
        ...router.query,
        q: searchText,
      },
    })
  }

  const allToolInfos = useAllToolInfos()

  const [debouncedSearchText] = useDebounce(searchText, 20, {leading: true})
  const filteredOnlineTools = React.useMemo(() => {
    if (debouncedSearchText) {
      const fuse = new Fuse(allToolInfos, {
        keys: [
          {name: 'label', weight: 1},
        ],
        includeMatches: true,
      })

      return highlight(fp.flow(
        fp.take(MaxToolCount),
      )(fuse.search(debouncedSearchText)))
    } else {
      return []
    }
  }, [allToolInfos, debouncedSearchText])

  const onlineToolCategories = React.useMemo(() => (
    ToolCategories
      .map(toolCategory => ({
        key: toolCategory,
        value: toolCategory,
        label: t(`tool-category.${toolCategory}`),
        groups: ToolGroups
          .map(toolGroup => [
            toolGroup,
            allToolInfos
              .filter(tool => tool.category === toolCategory)
              .filter(tool => tool.group === toolGroup)
          ])
          .filter(([_, toolInfos]) => toolInfos.length > 0)
          .map(([toolGroup, toolInfos]) => ({
            key: toolGroup,
            value: toolGroup,
            label: t(`tool-group.${toolGroup}`),
            tools: toolInfos.map(onlineTool => ({
              ...onlineTool,
              key: onlineTool.key,
              label: t(`${onlineTool.key}`),
              active: onlineTool.url === router.pathname,
            })),
          }))
      }))
      .filter(toolCategory => toolCategory.groups.length > 0)
  ), [t, allToolInfos, router.pathname])

  return (
    <NavbarContainer
      subHeader={
        <div css={styles.searchField}>
          <SearchField
            id="tool-search"
            placeholder={t('tool-layout.search-placeholder')}
            query={searchText}
            onQueryChange={onSearchTextChange}
          />
        </div>
      }
      {...props}
    >
      {searchText.length > 0 ? (
        <SearchPanel
          css={styles.section}
          title={t('search-results')}
          tools={filteredOnlineTools}
        />
      ) : null}

      {searchText.length === 0 ? (
        <div css={css`
          display: flex;
          flex-direction: column;
        `}>
          {onlineToolCategories.map(onlineToolCategory => (
            <CategoryPanel key={onlineToolCategory.key} onlineToolCategory={onlineToolCategory}/>
          ))}
        </div>
      ) : null}
    </NavbarContainer>
  )
}


function SearchPanel({tools, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
      padding: 16px;
      background: ${theme.palette.surface.main};
    `,

    header: css`
      font-size: 1.2rem;
      font-weight: 600;
      margin-bottom: 8px;
    `,
  }

  const {t} = useTranslation()

  return (
    <Paper css={styles.root} {...props}>
      <div css={styles.header}>{t('tool-layout.search-results')}</div>
      <Divider/>
      <ToolList tools={tools}/>
    </Paper>
  )
}


function CategoryPanel({onlineToolCategory, ...props}) {
  const theme = useTheme()
  const styles = {
    root: css`
    `,

    header: css`
      font-size: 1.2rem;
      font-weight: 600;
    `,

    group: css`
      padding: 16px;
      color: ${theme.palette.onSurface.dark};

      & :not(:first-of-type) {
        margin-top: 16px;
      }
    `,

    groupTitle: css`
      font-size: 1.2rem;
      font-weight: 600;
    `,
  }

  const defaultExpanded = React.useMemo(() => {
    return onlineToolCategory.groups.filter(group => group.tools.filter(tool => tool.active).length > 0).length > 0
  }, [onlineToolCategory])

  return (
    <Accordion css={styles.root} defaultExpanded={defaultExpanded} {...props}>
      <AccordionSummary expandIcon={<ExpandMoreIcon/>}>
        <div css={styles.header}>{onlineToolCategory.label}</div>
      </AccordionSummary>
      <AccordionDetails css={styles.detail}>
        {
          onlineToolCategory.groups.map(group => (
            <Paper key={group.key} css={styles.group}>
              <Typography css={styles.groupTitle}>{group.label}</Typography>
              <ToolList tools={group.tools}/>
            </Paper>
          ))
        }
      </AccordionDetails>
    </Accordion>
  )
}

function highlight(fuseSearchResult) {
  const generateHighlightedText = (inputText, regions = []) => {
    let content = ''
    let nextUnhighlightedRegionStartingIndex = 0

    regions.forEach(region => {
      const lastRegionNextIndex = region[1] + 1

      content += [
        inputText.substring(nextUnhighlightedRegionStartingIndex, region[0]),
        `<b>`,
        inputText.substring(region[0], lastRegionNextIndex),
        '</b>',
      ].join('')

      nextUnhighlightedRegionStartingIndex = lastRegionNextIndex
    })

    content += inputText.substring(nextUnhighlightedRegionStartingIndex)

    return content
  }

  return fuseSearchResult
    .filter(({matches}) => matches && matches.length)
    .map(({item, matches}) => {
      const highlightedItem = {...item}

      matches.forEach((match) => {
        lodash.set(highlightedItem, match.key, generateHighlightedText(match.value, match.indices))
      })

      return highlightedItem
    })
}


export default React.memo(Navbar)
