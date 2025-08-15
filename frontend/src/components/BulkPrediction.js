import React, { useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TablePagination,
  IconButton,
  Tooltip,
  Collapse,
  TextField,
  Rating,
  Slider,
} from '@mui/material';
import ReactMarkdown from 'react-markdown';
import BatchPredictionIcon from '@mui/icons-material/BatchPrediction';
import DownloadIcon from '@mui/icons-material/Download';
import FilterListIcon from '@mui/icons-material/FilterList';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import AssessmentIcon from '@mui/icons-material/Assessment';
import PriceInput from './common/PriceInput';
import { predictionAPI, tenderAPI } from '../services/api';

function BulkPrediction() {
  const [filters, setFilters] = useState({
    prefecture: 'すべて',
    municipality: 'すべて',
    use_type: 'すべて',
    bid_amount: '90',  // デフォルト90%
    use_ratio: true,    // 予定価格比率モード
    price_range: [100000000, 2000000000], // 1億円～20億円
  });
  const [predictions, setPredictions] = useState([]);
  const [filterOptions, setFilterOptions] = useState({
    prefectures: [],
    municipalities: [],
    use_types: [],
    prefecture_municipalities: {},
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [showFilters, setShowFilters] = useState(true);
  const [expandedRow, setExpandedRow] = useState(null);

  React.useEffect(() => {
    fetchFilterOptions();
  }, []);

  const fetchFilterOptions = async () => {
    try {
      const options = await tenderAPI.getFilterOptions();
      setFilterOptions(options);
    } catch (error) {
      console.error('Failed to fetch filter options:', error);
    }
  };

  const handleFilterChange = (field) => (event) => {
    const newFilters = {
      ...filters,
      [field]: event.target.value,
    };
    
    // 都道府県が変更されたら市区町村をリセット
    // ただし、選択した市区町村が新しい都道府県に存在しない場合のみ
    if (field === 'prefecture' && event.target.value !== 'すべて') {
      const newPrefecture = event.target.value;
      if (filterOptions.prefecture_municipalities && 
          filterOptions.prefecture_municipalities[newPrefecture] &&
          filters.municipality !== 'すべて' &&
          !filterOptions.prefecture_municipalities[newPrefecture].includes(filters.municipality)) {
        newFilters.municipality = 'すべて';
      }
    } else if (field === 'prefecture' && event.target.value === 'すべて') {
      // 都道府県が「すべて」になったら市区町村も「すべて」に
      newFilters.municipality = 'すべて';
    }
    
    setFilters(newFilters);
  };

  const handleBulkPredict = async () => {
    if (!filters.bid_amount) {
      setError('入札額を入力してください');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const searchParams = {};
      if (filters.prefecture && filters.prefecture !== 'すべて') searchParams.prefecture = filters.prefecture;
      if (filters.municipality && filters.municipality !== 'すべて') searchParams.municipality = filters.municipality;
      if (filters.use_type && filters.use_type !== 'すべて') searchParams.use_type = filters.use_type;

      const result = await predictionAPI.predictBulk(
        searchParams,
        parseInt(filters.bid_amount),
        '星田建設株式会社',
        true,  // use_ratio = true
        filters.price_range  // 価格レンジを渡す
      );
      setPredictions(result.predictions || result || []);
    } catch (err) {
      setError('一括予測に失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    const csvContent = [
      ['案件ID', '案件名', 'ランク', '勝率', '推奨度'],
      ...predictions.map(p => [
        p.tender_id,
        p.project_name || p.title || '',
        p.rank,
        `${Math.round(p.win_probability * 100)}%`,
        getRankScore(p.rank),
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `bulk_prediction_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  const formatPrice = (price) => {
    if (!price && price !== 0) return '―';
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const getRankColor = (rank) => {
    const colors = {
      A: 'success',
      B: 'success',
      C: 'warning',
      D: 'warning',
      E: 'error',
    };
    return colors[rank] || 'default';
  };

  const getRankScore = (rank) => {
    const scores = {
      A: 5,
      B: 4,
      C: 3,
      D: 2,
      E: 1,
    };
    return scores[rank] || 0;
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleRowClick = (tenderId) => {
    setExpandedRow(expandedRow === tenderId ? null : tenderId);
  };

  // 統計情報の計算
  const getStatistics = () => {
    if (predictions.length === 0) return null;
    
    const rankCounts = predictions.reduce((acc, p) => {
      acc[p.rank] = (acc[p.rank] || 0) + 1;
      return acc;
    }, {});

    const avgWinProb = predictions.reduce((sum, p) => sum + p.win_probability, 0) / predictions.length;
    const recommendedCount = predictions.filter(p => p.rank === 'A' || p.rank === 'B').length;

    return {
      total: predictions.length,
      rankCounts,
      avgWinProb,
      recommendedCount,
    };
  };

  const stats = getStatistics();

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
          一括予測
        </Typography>
        <Typography variant="h6" sx={{ fontWeight: 200, color: '#757575' }}>
          複数案件の勝率を同時分析
        </Typography>
      </Box>

      {/* フィルター */}
      <Paper 
        sx={{ 
          p: { xs: 3, md: 6 }, 
          mb: { xs: 3, md: 6 },
          backgroundColor: '#ffffff',
          border: '1px solid #e0e0e0',
        }} 
        elevation={0}
      >
        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, alignItems: { xs: 'stretch', sm: 'center' }, justifyContent: 'space-between', mb: { xs: 3, md: 4 }, gap: { xs: 2, sm: 0 } }}>
          <Typography 
            variant="h5"
            sx={{
              fontWeight: 200,
              letterSpacing: '0.005em',
              color: '#212121'
            }}
          >
            検索条件
          </Typography>
          <Button
            variant="outlined"
            onClick={() => setShowFilters(!showFilters)}
            sx={{ fontWeight: 200 }}
          >
            {showFilters ? '条件を閉じる' : '条件を開く'}
          </Button>
        </Box>
        
        <Collapse in={showFilters}>
          <Grid container spacing={{ xs: 2, md: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                select
                fullWidth
                label="都道府県"
                value={filters.prefecture}
                onChange={handleFilterChange('prefecture')}
                size="medium"
              >
                <MenuItem value="すべて">すべて</MenuItem>
                {filterOptions.prefectures.map((pref) => (
                  <MenuItem key={pref} value={pref}>
                    {pref}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                select
                fullWidth
                label="市区町村"
                value={filters.municipality}
                onChange={handleFilterChange('municipality')}
                size="medium"
              >
                <MenuItem value="すべて">すべて</MenuItem>
                {filters.prefecture !== 'すべて' && filterOptions.prefecture_municipalities && 
                 filterOptions.prefecture_municipalities[filters.prefecture] ? (
                  // 特定の都道府県が選択されている場合、その都道府県の市区町村のみ表示
                  filterOptions.prefecture_municipalities[filters.prefecture].map((municipality) => (
                    <MenuItem key={municipality} value={municipality}>
                      {municipality}
                    </MenuItem>
                  ))
                ) : (
                  // 都道府県が「すべて」の場合、全市区町村を表示
                  filterOptions.municipalities && filterOptions.municipalities.map((municipality) => (
                    <MenuItem key={municipality} value={municipality}>
                      {municipality}
                    </MenuItem>
                  ))
                )}
              </TextField>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                select
                fullWidth
                label="用途種別"
                value={filters.use_type}
                onChange={handleFilterChange('use_type')}
                size="medium"
              >
                <MenuItem value="すべて">すべて</MenuItem>
                {filterOptions.use_types.map((type) => (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                label="予定価格比率"
                type="number"
                value={filters.bid_amount}
                onChange={handleFilterChange('bid_amount')}
                InputProps={{
                  endAdornment: '%',
                  inputProps: { min: 70, max: 100, step: 1 }
                }}
                helperText="予定価格に対する入札比率（70-100%）"
                required
                fullWidth
                size="medium"
                sx={{
                  '& .MuiInputBase-root': {
                    fontWeight: 200,
                    fontSize: { xs: '1rem', md: '1.1rem' },
                  },
                  '& .MuiInputLabel-root': {
                    fontWeight: 200,
                  },
                  '& .MuiFormHelperText-root': {
                    fontSize: { xs: '0.75rem', md: '0.8rem' },
                  },
                }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Box sx={{ px: { xs: 1, md: 2 } }}>
                <Typography variant="caption" sx={{ color: '#757575', fontWeight: 200, mb: 1, display: 'block' }}>
                  入札額レンジ（予定価格×比率の結果をこの範囲でフィルター）
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 1, md: 2 }, flexDirection: { xs: 'column', sm: 'row' } }}>
                  <Typography variant="body2" sx={{ minWidth: { xs: 80, md: 100 }, fontWeight: 200, fontSize: { xs: '0.8rem', md: '0.875rem' } }}>
                    ¥{(filters.price_range[0] / 100000000).toFixed(1)}億
                  </Typography>
                  <Slider
                    value={filters.price_range}
                    onChange={(e, newValue) => setFilters({...filters, price_range: newValue})}
                    valueLabelDisplay="auto"
                    valueLabelFormat={(value) => `¥${(value / 100000000).toFixed(1)}億`}
                    min={10000000}  // 1千万円
                    max={5000000000} // 50億円
                    step={10000000}  // 1千万円刻み
                    sx={{
                      '& .MuiSlider-thumb': {
                        backgroundColor: '#1b5e20',
                      },
                      '& .MuiSlider-track': {
                        backgroundColor: '#1b5e20',
                      },
                      '& .MuiSlider-rail': {
                        backgroundColor: '#e0e0e0',
                      },
                    }}
                  />
                  <Typography variant="body2" sx={{ minWidth: { xs: 80, md: 100 }, textAlign: { xs: 'center', sm: 'right' }, fontWeight: 200, fontSize: { xs: '0.8rem', md: '0.875rem' } }}>
                    ¥{(filters.price_range[1] / 100000000).toFixed(1)}億
                  </Typography>
                </Box>
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-start', mt: { xs: 3, md: 4 } }}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleBulkPredict}
                  disabled={loading || !filters.bid_amount}
                  fullWidth
                  sx={{
                    px: { xs: 4, md: 6 },
                    py: { xs: 2, md: 3 },
                    fontSize: { xs: '0.9rem', md: '1rem' },
                    fontWeight: 200,
                    letterSpacing: '0.02em',
                    maxWidth: { xs: 'none', sm: 'auto' },
                  }}
                >
                  一括予測実行
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Collapse>
      </Paper>

      {loading && <LinearProgress sx={{ mb: 2 }} />}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* 統計情報 */}
      {stats && (
        <Box sx={{ mb: { xs: 4, md: 6 } }}>
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
            予測統計
          </Typography>
          <Grid container spacing={{ xs: 3, md: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper 
                sx={{ 
                  p: { xs: 3, md: 4 }, 
                  textAlign: 'center', 
                  backgroundColor: '#ffffff',
                  border: '1px solid #e0e0e0',
                }}
                elevation={0}
              >
                <Typography variant="h2" sx={{ fontWeight: 100, color: '#212121', mb: 2, fontSize: { xs: '2rem', md: '3rem' } }}>
                  {stats.total}
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 200, color: '#757575', fontSize: { xs: '0.9rem', md: '1rem' } }}>
                  対象案件数
                </Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Paper 
                sx={{ 
                  p: { xs: 3, md: 4 }, 
                  textAlign: 'center', 
                  backgroundColor: '#ffffff',
                  border: '1px solid #0a6e4a',
                }}
                elevation={0}
              >
                <Typography variant="h2" sx={{ fontWeight: 100, color: '#0a6e4a', mb: 2, fontSize: { xs: '2rem', md: '3rem' } }}>
                  {stats.recommendedCount}
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 200, color: '#757575', fontSize: { xs: '0.8rem', md: '1rem' } }}>
                  推奨案件数（A/Bランク）
                </Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Paper 
                sx={{ 
                  p: { xs: 3, md: 4 }, 
                  textAlign: 'center', 
                  backgroundColor: '#ffffff',
                  border: '1px solid #e0e0e0',
                }}
                elevation={0}
              >
                <Typography variant="h2" sx={{ fontWeight: 100, color: '#212121', mb: 2, fontSize: { xs: '2rem', md: '3rem' } }}>
                  {Math.round(stats.avgWinProb * 100)}%
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 200, color: '#757575', fontSize: { xs: '0.9rem', md: '1rem' } }}>
                  平均勝率
                </Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Paper 
                sx={{ 
                  p: { xs: 3, md: 4 },
                  backgroundColor: '#ffffff',
                  border: '1px solid #e0e0e0',
                }}
                elevation={0}
              >
                <Typography variant="body1" sx={{ fontWeight: 200, color: '#757575', mb: 3, textAlign: 'center', fontSize: { xs: '0.9rem', md: '1rem' } }}>
                  ランク分布
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap', gap: { xs: 1, md: 0 } }}>
                  {Object.entries(stats.rankCounts).map(([rank, count]) => (
                    <Box key={rank} sx={{ textAlign: 'center' }}>
                      <Typography variant="h6" sx={{ fontWeight: 200, color: rank === 'A' || rank === 'B' ? '#0a6e4a' : '#757575' }}>
                        {rank}
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 200, color: '#757575' }}>
                        {count}件
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </Box>
      )}

      {/* 結果テーブル */}
      {predictions.length > 0 && (
        <Paper 
          elevation={0}
          sx={{
            backgroundColor: '#ffffff',
            border: '1px solid #e0e0e0',
          }}
        >
          <Box sx={{ p: { xs: 3, md: 4 }, borderBottom: '1px solid #e0e0e0', display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, justifyContent: 'space-between', alignItems: { xs: 'stretch', sm: 'center' }, gap: { xs: 2, sm: 0 } }}>
            <Typography 
              variant="h5"
              sx={{
                fontWeight: 200,
                letterSpacing: '0.005em',
                color: '#212121',
                fontSize: { xs: '1.25rem', md: '1.5rem' }
              }}
            >
              予測結果一覧
            </Typography>
            <Button
              variant="outlined"
              onClick={handleExport}
              sx={{ fontWeight: 200 }}
            >
              CSVエクスポート
            </Button>
          </Box>
          
          <TableContainer>
            <Box sx={{ overflowX: 'auto' }}>
              <Table sx={{ minWidth: { xs: 650, md: 'auto' } }}>
              <TableHead>
                <TableRow>
                  <TableCell width="40"></TableCell>
                  <TableCell>案件名</TableCell>
                  <TableCell align="center">ランク</TableCell>
                  <TableCell align="center">勝率</TableCell>
                  <TableCell align="center">推奨度</TableCell>
                  <TableCell align="center">信頼度</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {predictions
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((prediction) => (
                    <React.Fragment key={prediction.tender_id}>
                      <TableRow
                        hover
                        sx={{ 
                          cursor: 'pointer',
                          '&:hover': { bgcolor: 'action.hover' }
                        }}
                        onClick={() => handleRowClick(prediction.tender_id)}
                      >
                        <TableCell>
                          <IconButton size="small">
                            {expandedRow === prediction.tender_id ? 
                              <ExpandLessIcon /> : <ExpandMoreIcon />}
                          </IconButton>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {prediction.project_name || prediction.title || '―'}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {prediction.tender_id}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Typography 
                            variant="h6" 
                            sx={{ 
                              fontWeight: 200, 
                              color: prediction.rank === 'A' || prediction.rank === 'B' ? '#0a6e4a' : '#757575' 
                            }}
                          >
                            {prediction.rank}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Typography 
                            variant="body1" 
                            sx={{ 
                              fontWeight: 200,
                              color: prediction.win_probability >= 0.5 ? '#0a6e4a' : '#757575'
                            }}
                          >
                            {Math.round(prediction.win_probability * 100)}%
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Typography 
                            variant="body1" 
                            sx={{ 
                              fontWeight: 200,
                              color: prediction.rank === 'A' || prediction.rank === 'B' ? '#0a6e4a' : '#757575'
                            }}
                          >
                            {getRankScore(prediction.rank)}/5
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Typography variant="body1" sx={{ fontWeight: 200, color: '#757575' }}>
                            {prediction.confidence === 'high' ? '高' :
                             prediction.confidence === 'medium' ? '中' : '低'}
                          </Typography>
                        </TableCell>
                      </TableRow>
                      
                      <TableRow>
                        <TableCell colSpan={6} sx={{ py: 0, px: 0 }}>
                          <Collapse in={expandedRow === prediction.tender_id}>
                            <Box 
                              sx={{ 
                                p: 2, 
                                bgcolor: 'grey.50',
                                maxHeight: '400px',
                                overflowY: 'auto',
                                '& h3': { fontSize: '1rem', fontWeight: 500, mt: 1, mb: 0.5 },
                                '& h4': { fontSize: '0.95rem', fontWeight: 500, mt: 1, mb: 0.5 },
                                '& p': { fontSize: '0.875rem', mb: 0.5 },
                                '& ul': { pl: 2, mb: 0.5 },
                                '& li': { fontSize: '0.875rem', mb: 0.25 },
                                '& strong': { fontWeight: 600 }
                              }}
                            >
                              <Typography variant="body2" component="div" gutterBottom>
                                <strong>推奨事項:</strong>
                              </Typography>
                              <ReactMarkdown>{prediction.recommendation}</ReactMarkdown>
                            </Box>
                          </Collapse>
                        </TableCell>
                      </TableRow>
                    </React.Fragment>
                  ))}
              </TableBody>
              </Table>
            </Box>
          </TableContainer>
          
          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={predictions.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            labelRowsPerPage="表示件数:"
            labelDisplayedRows={({ from, to, count }) => `${from}-${to} / ${count}件`}
          />
        </Paper>
      )}

      {!loading && predictions.length === 0 && filters.bid_amount && (
        <Paper 
          sx={{ 
            p: { xs: 4, md: 8 }, 
            textAlign: 'center', 
            mt: { xs: 4, md: 6 },
            backgroundColor: '#ffffff',
            border: '1px solid #e0e0e0',
          }}
          elevation={0}
        >
          <Typography variant="h5" sx={{ color: '#757575', mb: 2, fontWeight: 200 }}>
            予測結果がありません
          </Typography>
          <Typography variant="body1" sx={{ color: '#757575', fontWeight: 200 }}>
            検索条件を変更して再度お試しください
          </Typography>
        </Paper>
      )}
    </Box>
  );
}

export default BulkPrediction;