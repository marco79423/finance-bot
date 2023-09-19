import React from 'react'
import {useRouter} from 'next/router'
import {css, useTheme} from '@emotion/react'
import {useTranslation} from 'next-i18next'
import lodash from 'lodash'
import {useDebounce} from 'use-debounce'
import Fuse from 'fuse.js'
import Masonry from 'react-masonry-css'

import {ToolCategories, ToolGroups} from '../../../config/categories.config'
import HomeLayout from './HomeLayout'
import ToolPanel from './ToolPanel'
import SearchField from '../../../components/elements/SearchField'
import Paper from '../../../components/elements/Paper'
import {useAppCtx} from '../../../contexts/appCtx'
import useAllToolInfos from '../../../hooks/useAllToolInfos'

export default function Home({query}) {
  const theme = useTheme()
  const styles = {
    root: css`
    `,

    control: css`
      margin-top: 8px;
    `,

    searchField: css`
      flex: 1;
      max-width: 400px;

      & > div {
        height: 48px;
        padding: 8px 16px;
      }
    `,

    mobileContent: css`
      margin-top: 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    `,

    desktopContent: css`
      margin-top: 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;

      .masonry {
        display: flex;
        gap: 16px;
      }

      .masonry-column {
        display: flex;
        flex-direction: column;
        gap: 16px;
      }
    `,

    section: css`
      padding: 24px;
      background: ${theme.palette.surface.main};
    `,

    sectionHeader: css`
      font-size: 1.4rem;
      font-weight: 600;
      margin-bottom: 16px;
    `,

    sectionBody: css`
      display: flex;
      flex-direction: column;
      gap: 16px;
    `,

    adFooter: css`
      margin: 0 auto;
      max-width: 728px;
    `,
  }

  const {t} = useTranslation()
  const [currentCategory, setCurrentCategory] = React.useState('all')

  const allToolInfos = useAllToolInfos()
  const allCategoryTools = React.useMemo(() =>
      allToolInfos.filter(onlineTool => onlineTool.category === currentCategory || currentCategory === 'all'),
    [allToolInfos, currentCategory]
  )

  const router = useRouter()
  const [queryText, setQueryText] = React.useState(query)
  const onSearchTextChange = React.useCallback((queryText) => {
    (async function () {
      setQueryText(queryText)
      await router.replace({
        query: {
          ...router.query,
          q: queryText,
        },
      })
    }())
  }, [router])

  React.useEffect(() => {
    onSearchTextChange('')
  }, [currentCategory])

  const [debouncedSearchText] = useDebounce(queryText, 20, {leading: true})
  const filteredCategoryTools = React.useMemo(() => {
    if (debouncedSearchText) {
      const fuse = new Fuse(allCategoryTools, {
        keys: [
          {name: 'label', weight: 1},
        ],
        includeMatches: true,
      })

      return highlight(fuse.search(debouncedSearchText))
    } else {
      return allCategoryTools
    }
  }, [allCategoryTools, debouncedSearchText])

  const toolCategories = React.useMemo(() => (
    ToolCategories
      .map(toolCategory => ({
        key: toolCategory,
        value: toolCategory,
        label: t(`tool-category.${toolCategory}`),
        groups: ToolGroups
          .map(toolGroup => [
            toolGroup,
            filteredCategoryTools
              .filter(onlineTool => onlineTool.category === toolCategory)
              .filter(onlineTool => onlineTool.group === toolGroup)
          ])
          .filter(([_, onlineTools]) => onlineTools.length > 0)
          .map(([toolGroup, onlineTools]) => ({
            key: toolGroup,
            value: toolGroup,
            label: t(`tool-group.${toolGroup}`),
            tools: onlineTools,
          }))
      }))
      .filter(toolCategory => toolCategory.groups.length > 0)
  ), [t, filteredCategoryTools])

  const appCtx = useAppCtx()

  return (
    <HomeLayout currentCategory={currentCategory} setCurrentCategory={setCurrentCategory}>
      <div css={styles.root}>
        <div css={styles.control}>
          <div id="home-search" css={styles.searchField}>
            <SearchField
              placeholder={t('home.search-placeholder')}
              query={queryText}
              onQueryChange={onSearchTextChange}
            />
          </div>
        </div>
        {appCtx.isMobile ? (
          <div css={styles.mobileContent}>
            {toolCategories.map(toolCategory => (
              <Paper key={toolCategory.key} css={styles.section}>
                <div css={styles.sectionHeader}>{toolCategory.label}</div>
                <div css={styles.sectionBody}>
                  {toolCategory.groups.map(toolGroup => (
                    <ToolPanel
                      key={toolGroup.key}
                      title={toolGroup.label}
                      list={toolGroup.tools}
                    />
                  ))}
                </div>
              </Paper>
            ))}
          </div>
        ) : (
          <div css={styles.desktopContent}>
            {toolCategories.map(toolCategory => (
              <Paper key={toolCategory.key} css={styles.section}>
                <div css={styles.sectionHeader}>{toolCategory.label}</div>
                <Masonry
                  className="masonry"
                  columnClassName="masonry-column"
                  breakpointCols={{default: 4, [theme.breakpoints.lg]: 3, [theme.breakpoints.md]: 2}}>
                  {toolCategory.groups.map(toolGroup => (
                    <ToolPanel
                      key={toolGroup.key}
                      title={toolGroup.label}
                      list={toolGroup.tools}
                    />
                  ))}
                </Masonry>
              </Paper>
            ))}
          </div>
        )}

        {/*<div css={styles.adFooter}>*/}
        {/*  <Adsense*/}
        {/*    client="ca-pub-9395644566418596"*/}
        {/*    slot="1014541144"*/}
        {/*    format="auto"*/}
        {/*    style={{*/}
        {/*      display: 'block',*/}

        {/*      width: '100vw',*/}
        {/*      maxWidth: 728,*/}
        {/*      height: 90,*/}
        {/*    }}*/}
        {/*    responsive="true"*/}
        {/*  />*/}
        {/*</div>*/}
      </div>
    </HomeLayout>
  )
}


const highlight = (fuseSearchResult) => {
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
