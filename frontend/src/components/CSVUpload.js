import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DownloadIcon from '@mui/icons-material/Download';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import RefreshIcon from '@mui/icons-material/Refresh';
import DescriptionIcon from '@mui/icons-material/Description';
import InfoIcon from '@mui/icons-material/Info';

function CSVUpload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadHistory, setUploadHistory] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showHelp, setShowHelp] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchUploadHistory();
  }, []);

  const fetchUploadHistory = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/csv/upload-history', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUploadHistory(data);
      }
    } catch (err) {
      console.error('Failed to fetch upload history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'text/csv') {
      setSelectedFile(file);
      setError('');
    } else {
      setError('CSVファイルを選択してください');
      setSelectedFile(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('ファイルを選択してください');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/csv/upload-awards', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess(`${data.record_count}件のデータを正常にアップロードしました`);
        setSelectedFile(null);
        // ファイル入力をリセット
        document.getElementById('file-input').value = '';
        // 履歴を更新
        fetchUploadHistory();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'アップロードに失敗しました');
      }
    } catch (err) {
      setError('アップロード中にエラーが発生しました');
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const token = localStorage.getItem('token');
      console.log('Downloading template with token:', token ? 'exists' : 'missing');
      
      const response = await fetch('http://localhost:8000/csv/download-template', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      console.log('Template download response:', response.status);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'company_awards_template.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        console.log('Template downloaded successfully');
      } else {
        console.error('Template download failed:', response.status, response.statusText);
        setError(`テンプレートのダウンロードに失敗しました (${response.status})`);
      }
    } catch (err) {
      console.error('Template download error:', err);
      setError('テンプレートのダウンロードに失敗しました');
    }
  };

  const getStatusChip = (status) => {
    switch (status) {
      case 'completed':
        return <Chip label="完了" color="success" size="small" icon={<CheckCircleIcon />} />;
      case 'processing':
        return <Chip label="処理中" color="warning" size="small" icon={<HourglassEmptyIcon />} />;
      case 'failed':
        return <Chip label="失敗" color="error" size="small" icon={<ErrorIcon />} />;
      default:
        return <Chip label={status} size="small" />;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

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
          落札実績データ管理
        </Typography>
        <Typography variant="h6" sx={{ fontWeight: 200, color: '#757575' }}>
          過去の落札実績をCSVファイルでアップロード
        </Typography>
      </Box>

      {/* アップロードエリア */}
      <Paper 
        elevation={0}
        sx={{
          p: { xs: 3, md: 6 },
          mb: { xs: 3, md: 6 },
          backgroundColor: '#ffffff',
          border: '1px solid #e0e0e0',
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          flexDirection: { xs: 'column', sm: 'row' },
          justifyContent: 'space-between', 
          alignItems: { xs: 'stretch', sm: 'center' }, 
          mb: { xs: 3, md: 4 },
          gap: { xs: 2, sm: 0 }
        }}>
          <Typography 
            variant="h5"
            sx={{
              fontWeight: 200,
              letterSpacing: '0.005em',
              color: '#212121',
              mb: { xs: 2, sm: 0 }
            }}
          >
            CSVファイルアップロード
          </Typography>
          <Box sx={{ 
            display: 'flex', 
            flexDirection: { xs: 'column', sm: 'row' },
            gap: { xs: 1, sm: 0 },
            width: { xs: '100%', sm: 'auto' }
          }}>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={handleDownloadTemplate}
              sx={{ 
                mr: { xs: 0, sm: 2 }, 
                fontWeight: 200,
                width: { xs: '100%', sm: 'auto' },
                justifyContent: { xs: 'center', sm: 'flex-start' }
              }}
            >
              テンプレート
            </Button>
            <Button
              variant="outlined"
              startIcon={<InfoIcon />}
              onClick={() => setShowHelp(true)}
              sx={{ 
                fontWeight: 200,
                width: { xs: '100%', sm: 'auto' },
                justifyContent: { xs: 'center', sm: 'flex-start' }
              }}
            >
              ヘルプ
            </Button>
          </Box>
        </Box>

        <Box
          sx={{
            border: '2px dashed #e0e0e0',
            borderRadius: 2,
            p: { xs: 4, md: 6 },
            textAlign: 'center',
            backgroundColor: selectedFile ? '#f5f5f5' : '#fafafa',
            transition: 'all 0.3s ease',
          }}
        >
          <input
            id="file-input"
            type="file"
            accept=".csv"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <label htmlFor="file-input">
            <IconButton
              component="span"
              sx={{
                mb: 2,
                backgroundColor: '#1b5e20',
                color: '#ffffff',
                '&:hover': {
                  backgroundColor: '#2e7d32',
                },
                width: 80,
                height: 80,
              }}
            >
              <CloudUploadIcon sx={{ fontSize: 40 }} />
            </IconButton>
          </label>
          
          {selectedFile ? (
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 300, mb: 1 }}>
                選択されたファイル
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 200, color: '#757575', mb: 3 }}>
                {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
              </Typography>
              <Button
                variant="contained"
                size="large"
                onClick={handleUpload}
                disabled={uploading}
                sx={{
                  px: 6,
                  py: 2,
                  fontWeight: 200,
                  letterSpacing: '0.02em',
                }}
              >
                {uploading ? 'アップロード中...' : 'アップロード開始'}
              </Button>
            </Box>
          ) : (
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 300, mb: 1 }}>
                ファイルを選択
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 200, color: '#757575' }}>
                クリックしてCSVファイルを選択してください
              </Typography>
            </Box>
          )}
        </Box>

        {uploading && <LinearProgress sx={{ mt: 2 }} />}
        
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mt: 2 }}>
            {success}
          </Alert>
        )}
      </Paper>

      {/* アップロード履歴 */}
      <Paper 
        elevation={0}
        sx={{
          backgroundColor: '#ffffff',
          border: '1px solid #e0e0e0',
        }}
      >
        <Box sx={{ p: 4, borderBottom: '1px solid #e0e0e0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography 
            variant="h5"
            sx={{
              fontWeight: 200,
              letterSpacing: '0.005em',
              color: '#212121'
            }}
          >
            アップロード履歴
          </Typography>
          <IconButton onClick={fetchUploadHistory} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Box>
        
        {loading ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <LinearProgress />
          </Box>
        ) : uploadHistory.length > 0 ? (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ファイル名</TableCell>
                  <TableCell align="center">件数</TableCell>
                  <TableCell align="center">ステータス</TableCell>
                  <TableCell>アップロード日時</TableCell>
                  <TableCell>完了日時</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {uploadHistory.map((history) => (
                  <TableRow key={history.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <DescriptionIcon sx={{ mr: 1, fontSize: 20, color: '#757575' }} />
                        {history.file_name}
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      {history.record_count || '-'}
                    </TableCell>
                    <TableCell align="center">
                      {getStatusChip(history.upload_status)}
                    </TableCell>
                    <TableCell>
                      {formatDate(history.uploaded_at)}
                    </TableCell>
                    <TableCell>
                      {history.completed_at ? formatDate(history.completed_at) : '-'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Box sx={{ p: 8, textAlign: 'center' }}>
            <Typography variant="h6" sx={{ fontWeight: 200, color: '#757575', mb: 2 }}>
              アップロード履歴がありません
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 200, color: '#757575' }}>
              CSVファイルをアップロードすると、ここに履歴が表示されます
            </Typography>
          </Box>
        )}
      </Paper>

      {/* ヘルプダイアログ */}
      <Dialog open={showHelp} onClose={() => setShowHelp(false)} maxWidth="md" fullWidth>
        <DialogTitle>CSVファイルフォーマット</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 3 }}>
            以下のカラムを含むCSVファイルをアップロードしてください：
          </Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText 
                primary="tender_id" 
                secondary="案件ID（必須）" 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText 
                primary="project_name" 
                secondary="工事名（必須）" 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText 
                primary="publisher" 
                secondary="発注者（必須）" 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText 
                primary="prefecture" 
                secondary="都道府県（必須）" 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText 
                primary="municipality" 
                secondary="市区町村（必須）" 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText 
                primary="use_type" 
                secondary="用途種別（必須）例：学校、庁舎、文化施設" 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText 
                primary="method" 
                secondary="入札方式（必須）例：一般競争入札、総合評価方式" 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText 
                primary="floor_area_m2" 
                secondary="延床面積（㎡）（必須）" 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText 
                primary="award_date" 
                secondary="落札日（必須）形式：YYYY-MM-DD" 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText 
                primary="award_amount_jpy" 
                secondary="落札額（円）（必須）" 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText 
                primary="estimated_price_jpy" 
                secondary="予定価格（円）（必須）" 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText 
                primary="win_rate" 
                secondary="落札率（%）（必須）" 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText 
                primary="participants_count" 
                secondary="参加社数（必須）" 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><InfoIcon color="info" /></ListItemIcon>
              <ListItemText 
                primary="technical_score" 
                secondary="技術点（オプション）総合評価方式の場合" 
              />
            </ListItem>
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHelp(false)}>閉じる</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default CSVUpload;