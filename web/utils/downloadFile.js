import jsDownload from 'js-file-download'

export default async function downloadFile({fileName, data}) {
  jsDownload(data, fileName)
}
