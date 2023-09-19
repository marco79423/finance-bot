import {blueGrey, grey, pink} from '@mui/material/colors'
import {createTheme} from '@mui/material/styles'

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      lightest: blueGrey[700],
      light: blueGrey[800],
      main: blueGrey[900],
      dark: blueGrey[900],
    },
    onPrimary: {
      main: grey[300],
      dark: grey[300],
    },
    secondary: {
      light: pink[200],
      main: pink[400],
      dark: pink[600],
    },
    surface: {
      light: grey[900],
      main: grey[900],
      dark: grey[900],
    },
    onSurface: {
      light: grey[200],
      main: grey[300],
      dark: grey[400],
    },
    background: {
      light: '#121212',
      main: '#121212',
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
  secondary: {
    light: pink[200],
    main: pink[400],
    dark: pink[600],
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
