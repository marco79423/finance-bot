export default async function delay(wait) {
  await new Promise(resolve => setTimeout(resolve, wait))
}
