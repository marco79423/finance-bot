import React from 'react'
import Document, {Head, Html, Main, NextScript} from 'next/document'
import createEmotionServer from '@emotion/server/create-instance'

import createEmotionCache from '../utils/createEmotionCache'

export default class MyDocument extends Document {
  static async getInitialProps(ctx) {
    // Emotion
    const cache = createEmotionCache()
    const {extractCriticalToChunks} = createEmotionServer(cache)

    const originalRenderPage = ctx.renderPage
    ctx.renderPage = () =>
      originalRenderPage({
        // eslint-disable-next-line react/display-name
        enhanceApp: (App) => (props) => (
          <App emotionCache={cache} {...props} />
        ),
      })

    const initialProps = await Document.getInitialProps(ctx)
    // This is important. It prevents Emotion to render invalid HTML.
    // See https://github.com/mui/material-ui/issues/26561#issuecomment-855286153
    const emotionStyles = extractCriticalToChunks(initialProps.html)
    const emotionStyleTags = emotionStyles.styles.map((style) => (
      <style
        data-emotion={`${style.key} ${style.ids.join(' ')}`}
        key={style.key}
        // eslint-disable-next-line react/no-danger
        dangerouslySetInnerHTML={{__html: style.css}}
      />
    ))

    return {
      ...initialProps,
      emotionStyleTags,
    }
  }

  render() {
    return (
      <Html>
        <Head>
          <meta charSet="UTF-8"/>

          <link rel="icon" type="image/svg+xml" href="/favicon.svg"/>
          <link rel="shortcut icon" type="image/svg+xml" href="/favicon.svg"/>
          <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png"/>
          <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png"/>
          <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png"/>
          <link rel="icon" type="image/png" sizes="192x192" href="/logo-192x192.png"/>
          <link rel="icon" type="image/png" sizes="512x512" href="/logo-512x512.png"/>

          <link rel="manifest" href="/manifest.json"/>

          <link rel="search" href="/opensearch.xml" type="application/opensearchdescription+xml" title="Paji"/>

          {/* https://nextjs.org/docs/messages/google-font-display */}
          <link rel="stylesheet"
                href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=optional"/>
          <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons"/>

          <meta name="emotion-insertion-point" content="" />
          {this.props.emotionStyleTags}
        </Head>
        <body>
        <Main/>
        <NextScript/>
        </body>
      </Html>
    )
  }
}
