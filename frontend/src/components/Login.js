import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  Container,
  InputAdornment,
  IconButton,
} from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { BiGlasses } from 'react-icons/bi';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LockIcon from '@mui/icons-material/Lock';

function Login({ onLogin }) {
  const [credentials, setCredentials] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (field) => (event) => {
    setCredentials({
      ...credentials,
      [field]: event.target.value,
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!credentials.email || !credentials.password) {
      setError('メールアドレスとパスワードを入力してください');
      return;
    }

    setLoading(true);
    try {
      const apiUrl = window.location.hostname.includes('azurewebsites.net') 
        ? 'https://app-bid-kacho-backend.azurewebsites.net' 
        : (import.meta.env.VITE_API_URL || 'http://localhost:8000');
      const response = await fetch(`${apiUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        const data = await response.json();
        // トークンとユーザー情報を保存
        localStorage.setItem('token', data.token);
        localStorage.setItem('company_name', data.company_name);
        localStorage.setItem('company_id', data.company_id);
        onLogin(data);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'ログインに失敗しました');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('ログインに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = (companyType) => {
    // デモアカウントは統一
    setCredentials({
      email: 'demo@example.com',
      password: 'demo123',
    });
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#ffffff',
        backgroundImage: `
          linear-gradient(rgba(0, 0, 0, 0.02) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0, 0, 0, 0.02) 1px, transparent 1px)
        `,
        backgroundSize: '20px 20px',
        backgroundPosition: '0 0, 0 0',
        px: { xs: 2, sm: 0 },
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={0}
          sx={{
            p: { xs: 4, sm: 6, md: 8 },
            backgroundColor: '#ffffff',
            border: '1px solid #e0e0e0',
            mx: { xs: 0, sm: 'auto' },
          }}
        >
          {/* ロゴエリア */}
          <Box sx={{ textAlign: 'center', mb: { xs: 4, md: 6 } }}>
            <BiGlasses style={{ fontSize: 48, color: '#1b5e20', marginBottom: 16 }} />
            <Typography
              variant="h3"
              sx={{
                fontWeight: 100,
                letterSpacing: '0.02em',
                color: '#212121',
                mb: 1,
                fontSize: { xs: '2rem', md: '3rem' },
              }}
            >
              入札課長
            </Typography>
            <Typography
              variant="body1"
              sx={{
                fontWeight: 200,
                color: '#757575',
                fontSize: { xs: '0.9rem', md: '1rem' },
              }}
            >
              AI入札検索＆勝率予測ツール
            </Typography>
          </Box>

          {/* ログインフォーム */}
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              type="email"
              label="メールアドレス"
              value={credentials.email}
              onChange={handleChange('email')}
              sx={{ mb: { xs: 2, md: 3 } }}
              size="medium"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <AccountCircleIcon sx={{ color: '#757575' }} />
                  </InputAdornment>
                ),
              }}
              disabled={loading}
            />

            <TextField
              fullWidth
              type={showPassword ? 'text' : 'password'}
              label="パスワード"
              value={credentials.password}
              onChange={handleChange('password')}
              sx={{ mb: { xs: 3, md: 4 } }}
              size="medium"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LockIcon sx={{ color: '#757575' }} />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                      size="small"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              disabled={loading}
            />

            {error && (
              <Alert 
                severity="error" 
                sx={{ 
                  mb: { xs: 2, md: 3 },
                  fontSize: { xs: '0.85rem', md: '1rem' }
                }}
              >
                {error}
              </Alert>
            )}

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{
                py: { xs: 1.5, md: 2 },
                fontSize: { xs: '0.9rem', md: '1rem' },
                fontWeight: 200,
                letterSpacing: '0.02em',
                backgroundColor: '#1b5e20',
                '&:hover': {
                  backgroundColor: '#2e7d32',
                },
              }}
            >
              {loading ? 'ログイン中...' : 'ログイン'}
            </Button>
          </form>

          {/* デモアクセス */}
          <Box sx={{ mt: { xs: 4, md: 6 }, pt: { xs: 3, md: 4 }, borderTop: '1px solid #e0e0e0' }}>
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                textAlign: 'center',
                color: '#757575',
                fontWeight: 200,
                mb: 2,
                fontSize: { xs: '0.7rem', md: '0.75rem' },
              }}
            >
              デモアカウントでログイン
            </Typography>
            <Box>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => handleDemoLogin()}
                disabled={loading}
                size="medium"
                sx={{
                  py: { xs: 1, md: 1.5 },
                  fontSize: { xs: '0.85rem', md: '1rem' },
                  fontWeight: 200,
                  borderColor: '#1b5e20',
                  color: '#1b5e20',
                  '&:hover': {
                    borderColor: '#2e7d32',
                    backgroundColor: 'rgba(27, 94, 32, 0.04)',
                  },
                }}
              >
                デモアカウントでログイン
              </Button>
            </Box>
          </Box>
        </Paper>

        {/* フッター */}
        <Typography
          variant="caption"
          sx={{
            display: 'block',
            textAlign: 'center',
            mt: { xs: 3, md: 4 },
            color: '#757575',
            fontWeight: 200,
            fontSize: { xs: '0.7rem', md: '0.75rem' },
          }}
        >
          © 2025 入札課長
        </Typography>
      </Container>
    </Box>
  );
}

export default Login;