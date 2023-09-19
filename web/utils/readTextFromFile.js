export default async function readTextFromFile(file) {
  return await new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (event) => {
      resolve(event?.target?.result)
    }
    reader.onerror = (event) => {
      reader.abort()
      reject(event)
    }
    reader.readAsText(file, 'utf-8')
  })
}
