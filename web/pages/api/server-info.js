import packageJson from '../../package.json'

export default async function handler(_, res) {
  res.status(200).json({
    data: {
      frontendVersion: packageJson.version
    }
  })
};
