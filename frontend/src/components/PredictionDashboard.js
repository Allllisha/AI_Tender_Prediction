import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  Alert,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Card,
  CardContent,
  Divider,
  Rating,
  Tooltip,
  Fade,
  Zoom,
  Stack,
} from '@mui/material';
import ReactMarkdown from 'react-markdown';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import CalculateIcon from '@mui/icons-material/Calculate';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import BusinessIcon from '@mui/icons-material/Business';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import AssessmentIcon from '@mui/icons-material/Assessment';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import PriceInput from './common/PriceInput';
import { predictionAPI } from '../services/api';

function PredictionDashboard({ selectedTender, companyStrengths, prediction, setPrediction }) {
  const [bidAmount, setBidAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 案件が選択されたら最低制限価格を初期値として設定
  useEffect(() => {
    if (selectedTender) {
      // 最低制限価格があればそれを、なければ予定価格の90%を初期値とする
      if (selectedTender.minimum_price) {
        setBidAmount(selectedTender.minimum_price);
      } else if (selectedTender.estimated_price) {
        // 最低制限価格がない場合は予定価格の90%を初期値とする
        setBidAmount(Math.floor(selectedTender.estimated_price * 0.9));
      }
      // 案件が変わったら前の予測結果をクリア
      setPrediction(null);
      setError(null);
    }
  }, [selectedTender, setPrediction]);

  const handlePredict = async () => {
    if (!selectedTender || !bidAmount) {
      setError('案件と入札額を入力してください');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      // ログインしている会社名を使用（デフォルトは「いであ株式会社」）
      const companyName = localStorage.getItem('company_name') || 'いであ株式会社';
      const result = await predictionAPI.predictSingle(
        selectedTender.tender_id,
        parseInt(bidAmount),
        companyName
      );
      setPrediction(result);
    } catch (err) {
      setError('予測に失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    if (!price && price !== 0) return '―';
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const formatArea = (area) => {
    if (!area) return '―';
    return new Intl.NumberFormat('ja-JP').format(area) + ' ㎡';
  };

  const getRankColor = (rank) => {
    const colors = {
      A: '#1e3a5f',
      B: '#2a4a6f',
      C: '#ffc107',
      D: '#ff9800',
      E: '#f44336',
    };
    return colors[rank] || '#9e9e9e';
  };

  const getRankDescription = (rank) => {
    const descriptions = {
      A: '非常に有望',
      B: '有望',
      C: '妥当',
      D: 'やや不利',
      E: '困難',
    };
    return descriptions[rank] || '―';
  };

  const getConfidenceIcon = (confidence) => {
    if (confidence === 'high') return <CheckCircleIcon sx={{ color: '#1e3a5f' }} />;
    if (confidence === 'medium') return <InfoIcon sx={{ color: '#1e3a5f' }} />;
    return <WarningIcon color="warning" />;
  };

  const getConfidenceLabel = (confidence) => {
    const labels = {
      high: '高',
      medium: '中',
      low: '低',
    };
    return labels[confidence] || confidence;
  };

  const getRiskIcon = (risk) => {
    if (risk.includes('最低制限価格')) return <ErrorIcon color="error" />;
    if (risk.includes('激戦区')) return <WarningIcon color="warning" />;
    return <InfoIcon color="info" />;
  };

  if (!selectedTender) {
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
          案件が選択されていません
        </Typography>
        <Typography variant="body1" sx={{ color: '#757575', fontWeight: 200 }}>
          案件検索タブから案件を選択してください
        </Typography>
      </Paper>
    );
  }

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
          個別予測
        </Typography>
        <Typography variant="h6" sx={{ fontWeight: 200, color: '#757575' }}>
          選択された案件の勝率を詳細分析
        </Typography>
      </Box>

      {/* 案件情報 */}
      <Paper 
        elevation={0}
        sx={{ 
          p: { xs: 3, md: 6 }, 
          mb: { xs: 3, md: 6 },
          backgroundColor: '#ffffff',
          border: '1px solid #e0e0e0',
        }}
      >
        <Typography 
          variant="h4" 
          sx={{ 
            fontWeight: 200, 
            letterSpacing: '0.005em',
            mb: 4,
            color: '#212121'
          }}
        >
          {selectedTender.title}
        </Typography>
        
        <Grid container spacing={{ xs: 2, md: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em' }}>
              地域
            </Typography>
            <Typography variant="body1" sx={{ mt: 1, fontWeight: 200, fontSize: { xs: '0.9rem', md: '1rem' } }}>
              {selectedTender.prefecture} {selectedTender.municipality}
            </Typography>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em' }}>
              発注者
            </Typography>
            <Typography variant="body1" sx={{ mt: 1, fontWeight: 200, fontSize: { xs: '0.9rem', md: '1rem' } }}>
              {selectedTender.publisher}
            </Typography>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em' }}>
              入札日
            </Typography>
            <Typography variant="body1" sx={{ mt: 1, fontWeight: 200, fontSize: { xs: '0.9rem', md: '1rem' } }}>
              {selectedTender.bid_date}
            </Typography>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em' }}>
              予定価格
            </Typography>
            <Typography variant="h6" sx={{ mt: 1, fontWeight: 300, color: '#1e3a5f', fontSize: { xs: '1.1rem', md: '1.25rem' } }}>
              {formatPrice(selectedTender.estimated_price)}
            </Typography>
          </Grid>
        </Grid>

        <Box sx={{ mt: { xs: 3, md: 4 }, pt: { xs: 3, md: 4 }, borderTop: '1px solid #e0e0e0', display: 'flex', gap: { xs: 2, md: 3 }, flexWrap: 'wrap' }}>
          <Chip
            label={selectedTender.use_type}
            sx={{ fontWeight: 200 }}
          />
          <Chip
            label={selectedTender.bid_method}
            sx={{ fontWeight: 200 }}
          />
          {selectedTender.floor_area_m2 && (
            <Chip
              label={`延床 ${formatArea(selectedTender.floor_area_m2)}`}
              sx={{ fontWeight: 200 }}
            />
          )}
        </Box>
      </Paper>

      {/* 入札額入力 */}
      <Paper 
        sx={{ 
          p: { xs: 3, md: 6 }, 
          mb: { xs: 3, md: 6 },
          backgroundColor: '#ffffff',
          border: '1px solid #e0e0e0',
        }} 
        elevation={0}
      >
        <Typography 
          variant="h5" 
          sx={{
            fontWeight: 200,
            letterSpacing: '0.005em',
            mb: 4,
            color: '#212121'
          }}
        >
          入札額シミュレーション
        </Typography>
        
        <Grid container spacing={{ xs: 2, md: 4 }} alignItems="flex-end">
          <Grid item xs={12} md={6}>
            <PriceInput
              label="入札予定額"
              value={bidAmount}
              onChange={(e) => setBidAmount(e.target.value)}
              step={10000000}
              min={selectedTender.minimum_price || 0}
              max={selectedTender.estimated_price}
              helperText={
                selectedTender.minimum_price
                  ? `最低制限価格: ${formatPrice(selectedTender.minimum_price)}`
                  : null
              }
              required
              size="medium"
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            {bidAmount && (
              <Box>
                <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em' }}>
                  予定価格比
                </Typography>
                <Typography variant="h6" sx={{ mt: 1, fontWeight: 300, color: '#1e3a5f', fontSize: { xs: '1.1rem', md: '1.25rem' } }}>
                  {Math.round((parseInt(bidAmount) / selectedTender.estimated_price) * 100)}%
                </Typography>
              </Box>
            )}
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              onClick={handlePredict}
              disabled={loading || !bidAmount}
              sx={{
                py: { xs: 2, md: 3 },
                fontSize: { xs: '0.9rem', md: '1rem' },
                fontWeight: 200,
                letterSpacing: '0.02em',
              }}
            >
              予測実行
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {loading && (
        <Fade in={loading}>
          <Box sx={{ mb: 4 }}>
            <LinearProgress sx={{ mb: 2 }} />
            <Typography 
              variant="h6" 
              sx={{ 
                textAlign: 'center', 
                color: '#424242', 
                fontWeight: 200,
                fontSize: '1.2rem',
                letterSpacing: '0.05em',
                animation: 'pulse 1.5s ease-in-out infinite',
                '@keyframes pulse': {
                  '0%': { opacity: 0.6 },
                  '50%': { opacity: 1 },
                  '100%': { opacity: 0.6 },
                }
              }}
            >
              予測中...
            </Typography>
            <Typography 
              variant="body2" 
              sx={{ 
                textAlign: 'center', 
                color: '#9e9e9e', 
                fontWeight: 200,
                mt: 1
              }}
            >
              AIが類似案件を分析しています
            </Typography>
          </Box>
        </Fade>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* 予測結果 */}
      {prediction && (
        <Box>
          <Box sx={{ mb: 6, borderBottom: '1px solid #e0e0e0', pb: 4 }}>
            <Typography 
              variant="h3" 
              sx={{ 
                fontWeight: 100, 
                letterSpacing: '0.02em',
                mb: 1,
                color: '#212121'
              }}
            >
              予測結果
            </Typography>
          </Box>

          <Grid container spacing={{ xs: 3, md: 6 }}>
            {/* メイン結果 */}
            <Grid item xs={12} sm={6} md={4}>
              <Paper 
                elevation={0}
                sx={{
                  p: { xs: 4, md: 6 },
                  textAlign: 'center',
                  backgroundColor: '#ffffff',
                  border: '1px solid #e0e0e0',
                }}
              >
                <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em' }}>
                  予測ランク
                </Typography>
                <Typography 
                  variant="h1" 
                  sx={{ 
                    fontWeight: 'bold', 
                    color: getRankColor(prediction.rank),
                    my: 3,
                    textShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    fontSize: '5rem'
                  }}
                >
                  {prediction.rank}
                </Typography>
                <Chip 
                  label={getRankDescription(prediction.rank)}
                  sx={{ 
                    backgroundColor: getRankColor(prediction.rank),
                    color: 'white',
                    fontWeight: 'bold',
                    fontSize: '1rem',
                    px: 2,
                    py: 0.5
                  }}
                />
              </Paper>
            </Grid>

            {/* 勝率 */}
            <Grid item xs={12} sm={6} md={4}>
              <Paper 
                elevation={0}
                sx={{
                  p: { xs: 4, md: 6 },
                  textAlign: 'center',
                  backgroundColor: '#ffffff',
                  border: '1px solid #e0e0e0',
                }}
              >
                <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em' }}>
                  勝率予測
                </Typography>
                <Typography 
                  variant="h1" 
                  sx={{ 
                    fontWeight: 100, 
                    color: prediction.win_probability >= 0.5 ? '#1e3a5f' : '#757575',
                    my: 3
                  }}
                >
                  {Math.round(prediction.win_probability * 100)}%
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 200, color: '#757575' }}>
                  信頼度: {getConfidenceLabel(prediction.confidence)}
                </Typography>
              </Paper>
            </Grid>

            {/* 分析基準 */}
            <Grid item xs={12} md={4}>
              <Paper 
                elevation={0}
                sx={{
                  p: { xs: 4, md: 6 },
                  backgroundColor: '#ffffff',
                  border: '1px solid #e0e0e0',
                }}
              >
                <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em', mb: 3, display: 'block' }}>
                  分析基準
                </Typography>
                <Box sx={{ '& > div': { mb: 3 } }}>
                  <Box>
                    <Typography variant="body2" sx={{ color: '#757575', fontWeight: 200 }}>
                      類似案件数
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 200 }}>
                      {prediction.basis.n_similar || 0}件
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" sx={{ color: '#757575', fontWeight: 200 }}>
                      類似案件中央値
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 200 }}>
                      {formatPrice(prediction.basis.similar_median)}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" sx={{ color: '#757575', fontWeight: 200 }}>
                      価格差
                    </Typography>
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        fontWeight: 200,
                        color: prediction.basis.price_gap > 0 ? '#757575' : '#1e3a5f'
                      }}
                    >
                      {formatPrice(Math.abs(prediction.basis.price_gap))}
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </Grid>

            {/* 判断理由 */}
            {prediction.judgment_reason && (
              <Grid item xs={12}>
                <Paper 
                  elevation={0}
                  sx={{
                    p: { xs: 4, md: 6 },
                    backgroundColor: '#f8f8f8',
                    border: '1px solid #e0e0e0',
                  }}
                >
                  <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em', mb: 3, display: 'block' }}>
                    AI判断理由
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 200, color: '#212121', lineHeight: 1.8 }}>
                    {prediction.judgment_reason}
                  </Typography>
                </Paper>
              </Grid>
            )}

            {/* リスク要因 */}
            {prediction.risk_notes && prediction.risk_notes.length > 0 && (
              <Grid item xs={12}>
                <Paper 
                  elevation={0}
                  sx={{
                    p: { xs: 4, md: 6 },
                    backgroundColor: '#ffffff',
                    border: '1px solid #e0e0e0',
                  }}
                >
                  <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em', mb: 3, display: 'block' }}>
                    リスク要因
                  </Typography>
                  <Box sx={{ '& > div': { mb: 2 } }}>
                    {prediction.risk_notes.map((risk, index) => (
                      <Typography key={index} variant="body1" sx={{ fontWeight: 200, color: '#212121' }}>
                        • {risk}
                      </Typography>
                    ))}
                  </Box>
                </Paper>
              </Grid>
            )}

            {/* 推奨事項 */}
            <Grid item xs={12}>
              <Paper 
                elevation={0}
                sx={{
                  p: { xs: 4, md: 6 },
                  backgroundColor: prediction.rank === 'A' || prediction.rank === 'B' ? '#f5f5f5' : '#ffffff',
                  border: `2px solid ${getRankColor(prediction.rank)}`,
                  borderRadius: 2,
                }}
              >
                <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em', mb: 3, display: 'block' }}>
                  推奨事項
                </Typography>
                <Box 
                  sx={{ 
                    maxHeight: '600px', 
                    overflowY: 'auto',
                    '& h3': { 
                      fontSize: '1.2rem', 
                      fontWeight: 500, 
                      color: '#212121',
                      mt: 2,
                      mb: 1
                    },
                    '& h4': { 
                      fontSize: '1.1rem', 
                      fontWeight: 500, 
                      color: '#424242',
                      mt: 2,
                      mb: 1
                    },
                    '& p': { 
                      fontSize: '0.95rem',
                      fontWeight: 200, 
                      color: '#212121', 
                      lineHeight: 1.6,
                      mb: 1
                    },
                    '& ul': {
                      pl: 3,
                      mb: 1
                    },
                    '& li': {
                      fontSize: '0.95rem',
                      fontWeight: 200,
                      color: '#212121',
                      lineHeight: 1.6,
                      mb: 0.5
                    },
                    '& strong': {
                      fontWeight: 500
                    }
                  }}
                >
                  <ReactMarkdown>{prediction.recommendation}</ReactMarkdown>
                </Box>
              </Paper>
            </Grid>

            {/* 類似案件詳細 */}
            {prediction.similar_cases && prediction.similar_cases.length > 0 && (
              <Grid item xs={12}>
                <Paper 
                  elevation={0}
                  sx={{
                    p: { xs: 3, md: 6 },
                    backgroundColor: '#ffffff',
                    border: '1px solid #e0e0e0',
                  }}
                >
                  <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, textTransform: 'uppercase', letterSpacing: '0.02em', mb: 3, display: 'block' }}>
                    類似案件の落札実績
                  </Typography>
                  <Box sx={{ 
                    overflowX: 'auto',
                    '&::-webkit-scrollbar': {
                      height: '8px',
                    },
                    '&::-webkit-scrollbar-track': {
                      backgroundColor: '#f5f5f5',
                    },
                    '&::-webkit-scrollbar-thumb': {
                      backgroundColor: '#bdbdbd',
                      borderRadius: '4px',
                      '&:hover': {
                        backgroundColor: '#9e9e9e',
                      },
                    },
                  }}>
                    <table style={{ 
                      minWidth: '800px', 
                      width: '100%', 
                      borderCollapse: 'collapse',
                      fontSize: 'clamp(0.75rem, 2vw, 1rem)'
                    }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid #e0e0e0' }}>
                          <th style={{ 
                            padding: '12px', 
                            textAlign: 'left', 
                            fontWeight: 200, 
                            color: '#757575',
                            minWidth: '150px',
                            whiteSpace: 'nowrap'
                          }}>落札企業</th>
                          <th style={{ 
                            padding: '12px', 
                            textAlign: 'right', 
                            fontWeight: 200, 
                            color: '#757575',
                            minWidth: '120px',
                            whiteSpace: 'nowrap'
                          }}>落札価格</th>
                          <th style={{ 
                            padding: '12px', 
                            textAlign: 'left', 
                            fontWeight: 200, 
                            color: '#757575',
                            minWidth: '100px',
                            whiteSpace: 'nowrap'
                          }}>地域</th>
                          <th style={{ 
                            padding: '12px', 
                            textAlign: 'left', 
                            fontWeight: 200, 
                            color: '#757575',
                            minWidth: '100px',
                            whiteSpace: 'nowrap'
                          }}>用途</th>
                          <th style={{ 
                            padding: '12px', 
                            textAlign: 'left', 
                            fontWeight: 200, 
                            color: '#757575',
                            minWidth: '120px',
                            whiteSpace: 'nowrap'
                          }}>入札方式</th>
                          <th style={{ 
                            padding: '12px', 
                            textAlign: 'left', 
                            fontWeight: 200, 
                            color: '#757575',
                            minWidth: '100px',
                            whiteSpace: 'nowrap'
                          }}>時期</th>
                        </tr>
                      </thead>
                      <tbody>
                        {prediction.similar_cases.map((caseItem, index) => (
                          <tr key={index} style={{ borderBottom: '1px solid #f0f0f0' }}>
                            <td style={{ 
                              padding: '12px', 
                              fontWeight: 200,
                              whiteSpace: 'nowrap',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              maxWidth: '200px'
                            }}>{caseItem.contractor}</td>
                            <td style={{ 
                              padding: '12px', 
                              textAlign: 'right', 
                              fontWeight: 200,
                              whiteSpace: 'nowrap'
                            }}>{caseItem.contract_amount_display}</td>
                            <td style={{ 
                              padding: '12px', 
                              fontWeight: 200,
                              whiteSpace: 'nowrap'
                            }}>{caseItem.prefecture}</td>
                            <td style={{ 
                              padding: '12px', 
                              fontWeight: 200,
                              whiteSpace: 'nowrap'
                            }}>{caseItem.use_type}</td>
                            <td style={{ 
                              padding: '12px', 
                              fontWeight: 200,
                              whiteSpace: 'nowrap'
                            }}>{caseItem.bid_method}</td>
                            <td style={{ 
                              padding: '12px', 
                              fontWeight: 200,
                              whiteSpace: 'nowrap'
                            }}>{caseItem.award_date}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Box>
                </Paper>
              </Grid>
            )}
          </Grid>
        </Box>
      )}
    </Box>
  );
}

export default PredictionDashboard;