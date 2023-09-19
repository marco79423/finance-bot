import React from 'react'
import {useTranslation} from 'next-i18next'

import SettingsControl from '../../../components/modules/SettingsControl'
import Navbar from './Navbar'
import {ToolCategories} from '../../../config/categories.config'
import AppLayout from '../../../components/layouts/AppLayout'

export default function HomeLayout({currentCategory, setCurrentCategory, children, ...props}) {
  const {t} = useTranslation()

  const categories = React.useMemo(() => (
    [
      ...ToolCategories
        .map(category => ({
          key: category,
          value: category,
          label: t(`tool-category.${category}`),
        }))
    ]
  ), [t])

  const steps = React.useMemo(() => {
    return [
      {
        target: '#home-container',
        disableBeacon: true,
        content: t('home.tour.tool-dashboard'),
        placement: 'bottom',
      },
      {
        target: '#home-category',
        disableBeacon: true,
        content: t('home.tour.tool-category'),
      },
      {
        target: '#home-search',
        disableBeacon: true,
        content: t('home.tour.tool-search'),
      },
    ]
  }, [t])

  return (
    <AppLayout
      namePrefix={'home'}
      title={t('home.title')}
      navbar={(
        <Navbar
          items={categories}
          currentItem={currentCategory}
          setItem={setCurrentCategory}
        />
      )}
      settings={
        <SettingsControl
          title={t('home.settings-title')}
          tourSteps={steps}
        />
      }
      description={t('home.description')}
      {...props}
    >
      {children}
    </AppLayout>
  )
}
