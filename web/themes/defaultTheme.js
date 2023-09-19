import {grey, indigo, pink} from '@mui/material/colors'
import {createTheme} from '@mui/material/styles'

const theme = createTheme({
  palette: {
    primary: {
      lightest: indigo[100],
      light: indigo[400],
      main: indigo[600],
      dark: indigo[800],
    },
    onPrimary: {
      main: 'white',
      dark: 'black',
    },
    secondary: {
      light: pink[200],
      main: pink[400],
      dark: pink[600],
    },
    surface: {
      light: 'white',
      main: grey[100],
      dark: grey[300],
    },
    onSurface: {
      light: '#000000',
      main: '#000000',
      dark: '#000000',
    },
    background: {
      light: indigo[300],
      main: indigo[400],
    },
    onBackground: {
      main: '#f6f3ed' // apple white
    },
    success: {
      light: '#4caf50',
      main: '#2e7d32',
      dark: '#1b5e20',
    },
    error: {
      light: '#e57373',
      main: '#f44336',
      dark: '#d32f2f',
    },
  },
  breakpoints: {
    xs: 0,
    sm: 600,
    md: 900,
    lg: 1200,
    xl: 1536,
  },
})

export default theme
