import React from 'react'
import {css} from '@emotion/react'

import {ProcessStatus} from '../../../constants'
import ProcessStatusInfo from '../../modules/ProcessStatusInfo'
import DataExportControl from '../../modules/DataExportControl'
import InputResultPanelToolLayout from '../InputResultPanelToolLayout'
import useAsyncDataTransform from '../../../hooks/useAsyncDataTransform'
import TextEditor from '../../modules/TextEditor'
import useLangConfig from '../../../hooks/useLangConfig'

const DefaultTransformOptions = {
  delayTime: 500
}

export default function TextToTextTransformerLayout({
                                                      inputLang = 'text',
                                                      outputLang = 'text',
                                                      transform,
                                                      inputExtraControl,
                                                      transformOptions = {}
                                                    }) {
  const styles = {
    top: css`
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    `,

    inputBottom: css`
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: space-between;
    `,

    bottomControlBar: css`
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: flex-end;

      height: 36px;
    `,
  }


  const [textInput, setTextInput] = React.useState('')
  const onTextInputChange = React.useCallback(textInput => {
    setTextInput(textInput)
  }, [])

  const [processStatus, outputResult] = useAsyncDataTransform(textInput, transform, {...DefaultTransformOptions, ...transformOptions})
  const outputLangConfig = useLangConfig(outputLang)

  return (
    <InputResultPanelToolLayout
      inputContent={(
        <TextEditor
          id="text-input"
          lang={inputLang}
          value={textInput}
          onChange={onTextInputChange}
          autoFocus={true}
          status={<ProcessStatusInfo id="process-status" processStatus={processStatus} enableProgressing/>}
          extraControl={inputExtraControl}
        />
      )}

      resultContent={(
        <TextEditor
          id="text-output"
          lang={outputLang}
          readOnly={true}
          loading={processStatus === ProcessStatus.Processing}
          value={outputResult instanceof Error ? outputResult.toString() : outputResult}

          extraControl={(
            <div css={styles.bottomControlBar}>
              <DataExportControl
                disabled={!outputResult || outputResult instanceof Error}
                data={outputResult}

                downloadButtonId={'download-button'}
                downloadFileExt={outputLangConfig.fileExt}
              />
            </div>
          )}
        />
      )}
    />
  )
}
