import {useAppCtx} from '../contexts/appCtx'


export default function useLocales() {
  const appCtx = useAppCtx()
  return appCtx.locales
}
