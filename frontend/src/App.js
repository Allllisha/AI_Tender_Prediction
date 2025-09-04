import React, { useState, useEffect } from 'react';
import {
  Container,
  AppBar,
  Toolbar,
  Typography,
  Tab,
  Tabs,
  Box,
  Paper,
  CssBaseline,
  Fade,
  Button,
  Menu,
  MenuItem,
  useMediaQuery,
  useTheme,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { BiGlasses } from 'react-icons/bi';
import { FaSearch, FaChartLine, FaListUl, FaBuilding, FaDatabase } from 'react-icons/fa';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LogoutIcon from '@mui/icons-material/Logout';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import TenderSearch from './components/TenderSearch';
import PredictionDashboard from './components/PredictionDashboard';
import CompanyStrengths from './components/CompanyStrengths';
import BulkPrediction from './components/BulkPrediction';
import Login from './components/Login';
import CSVUpload from './components/CSVUpload';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      light: '#5c7cfa',
      main: '#1e3a5f',
      dark: '#15304d',
      contrastText: '#ffffff',
    },
    secondary: {
      light: '#757575',
      main: '#424242',
      dark: '#212121',
      contrastText: '#ffffff',
    },
    success: {
      light: '#2a4a6f',
      main: '#1e3a5f',
      dark: '#15304d',
      contrastText: '#ffffff',
    },
    info: {
      light: '#5c7cfa',
      main: '#1e3a5f',
      dark: '#15304d',
    },
    warning: {
      light: '#757575',
      main: '#424242',
      dark: '#212121',
    },
    error: {
      light: '#757575',
      main: '#424242',
      dark: '#212121',
    },
    background: {
      default: '#ffffff',
      paper: '#ffffff',
    },
    text: {
      primary: '#212121',
      secondary: '#757575',
    },
    divider: '#e0e0e0',
    grey: {
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#e0e0e0',
      300: '#bdbdbd',
      400: '#9e9e9e',
      500: '#757575',
      600: '#616161',
      700: '#424242',
      800: '#303030',
      900: '#212121',
    },
  },
  typography: {
    fontFamily: [
      '"Inter"',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontWeight: 200,
      letterSpacing: '-0.01em',
      '@media (max-width:600px)': {
        fontSize: '2rem',
      },
      '@media (min-width:600px)': {
        fontSize: '2.5rem',
      },
      '@media (min-width:960px)': {
        fontSize: '3rem',
      },
      '@media (min-width:1280px)': {
        fontSize: '3.5rem',
      },
    },
    h2: {
      fontWeight: 200,
      letterSpacing: '-0.01em',
      '@media (max-width:600px)': {
        fontSize: '1.5rem',
      },
      '@media (min-width:600px)': {
        fontSize: '2rem',
      },
      '@media (min-width:960px)': {
        fontSize: '2.5rem',
      },
      '@media (min-width:1280px)': {
        fontSize: '2.75rem',
      },
    },
    h3: {
      fontWeight: 300,
      letterSpacing: '-0.005em',
      '@media (max-width:600px)': {
        fontSize: '1.25rem',
      },
      '@media (min-width:600px)': {
        fontSize: '1.75rem',
      },
      '@media (min-width:960px)': {
        fontSize: '2rem',
      },
      '@media (min-width:1280px)': {
        fontSize: '2.25rem',
      },
    },
    h4: {
      fontWeight: 300,
      letterSpacing: '-0.005em',
      '@media (max-width:600px)': {
        fontSize: '1.125rem',
      },
      '@media (min-width:600px)': {
        fontSize: '1.5rem',
      },
      '@media (min-width:960px)': {
        fontSize: '1.75rem',
      },
      '@media (min-width:1280px)': {
        fontSize: '1.875rem',
      },
    },
    h5: {
      fontWeight: 400,
      letterSpacing: '0em',
      '@media (max-width:600px)': {
        fontSize: '1rem',
      },
      '@media (min-width:600px)': {
        fontSize: '1.25rem',
      },
      '@media (min-width:960px)': {
        fontSize: '1.375rem',
      },
      '@media (min-width:1280px)': {
        fontSize: '1.5rem',
      },
    },
    h6: {
      fontWeight: 400,
      letterSpacing: '0em',
      '@media (max-width:600px)': {
        fontSize: '0.875rem',
      },
      '@media (min-width:600px)': {
        fontSize: '1rem',
      },
      '@media (min-width:960px)': {
        fontSize: '1.125rem',
      },
      '@media (min-width:1280px)': {
        fontSize: '1.25rem',
      },
    },
    subtitle1: {
      fontWeight: 400,
      letterSpacing: '0em',
      '@media (max-width:600px)': {
        fontSize: '0.875rem',
      },
      '@media (min-width:600px)': {
        fontSize: '1rem',
      },
      '@media (min-width:960px)': {
        fontSize: '1.1rem',
      },
    },
    subtitle2: {
      fontWeight: 400,
      letterSpacing: '0em',
      '@media (max-width:600px)': {
        fontSize: '0.75rem',
      },
      '@media (min-width:600px)': {
        fontSize: '0.875rem',
      },
      '@media (min-width:960px)': {
        fontSize: '1rem',
      },
    },
    body1: {
      fontWeight: 400,
      letterSpacing: '0em',
      lineHeight: 1.7,
      '@media (max-width:600px)': {
        fontSize: '0.875rem',
      },
      '@media (min-width:600px)': {
        fontSize: '0.9375rem',
      },
      '@media (min-width:960px)': {
        fontSize: '1rem',
      },
    },
    body2: {
      fontWeight: 400,
      letterSpacing: '0em',
      lineHeight: 1.6,
      '@media (max-width:600px)': {
        fontSize: '0.75rem',
      },
      '@media (min-width:600px)': {
        fontSize: '0.875rem',
      },
      '@media (min-width:960px)': {
        fontSize: '0.925rem',
      },
    },
    button: {
      fontWeight: 500,
      letterSpacing: '0.01em',
      textTransform: 'none',
      '@media (max-width:600px)': {
        fontSize: '0.875rem',
      },
      '@media (min-width:600px)': {
        fontSize: '1rem',
      },
    },
    caption: {
      '@media (max-width:600px)': {
        fontSize: '0.625rem',
      },
      '@media (min-width:600px)': {
        fontSize: '0.75rem',
      },
    },
  },
  shape: {
    borderRadius: 0,
  },
  spacing: (factor) => `${8 * factor}px`,
  shadows: [
    'none',
    '0px 1px 2px rgba(0, 0, 0, 0.04)',
    '0px 2px 4px rgba(0, 0, 0, 0.04)',
    '0px 4px 8px rgba(0, 0, 0, 0.04)',
    '0px 8px 16px rgba(0, 0, 0, 0.04)',
    'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none',
  ],
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        '*': {
          boxSizing: 'border-box',
          margin: 0,
          padding: 0,
        },
        html: {
          MozOsxFontSmoothing: 'grayscale',
          WebkitFontSmoothing: 'antialiased',
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100%',
          margin: 0,
          padding: 0,
        },
        body: {
          display: 'flex',
          flex: '1 1 auto',
          flexDirection: 'column',
          minHeight: '100%',
          backgroundColor: '#ffffff',
          backgroundImage: `
            linear-gradient(rgba(0, 0, 0, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 0, 0, 0.02) 1px, transparent 1px)
          `,
          backgroundSize: '20px 20px',
          backgroundPosition: '0 0, 0 0',
          margin: 0,
          padding: 0,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1e3a5f',  // 落ち着いた紺色に変更
          boxShadow: 'none',
          borderBottom: 'none',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 0,
          padding: '16px 32px',
          transition: 'all 0.2s ease',
          border: '2px solid #212121',
          backgroundColor: 'transparent',
          color: '#212121',
          '&:hover': {
            backgroundColor: '#212121',
            color: '#ffffff',
            borderColor: '#212121',
            transform: 'none',
            boxShadow: 'none',
          },
        },
        contained: {
          backgroundColor: '#212121',
          color: '#ffffff',
          border: '2px solid #212121',
          '&:hover': {
            backgroundColor: '#1e3a5f',
            borderColor: '#1e3a5f',
          },
        },
        outlined: {
          borderColor: '#212121',
          borderWidth: '2px',
          '&:hover': {
            backgroundColor: '#212121',
            color: '#ffffff',
            borderColor: '#212121',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 0,
          transition: 'border-color 0.2s ease',
          border: '1px solid #bdbdbd',
          boxShadow: 'none',
          backgroundColor: '#ffffff',
          '&:hover': {
            transform: 'none',
            borderColor: '#212121',
            boxShadow: 'none',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 0,
          backgroundColor: '#ffffff',
          border: '1px solid #bdbdbd',
          boxShadow: 'none',
        },
        elevation1: {
          boxShadow: 'none',
        },
        elevation2: {
          boxShadow: 'none',
        },
        elevation3: {
          boxShadow: 'none',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 0,
          fontWeight: 500,
          backgroundColor: '#f5f5f5',
          color: '#212121',
          border: '1px solid #bdbdbd',
        },
        colorPrimary: {
          backgroundColor: '#1e3a5f',
          color: '#ffffff',
          border: '1px solid #1e3a5f',
        },
        colorSecondary: {
          backgroundColor: '#757575',
          color: '#ffffff',
          border: '1px solid #757575',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 0,
            fontWeight: 400,
            '& fieldset': {
              borderColor: '#bdbdbd',
              borderWidth: '1px',
            },
            '&:hover fieldset': {
              borderColor: '#212121',
              borderWidth: '2px',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#1e3a5f',
              borderWidth: '2px',
            },
          },
          '& .MuiInputLabel-root': {
            fontWeight: 400,
            color: '#757575',
            '&.Mui-focused': {
              color: '#1e3a5f',
            },
          },
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 400,
          fontSize: '1.1rem',
          minHeight: 64,
          letterSpacing: '0em',
          color: '#757575',
          '&.Mui-selected': {
            color: '#212121',
            fontWeight: 500,
          },
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        indicator: {
          backgroundColor: '#212121',
          height: 2,
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 0,
          height: 1,
          backgroundColor: '#e0e0e0',
        },
        bar: {
          backgroundColor: '#1e3a5f',
        },
      },
    },
    MuiTable: {
      styleOverrides: {
        root: {
          borderCollapse: 'separate',
          borderSpacing: 0,
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          fontWeight: 400,
          borderBottom: '1px solid #e0e0e0',
          padding: '24px 16px',
          fontSize: '1rem',
        },
        head: {
          backgroundColor: '#fafafa',
          fontWeight: 500,
          textTransform: 'uppercase',
          letterSpacing: '0.01em',
          fontSize: '0.875rem',
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: {
          '&:hover': {
            backgroundColor: '#fafafa',
          },
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 0,
          border: '1px solid #e0e0e0',
          fontWeight: 200,
        },
        standardSuccess: {
          backgroundColor: '#e8f0fe',
          color: '#1e3a5f',
          '& .MuiAlert-icon': {
            color: '#1e3a5f',
          },
        },
        standardInfo: {
          backgroundColor: '#e8f0fe',
          color: '#1e3a5f',
          '& .MuiAlert-icon': {
            color: '#1e3a5f',
          },
        },
        filledSuccess: {
          backgroundColor: '#1e3a5f',
        },
        filledInfo: {
          backgroundColor: '#1e3a5f',
        },
        outlinedSuccess: {
          borderColor: '#1e3a5f',
          color: '#1e3a5f',
          '& .MuiAlert-icon': {
            color: '#1e3a5f',
          },
        },
        outlinedInfo: {
          borderColor: '#1e3a5f',
          color: '#1e3a5f',
          '& .MuiAlert-icon': {
            color: '#1e3a5f',
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          fontWeight: 200,
        },
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: {
          fontWeight: 200,
          '&:hover': {
            backgroundColor: '#fafafa',
          },
          '&.Mui-selected': {
            backgroundColor: '#1e3a5f',
            color: '#ffffff',
            '&:hover': {
              backgroundColor: '#15304d',
            },
          },
        },
      },
    },
  },
});

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 6 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);
  const [selectedTender, setSelectedTender] = useState(null);
  const [companyStrengths, setCompanyStrengths] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [companyName, setCompanyName] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [individualPrediction, setIndividualPrediction] = useState(null);
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  
  const customTheme = useTheme();
  const isMobile = useMediaQuery(customTheme.breakpoints.down('md'));
  const isTablet = useMediaQuery(customTheme.breakpoints.down('lg'));

  useEffect(() => {
    // ログイン状態を確認
    const token = localStorage.getItem('token');
    const savedCompanyName = localStorage.getItem('company_name');
    if (token && savedCompanyName) {
      setIsLoggedIn(true);
      setCompanyName(savedCompanyName);
      fetchCompanyStrengths();
    } else {
      // デモ用の自動ログイン
      const demoLogin = async () => {
        try {
          const apiUrl = window.location.hostname.includes('azurewebsites.net') 
            ? 'https://app-bid-kacho-backend.azurewebsites.net' 
            : (process.env.REACT_APP_API_URL || 'http://localhost:8000');
          const response = await fetch(`${apiUrl}/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email: 'demo@example.com',
              password: 'demo123'
            }),
          });
          
          if (response.ok) {
            const data = await response.json();
            console.log('Demo login successful:', data);
            localStorage.setItem('token', data.token || data.access_token);
            localStorage.setItem('company_name', data.company_name || '星田建設株式会社');
            localStorage.setItem('company_id', String(data.company_id || '1'));
            setIsLoggedIn(true);
            setCompanyName(data.company_name || '星田建設株式会社');
            // Add a small delay before fetching company strengths
            setTimeout(() => {
              fetchCompanyStrengths();
            }, 500);
          } else {
            console.error('Demo login failed with status:', response.status);
          }
        } catch (error) {
          console.log('Demo login failed, showing login screen');
        }
      };
      demoLogin();
    }
  }, []);

  const handleLogin = (loginData) => {
    setIsLoggedIn(true);
    setCompanyName(loginData.company_name);
    fetchCompanyStrengths();
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('company_name');
    localStorage.removeItem('company_id');
    setIsLoggedIn(false);
    setCompanyName('');
    setSelectedTender(null);
    setCompanyStrengths(null);
    setTabValue(0);
    handleMenuClose();
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const fetchCompanyStrengths = async () => {
    try {
      const token = localStorage.getItem('token');
      console.log('Fetching company strengths with token:', token ? 'Token exists' : 'No token');
      const { companyAPI } = await import('./services/api');
      const data = await companyAPI.getCompanyStrengths();
      setCompanyStrengths(data);
    } catch (error) {
      console.error('Failed to fetch company strengths:', error);
      // If it's a 401, the mock data in the API will be used
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleTenderSelect = (tender) => {
    setSelectedTender(tender);
    setIndividualPrediction(null); // 前の予測結果をクリア
    setTabValue(1); // 予測タブに切り替え
  };

  // ログインしていない場合はログイン画面を表示
  if (!isLoggedIn) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Login onLogin={handleLogin} />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ 
        minHeight: '100vh',
        backgroundColor: '#ffffff',
        backgroundImage: `
          linear-gradient(rgba(0, 0, 0, 0.02) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0, 0, 0, 0.02) 1px, transparent 1px)
        `,
        backgroundSize: '20px 20px',
        backgroundPosition: '0 0, 0 0',
      }}>
        <AppBar position="fixed" elevation={0} sx={{ 
          top: 0,
          left: 0,
          right: 0,
          width: '100%',
          margin: 0,
          padding: 0,
          border: 'none',
        }}>
          <Toolbar sx={{ 
            py: { xs: 2, md: 4 }, 
            px: { xs: 2, md: 8 },
            margin: 0,
            minHeight: 'auto'
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
              <BiGlasses style={{ 
                fontSize: isMobile ? 24 : 32, 
                color: '#ffffff', 
                marginRight: isMobile ? 8 : 16 
              }} />
              <Typography 
                variant={isMobile ? "h5" : "h4"} 
                component="div" 
                sx={{ 
                  fontWeight: 300,
                  letterSpacing: '-0.01em',
                  color: '#ffffff',
                  fontSize: { xs: '1.5rem', md: '1.875rem' }
                }}
              >
                入札課長
              </Typography>
            </Box>
            
            {isMobile ? (
              <IconButton
                edge="end"
                color="inherit"
                aria-label="menu"
                onClick={() => setMobileDrawerOpen(true)}
                sx={{ ml: 2 }}
              >
                <MenuIcon />
              </IconButton>
            ) : (
              <Button
                color="inherit"
                onClick={handleMenuOpen}
                endIcon={<ArrowDropDownIcon sx={{ color: '#ffffff' }} />}
                sx={{
                  ml: 2,
                  textTransform: 'none',
                  fontWeight: 200,
                  letterSpacing: '0.01em',
                  color: '#ffffff',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    color: '#ffffff',
                  },
                }}
              >
                <AccountCircleIcon sx={{ mr: 1, color: '#ffffff' }} />
                {companyName}
              </Button>
            )}
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
            >
              <MenuItem onClick={handleLogout}>
                <LogoutIcon sx={{ mr: 1, fontSize: 18 }} />
                ログアウト
              </MenuItem>
            </Menu>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ 
          pt: { xs: 12, md: 20 }, 
          pb: { xs: 4, md: 8 },
          px: { xs: 1, sm: 2, md: 3 }
        }}>
          {!isMobile && (
            <Paper 
              elevation={0}
              sx={{ 
                mb: { xs: 4, md: 8 },
                backgroundColor: '#ffffff',
                borderBottom: '1px solid #e0e0e0',
              }}
            >
              <Tabs 
                value={tabValue} 
                onChange={handleTabChange} 
                centered={!isTablet}
                variant={isTablet ? "scrollable" : "standard"}
                scrollButtons={isTablet ? "auto" : false}
                allowScrollButtonsMobile
                sx={{ 
                  px: { xs: 1, md: 0 },
                  '& .MuiTab-root': {
                    py: { xs: 2, md: 4 },
                    px: { xs: 3, md: 6 },
                    minWidth: { xs: 140, md: 200 },
                    fontSize: { xs: '0.875rem', md: '1.1rem' },
                  }
                }}
              >
              <Tab 
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <FaSearch />
                    <span>案件検索</span>
                  </Box>
                } 
              />
              <Tab 
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <FaChartLine />
                    <span>個別予測</span>
                  </Box>
                } 
              />
              <Tab 
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <FaListUl />
                    <span>一括予測</span>
                  </Box>
                } 
              />
              <Tab 
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <FaBuilding />
                    <span>自社分析</span>
                  </Box>
                } 
              />
              <Tab 
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <FaDatabase />
                    <span>データ管理</span>
                  </Box>
                } 
              />
              </Tabs>
            </Paper>
          )}

          <TabPanel value={tabValue} index={0}>
            <TenderSearch onSelectTender={handleTenderSelect} />
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <PredictionDashboard 
              selectedTender={selectedTender}
              companyStrengths={companyStrengths}
              prediction={individualPrediction}
              setPrediction={setIndividualPrediction}
            />
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <BulkPrediction />
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            <CompanyStrengths strengths={companyStrengths} />
          </TabPanel>

          <TabPanel value={tabValue} index={4}>
            <CSVUpload />
          </TabPanel>
        </Container>
        
        {/* Mobile Drawer Navigation */}
        <Drawer
          anchor="right"
          open={mobileDrawerOpen}
          onClose={() => setMobileDrawerOpen(false)}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              width: 280,
              backgroundColor: '#ffffff',
              borderRight: '1px solid #e0e0e0',
            },
          }}
        >
          <Box sx={{ py: 2 }}>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              px: 2,
              pb: 2,
              borderBottom: '1px solid #e0e0e0'
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <BiGlasses style={{ fontSize: 24, color: '#1e3a5f', marginRight: 8 }} />
                <Typography variant="h6" sx={{ fontWeight: 400, color: '#212121' }}>
                  入札課長
                </Typography>
              </Box>
              <IconButton onClick={() => setMobileDrawerOpen(false)}>
                <CloseIcon />
              </IconButton>
            </Box>
            
            <List sx={{ pt: 2 }}>
              <ListItem
                button
                onClick={() => {
                  setTabValue(0);
                  setMobileDrawerOpen(false);
                }}
                selected={tabValue === 0}
                sx={{
                  py: 1.5,
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(66, 99, 235, 0.08)',
                    borderRight: '3px solid #1e3a5f',
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40, color: tabValue === 0 ? '#1e3a5f' : '#757575' }}>
                  <FaSearch size={18} />
                </ListItemIcon>
                <ListItemText 
                  primary="案件検索" 
                  primaryTypographyProps={{
                    fontSize: '1rem',
                    fontWeight: tabValue === 0 ? 500 : 400,
                    color: tabValue === 0 ? '#1e3a5f' : '#212121'
                  }}
                />
              </ListItem>
              
              <ListItem
                button
                onClick={() => {
                  setTabValue(1);
                  setMobileDrawerOpen(false);
                }}
                selected={tabValue === 1}
                sx={{
                  py: 1.5,
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(66, 99, 235, 0.08)',
                    borderRight: '3px solid #1e3a5f',
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40, color: tabValue === 1 ? '#1e3a5f' : '#757575' }}>
                  <FaChartLine size={18} />
                </ListItemIcon>
                <ListItemText 
                  primary="個別予測" 
                  primaryTypographyProps={{
                    fontSize: '1rem',
                    fontWeight: tabValue === 1 ? 500 : 400,
                    color: tabValue === 1 ? '#1e3a5f' : '#212121'
                  }}
                />
              </ListItem>
              
              <ListItem
                button
                onClick={() => {
                  setTabValue(2);
                  setMobileDrawerOpen(false);
                }}
                selected={tabValue === 2}
                sx={{
                  py: 1.5,
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(66, 99, 235, 0.08)',
                    borderRight: '3px solid #1e3a5f',
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40, color: tabValue === 2 ? '#1e3a5f' : '#757575' }}>
                  <FaListUl size={18} />
                </ListItemIcon>
                <ListItemText 
                  primary="一括予測" 
                  primaryTypographyProps={{
                    fontSize: '1rem',
                    fontWeight: tabValue === 2 ? 500 : 400,
                    color: tabValue === 2 ? '#1e3a5f' : '#212121'
                  }}
                />
              </ListItem>
              
              <ListItem
                button
                onClick={() => {
                  setTabValue(3);
                  setMobileDrawerOpen(false);
                }}
                selected={tabValue === 3}
                sx={{
                  py: 1.5,
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(66, 99, 235, 0.08)',
                    borderRight: '3px solid #1e3a5f',
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40, color: tabValue === 3 ? '#1e3a5f' : '#757575' }}>
                  <FaBuilding size={18} />
                </ListItemIcon>
                <ListItemText 
                  primary="自社分析" 
                  primaryTypographyProps={{
                    fontSize: '1rem',
                    fontWeight: tabValue === 3 ? 500 : 400,
                    color: tabValue === 3 ? '#1e3a5f' : '#212121'
                  }}
                />
              </ListItem>
              
              <ListItem
                button
                onClick={() => {
                  setTabValue(4);
                  setMobileDrawerOpen(false);
                }}
                selected={tabValue === 4}
                sx={{
                  py: 1.5,
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(66, 99, 235, 0.08)',
                    borderRight: '3px solid #1e3a5f',
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40, color: tabValue === 4 ? '#1e3a5f' : '#757575' }}>
                  <FaDatabase size={18} />
                </ListItemIcon>
                <ListItemText 
                  primary="データ管理" 
                  primaryTypographyProps={{
                    fontSize: '1rem',
                    fontWeight: tabValue === 4 ? 500 : 400,
                    color: tabValue === 4 ? '#1e3a5f' : '#212121'
                  }}
                />
              </ListItem>
            </List>
            
            <Divider sx={{ mt: 2, mb: 2 }} />
            
            {/* Company Info and Logout */}
            <Box sx={{ px: 2 }}>
              <Box sx={{ 
                p: 2, 
                mb: 2,
                backgroundColor: '#f5f5f5',
                borderRadius: 1
              }}>
                <Typography variant="caption" sx={{ color: '#757575', display: 'block', mb: 1 }}>
                  ログイン中
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 500, color: '#212121' }}>
                  {companyName}
                </Typography>
              </Box>
              
              <ListItem
                button
                onClick={() => {
                  handleLogout();
                  setMobileDrawerOpen(false);
                }}
                sx={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e0e0e0',
                  borderRadius: 1,
                  '&:hover': {
                    backgroundColor: '#f5f5f5',
                  }
                }}
              >
                <ListItemIcon>
                  <LogoutIcon sx={{ color: '#757575' }} />
                </ListItemIcon>
                <ListItemText primary="ログアウト" />
              </ListItem>
            </Box>
          </Box>
        </Drawer>
      </Box>
    </ThemeProvider>
  );
}

export default App;