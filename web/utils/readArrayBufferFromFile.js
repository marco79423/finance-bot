export default async function readArrayBufferFromFile(file) {
  return await new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (event) => {
      resolve(event?.target?.result)
    }
    reader.onerror = (event) => {
      reader.abort()
      reject(event)
    }
    reader.readAsArrayBuffer(file)
  })
}
