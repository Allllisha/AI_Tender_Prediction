import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert,
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell } from 'recharts';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import BusinessIcon from '@mui/icons-material/Business';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

function CompanyStrengths({ strengths }) {
  if (!strengths) {
    return (
      <Paper 
        sx={{ 
          p: { xs: 4, md: 8 }, 
          textAlign: 'center',
          backgroundColor: '#ffffff',
          border: '1px solid #e0e0e0',
        }}
        elevation={0}
      >
        <Typography variant="h5" sx={{ color: '#757575', mb: 2, fontWeight: 200 }}>
          データを読み込み中...
        </Typography>
        <LinearProgress />
      </Paper>
    );
  }

  const formatPrice = (price) => {
    if (price >= 100000000) {
      // 億単位の場合、小数点以下の処理を改善
      const oku = price / 100000000;
      if (oku >= 1000) {
        // 1000億以上
        return `${oku.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}億円`;
      } else if (oku >= 100) {
        // 100億以上
        return `${oku.toFixed(0)}億円`;
      } else {
        // 100億未満
        return `${oku.toFixed(1)}億円`;
      }
    } else if (price >= 10000000) {
      return `${(price / 10000000).toFixed(1)}千万円`;
    } else {
      return `${(price / 1000000).toFixed(1)}百万円`;
    }
  };

  // 都道府県データをグラフ用に変換
  const prefectureData = Object.entries(strengths.prefectures || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([name, value]) => ({ name, value }));

  // 用途別データをグラフ用に変換
  const useTypeData = Object.entries(strengths.use_types || {})
    .sort((a, b) => b[1] - a[1])
    .map(([name, value]) => ({ name, value }));

  // 入札方式データをグラフ用に変換
  const bidMethodData = Object.entries(strengths.bid_methods || {})
    .map(([name, value]) => ({ name, value }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  return (
    <Box>
      {/* ヘッダー */}
      <Box sx={{ mb: { xs: 4, sm: 6, md: 8 }, borderBottom: '1px solid #e0e0e0', pb: { xs: 2, sm: 3, md: 4 } }}>
        <Typography 
          variant="h2" 
          sx={{ 
            fontWeight: 100, 
            letterSpacing: '0.02em',
            mb: { xs: 1, md: 2 },
            color: '#212121'
          }}
        >
          自社分析
        </Typography>
        <Typography variant="h6" sx={{ fontWeight: 200, color: '#757575' }}>
          過去の落札実績に基づく自社の強み分析
        </Typography>
      </Box>
      
      {/* 基本統計 */}
      <Box sx={{ mb: { xs: 6, md: 8 } }}>
        <Typography 
          variant="h5" 
          sx={{ 
            fontWeight: 200, 
            letterSpacing: '0.005em',
            mb: { xs: 3, md: 4 },
            color: '#212121',
            fontSize: { xs: '1.25rem', md: '1.5rem' }
          }}
        >
          実績概要
        </Typography>
        <Grid container spacing={{ xs: 3, md: 6 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper 
              elevation={0}
              sx={{
                p: { xs: 3, md: 4 },
                textAlign: 'center',
                backgroundColor: '#ffffff',
                border: '1px solid #e0e0e0',
              }}
            >
              <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em', fontSize: { xs: '0.7rem', md: '0.75rem' } }}>
                総落札件数
              </Typography>
              <Typography variant="h2" sx={{ fontWeight: 100, color: '#212121', my: 2, fontSize: { xs: '2rem', md: '3rem' } }}>
                {strengths.total_awards}
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 200, color: '#757575', fontSize: { xs: '0.9rem', md: '1rem' } }}>
                件
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper 
              elevation={0}
              sx={{
                p: { xs: 3, md: 4 },
                textAlign: 'center',
                backgroundColor: '#ffffff',
                border: '1px solid #0a6e4a',
              }}
            >
              <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em', fontSize: { xs: '0.7rem', md: '0.75rem' } }}>
                総落札額
              </Typography>
              <Typography variant="h2" sx={{ fontWeight: 100, color: '#0a6e4a', my: 2, fontSize: { xs: '2rem', md: '3rem' } }}>
                {(strengths.total_amount / 100000000).toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}億
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 200, color: '#757575', fontSize: { xs: '0.9rem', md: '1rem' } }}>
                円
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper 
              elevation={0}
              sx={{
                p: { xs: 3, md: 4 },
                textAlign: 'center',
                backgroundColor: '#ffffff',
                border: '1px solid #e0e0e0',
              }}
            >
              <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em', fontSize: { xs: '0.7rem', md: '0.75rem' } }}>
                平均落札額
              </Typography>
              <Typography variant="h2" sx={{ fontWeight: 100, color: '#212121', my: 2, fontSize: { xs: '2rem', md: '3rem' } }}>
                {(strengths.avg_amount / 100000000).toFixed(1)}億
              </Typography>
              <Typography variant="body2" sx={{ color: '#757575', fontWeight: 200, fontSize: { xs: '0.9rem', md: '1rem' } }}>
                円
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper 
              elevation={0}
              sx={{
                p: { xs: 3, md: 4 },
                textAlign: 'center',
                backgroundColor: '#ffffff',
                border: '1px solid #e0e0e0',
              }}
            >
              <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em', fontSize: { xs: '0.7rem', md: '0.75rem' } }}>
                平均落札率
              </Typography>
              <Typography variant="h2" sx={{ fontWeight: 100, color: '#212121', my: 2, fontSize: { xs: '2rem', md: '3rem' } }}>
                {strengths.avg_win_rate?.toFixed(1)}%
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </Box>

      {/* 地域別実績 */}
      <Grid container spacing={{ xs: 3, md: 6 }} sx={{ mb: { xs: 6, md: 8 } }}>
        <Grid item xs={12} md={6}>
          <Paper 
            elevation={0}
            sx={{
              p: { xs: 4, md: 6 },
              backgroundColor: '#ffffff',
              border: '1px solid #e0e0e0',
            }}
          >
            <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em', mb: 3, display: 'block', fontSize: { xs: '0.7rem', md: '0.75rem' } }}>
              地域別実績
            </Typography>
            {strengths.strongest_prefecture && (
              <Typography variant="h6" sx={{ fontWeight: 300, color: '#0a6e4a', mb: 4, fontSize: { xs: '1.1rem', md: '1.25rem' } }}>
                最強エリア: {strengths.strongest_prefecture}
              </Typography>
            )}
            <Box sx={{ '& > div': { mb: 3 } }}>
              {prefectureData.slice(0, 5).map((pref, index) => (
                <Box key={pref.name} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body1" sx={{ fontWeight: 200, color: '#212121', fontSize: { xs: '0.9rem', md: '1rem' } }}>
                    {pref.name}
                  </Typography>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      fontWeight: 200, 
                      color: index === 0 ? '#0a6e4a' : '#757575',
                      fontSize: { xs: '1rem', md: '1.25rem' }
                    }}
                  >
                    {pref.value}件
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper 
            elevation={0}
            sx={{
              p: { xs: 4, md: 6 },
              backgroundColor: '#ffffff',
              border: '1px solid #e0e0e0',
            }}
          >
            <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em', mb: 3, display: 'block', fontSize: { xs: '0.7rem', md: '0.75rem' } }}>
              用途別実績
            </Typography>
            {strengths.strongest_use_type && (
              <Typography variant="h6" sx={{ fontWeight: 300, color: '#0a6e4a', mb: 4, fontSize: { xs: '1.1rem', md: '1.25rem' } }}>
                得意分野: {strengths.strongest_use_type}
              </Typography>
            )}
            <Box sx={{ '& > div': { mb: 3 } }}>
              {useTypeData.slice(0, 5).map((type, index) => (
                <Box key={type.name} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body1" sx={{ fontWeight: 200, color: '#212121', fontSize: { xs: '0.9rem', md: '1rem' } }}>
                    {type.name}
                  </Typography>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      fontWeight: 200, 
                      color: index === 0 ? '#0a6e4a' : '#757575',
                      fontSize: { xs: '1rem', md: '1.25rem' }
                    }}
                  >
                    {type.value}件
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* 入札方式別実績と推奨戦略 */}
      <Grid container spacing={{ xs: 3, md: 6 }}>
        <Grid item xs={12} md={6}>
          <Paper 
            elevation={0}
            sx={{
              p: { xs: 4, md: 6 },
              backgroundColor: '#ffffff',
              border: '1px solid #e0e0e0',
            }}
          >
            <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em', mb: 3, display: 'block', fontSize: { xs: '0.7rem', md: '0.75rem' } }}>
              入札方式別実績
            </Typography>
            <Box sx={{ '& > div': { mb: 3 } }}>
              {bidMethodData.map((method, index) => (
                <Box key={method.name} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body1" sx={{ fontWeight: 200, color: '#212121', fontSize: { xs: '0.9rem', md: '1rem' } }}>
                    {method.name}
                  </Typography>
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      fontWeight: 200, 
                      color: '#757575',
                      fontSize: { xs: '0.9rem', md: '1rem' }
                    }}
                  >
                    {method.value}件 ({Math.round((method.value / strengths.total_awards) * 100)}%)
                  </Typography>
                </Box>
              ))}
            </Box>
            {strengths.avg_tech_score && (
              <Box sx={{ mt: 4, pt: 4, borderTop: '1px solid #e0e0e0' }}>
                <Typography variant="body1" sx={{ fontWeight: 200, color: '#212121' }}>
                  総合評価方式での平均技術点: {strengths.avg_tech_score.toFixed(1)}点
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper 
            elevation={0}
            sx={{
              p: { xs: 4, md: 6 },
              backgroundColor: '#ffffff',
              border: '1px solid #e0e0e0',
            }}
          >
            <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em', mb: 3, display: 'block', fontSize: { xs: '0.7rem', md: '0.75rem' } }}>
              推奨戦略
            </Typography>
            <Box sx={{ '& > div': { mb: 3 } }}>
              {strengths.strongest_prefecture && (
                <Box>
                  <Typography variant="body1" sx={{ fontWeight: 300, color: '#212121', mb: 1 }}>
                    {strengths.strongest_prefecture}での案件に注力
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 200, color: '#757575' }}>
                    最も実績のある地域です
                  </Typography>
                </Box>
              )}
              {strengths.strongest_use_type && (
                <Box>
                  <Typography variant="body1" sx={{ fontWeight: 300, color: '#212121', mb: 1 }}>
                    {strengths.strongest_use_type}案件を優先
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 200, color: '#757575' }}>
                    得意分野での勝率が高いです
                  </Typography>
                </Box>
              )}
              {strengths.avg_tech_score > 80 && (
                <Box>
                  <Typography variant="body1" sx={{ fontWeight: 300, color: '#212121', mb: 1 }}>
                    総合評価方式の案件を狙う
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 200, color: '#757575' }}>
                    技術点が高く有利です
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default CompanyStrengths;