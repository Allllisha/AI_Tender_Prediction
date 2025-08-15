import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  TextField,
  MenuItem,
  Button,
  Paper,
  Typography,
  Chip,
  Card,
  CardContent,
  CardActions,
  Divider,
  FormControl,
  InputLabel,
  Select,
  Collapse,
  IconButton,
  Alert,
  LinearProgress,
  Fade,
  Pagination,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import BusinessIcon from '@mui/icons-material/Business';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ClearIcon from '@mui/icons-material/Clear';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import ConstructionIcon from '@mui/icons-material/Construction';
import PriceInput from './common/PriceInput';
import { tenderAPI } from '../services/api';

function TenderSearch({ onSelectTender }) {
  const [filters, setFilters] = useState({
    prefecture: 'すべて',
    municipality: 'すべて',
    use_type: 'すべて',
    min_price: '',
    max_price: '',
    bid_method: 'すべて',
  });
  const [filterOptions, setFilterOptions] = useState({
    prefectures: [],
    municipalities: [],
    use_types: [],
    bid_methods: [],
    prefecture_municipalities: {},
  });
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const itemsPerPage = 12;

  useEffect(() => {
    fetchFilterOptions();
    // 初期検索を実行
    handleSearch();
  }, []);

  const fetchFilterOptions = async () => {
    try {
      const options = await tenderAPI.getFilterOptions();
      setFilterOptions(options);
    } catch (error) {
      console.error('Failed to fetch filter options:', error);
      setError('フィルターオプションの取得に失敗しました');
    }
  };

  const handleFilterChange = (field) => (event) => {
    const newFilters = {
      ...filters,
      [field]: event.target.value,
    };
    
    // 都道府県が変更されたら市区町村をリセット
    // ただし、選択した市区町村が新しい都道府県に存在しない場合のみ
    if (field === 'prefecture' && event.target.value && event.target.value !== 'すべて') {
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

  const handleClearFilters = () => {
    setFilters({
      prefecture: 'すべて',
      municipality: 'すべて',
      use_type: 'すべて',
      min_price: '',
      max_price: '',
      bid_method: 'すべて',
    });
  };

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    setPage(1); // 検索時はページを1にリセット
    try {
      const cleanFilters = {};
      Object.keys(filters).forEach((key) => {
        if (filters[key] !== '' && filters[key] !== 'すべて') {
          if (key === 'min_price' || key === 'max_price') {
            cleanFilters[key] = parseInt(filters[key]);
          } else {
            cleanFilters[key] = filters[key];
          }
        }
      });
      const results = await tenderAPI.searchTenders(cleanFilters);
      setSearchResults(results);
    } catch (error) {
      console.error('Search failed:', error);
      setError('検索に失敗しました。しばらくしてから再度お試しください。');
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    if (!price) return '―';
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

  const getRankColor = (tender) => {
    // 予定価格に基づく簡易ランク判定
    const price = tender.estimated_price;
    if (price >= 1000000000) return 'error'; // 10億円以上
    if (price >= 500000000) return 'warning'; // 5億円以上
    if (price >= 100000000) return 'info'; // 1億円以上
    return 'success';
  };

  const handlePageChange = (event, value) => {
    setPage(value);
    // ページ変更時にスクロール
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // ページネーション用のデータ計算
  const totalPages = Math.ceil(searchResults.length / itemsPerPage);
  const startIndex = (page - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedResults = searchResults.slice(startIndex, endIndex);

  return (
    <Box>
      <Box sx={{ mb: { xs: 4, sm: 6, md: 8 } }}>
        <Typography 
          variant="h2" 
          sx={{ 
            fontWeight: 200, 
            letterSpacing: '-0.01em',
            mb: { xs: 1, md: 2 },
            color: '#212121'
          }}
        >
          案件検索
        </Typography>
        <Typography variant="h6" sx={{ fontWeight: 400, color: '#757575' }}>
          全国の公共工事入札案件を統合検索
        </Typography>
      </Box>

      <Paper 
        sx={{ 
          p: { xs: 3, md: 6 }, 
          mb: { xs: 3, md: 6 },
          backgroundColor: '#ffffff',
          border: '1px solid #bdbdbd',
        }} 
        elevation={0}
      >
        <Grid container spacing={{ xs: 2, md: 3 }}>
          {/* 基本検索条件 */}
          <Grid item xs={12} sm={6} md={4}>
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
          
          <Grid item xs={12} sm={6} md={4}>
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
          
          <Grid item xs={12} sm={6} md={4}>
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

          {/* 詳細検索条件 */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Button
                onClick={() => setShowAdvanced(!showAdvanced)}
                endIcon={showAdvanced ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                size="small"
              >
                詳細条件
              </Button>
              {showAdvanced && (
                <Button
                  onClick={handleClearFilters}
                  startIcon={<ClearIcon />}
                  size="small"
                  sx={{ ml: 2 }}
                >
                  条件をクリア
                </Button>
              )}
            </Box>
            
            <Collapse in={showAdvanced}>
              <Grid container spacing={{ xs: 2, md: 3 }}>
                <Grid item xs={12} sm={6} md={4}>
                  <TextField
                    select
                    fullWidth
                    label="入札方式"
                    value={filters.bid_method}
                    onChange={handleFilterChange('bid_method')}
                    size="medium"
                  >
                    <MenuItem value="すべて">すべて</MenuItem>
                    {filterOptions.bid_methods.map((method) => (
                      <MenuItem key={method} value={method}>
                        {method}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                
                <Grid item xs={12} sm={6} md={4}>
                  <PriceInput
                    label="予定価格（下限）"
                    value={filters.min_price}
                    onChange={handleFilterChange('min_price')}
                    step={10000000} // 1000万円単位
                    helperText="最小金額を入力"
                    size="medium"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6} md={4}>
                  <PriceInput
                    label="予定価格（上限）"
                    value={filters.max_price}
                    onChange={handleFilterChange('max_price')}
                    step={10000000} // 1000万円単位
                    helperText="最大金額を入力"
                    size="medium"
                  />
                </Grid>
              </Grid>
            </Collapse>
          </Grid>

          {/* 検索ボタン */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', mt: { xs: 3, md: 4 } }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleSearch}
                disabled={loading}
                fullWidth
                sx={{ 
                  px: { xs: 4, md: 6 },
                  py: { xs: 2, md: 3 },
                  fontSize: { xs: '1rem', md: '1.1rem' },
                  fontWeight: 500,
                  letterSpacing: '0em',
                  maxWidth: { xs: 'none', sm: 'auto' },
                }}
              >
                検索実行
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {loading && <LinearProgress sx={{ mb: 2 }} />}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ mb: 6, borderBottom: '1px solid #e0e0e0', pb: 4 }}>
        <Typography 
          variant="h3" 
          sx={{ 
            fontWeight: 300,
            color: '#212121',
            letterSpacing: '-0.005em',
            mb: 1
          }}
        >
          検索結果
        </Typography>
        <Typography variant="h6" sx={{ fontWeight: 400, color: '#757575' }}>
          {searchResults.length}件の案件が見つかりました
        </Typography>
      </Box>

      <Grid container spacing={{ xs: 3, md: 6 }}>
        {paginatedResults.map((tender, index) => (
          <Grid item xs={12} sm={6} lg={4} key={tender.tender_id}>
            <Card 
              elevation={0}
              sx={{ 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                border: '1px solid #bdbdbd',
                backgroundColor: '#ffffff',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                '&:hover': {
                  borderColor: '#212121',
                  transform: { xs: 'none', md: 'translateY(-2px)' },
                  boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                }
              }}
              onClick={() => onSelectTender(tender)}
            >
              <CardContent sx={{ flexGrow: 1, p: { xs: 3, md: 4 } }}>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    fontWeight: 400, 
                    mb: { xs: 2, md: 3 },
                    letterSpacing: '0em',
                    lineHeight: 1.5,
                    color: '#212121',
                    fontSize: { xs: '1.1rem', md: '1.25rem' }
                  }}
                >
                  {tender.title}
                </Typography>

                <Box sx={{ mb: { xs: 3, md: 4 } }}>
                  <Typography variant="body2" sx={{ color: '#757575', mb: 1, fontWeight: 400 }}>
                    {tender.prefecture} {tender.municipality}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#757575', mb: 1, fontWeight: 400 }}>
                    {tender.publisher}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#757575', fontWeight: 400 }}>
                    入札日: {tender.bid_date}
                  </Typography>
                </Box>

                <Box sx={{ borderTop: '1px solid #e0e0e0', pt: { xs: 2, md: 3 } }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body2" sx={{ color: '#757575', fontWeight: 400 }}>
                      予定価格
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 500, color: '#212121' }}>
                      {formatPrice(tender.estimated_price)}
                    </Typography>
                  </Box>
                  
                  {tender.minimum_price && (
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="body2" sx={{ color: '#757575', fontWeight: 400 }}>
                        最低制限価格
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 400, color: '#212121' }}>
                        {formatPrice(tender.minimum_price)}
                      </Typography>
                    </Box>
                  )}
                  
                  {tender.floor_area_m2 && (
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" sx={{ color: '#757575', fontWeight: 400 }}>
                        延床面積
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 400, color: '#212121' }}>
                        {formatArea(tender.floor_area_m2)}
                      </Typography>
                    </Box>
                  )}
                </Box>

                <Box sx={{ mt: { xs: 2, md: 3 }, display: 'flex', gap: { xs: 1, md: 2 }, flexWrap: 'wrap' }}>
                  <Chip
                    label={tender.use_type}
                    size="small"
                    sx={{ fontWeight: 500 }}
                  />
                  <Chip
                    label={tender.bid_method}
                    size="small"
                    sx={{ fontWeight: 500 }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* ページネーション */}
      {searchResults.length > 0 && totalPages > 1 && (
        <Box sx={{ 
          mt: { xs: 4, md: 6 }, 
          display: 'flex', 
          flexDirection: { xs: 'column', sm: 'row' },
          justifyContent: 'center',
          alignItems: 'center',
          gap: { xs: 2, md: 3 }
        }}>
          <Typography variant="body2" sx={{ color: '#757575', fontWeight: 400 }}>
            {startIndex + 1}-{Math.min(endIndex, searchResults.length)} / {searchResults.length}件
          </Typography>
          <Pagination 
            count={totalPages} 
            page={page} 
            onChange={handlePageChange}
            size="large"
            sx={{
              '& .MuiPaginationItem-root': {
                fontWeight: 400,
                fontSize: { xs: '0.875rem', md: '1rem' },
                borderRadius: 0,
                border: '1px solid #bdbdbd',
                color: '#212121',
                '&:hover': {
                  backgroundColor: '#f5f5f5',
                  borderColor: '#212121',
                },
                '&.Mui-selected': {
                  backgroundColor: '#212121',
                  color: '#ffffff',
                  borderColor: '#212121',
                  '&:hover': {
                    backgroundColor: '#424242',
                  },
                },
              },
            }}
          />
        </Box>
      )}

      {!loading && searchResults.length === 0 && (
        <Paper 
          sx={{ 
            p: { xs: 4, md: 8 }, 
            textAlign: 'center', 
            mt: { xs: 4, md: 6 },
            backgroundColor: '#ffffff',
            border: '1px solid #bdbdbd',
          }}
          elevation={0}
        >
          <Typography variant="h5" sx={{ color: '#757575', mb: 2, fontWeight: 400 }}>
            検索結果がありません
          </Typography>
          <Typography variant="body1" sx={{ color: '#757575', fontWeight: 400 }}>
            検索条件を変更して再度お試しください
          </Typography>
        </Paper>
      )}
    </Box>
  );
}

export default TenderSearch;