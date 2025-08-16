import React, { useState, useEffect } from 'react';
import {
  TextField,
  InputAdornment,
  IconButton,
  Box,
  Typography,
  Tooltip,
  Alert,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

function PriceInput({ 
  label, 
  value, 
  onChange, 
  placeholder,
  helperText,
  step = 1000000, // デフォルト100万円単位
  min = 0,
  max,
  required = false,
  error = false,
  fullWidth = true,
  size = 'medium',
}) {
  const [displayValue, setDisplayValue] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  // 数値をカンマ区切りの文字列に変換
  const formatNumber = (num) => {
    if (!num && num !== 0) return '';
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  };

  // カンマ区切りの文字列を数値に変換
  const parseNumber = (str) => {
    if (!str) return '';
    const cleaned = str.replace(/,/g, '').replace(/[^\d]/g, '');
    return cleaned ? parseInt(cleaned, 10) : '';
  };

  // 億円表示用のフォーマット
  const formatInOku = (num) => {
    if (!num) return '';
    const oku = Math.floor(num / 100000000);
    const man = Math.floor((num % 100000000) / 10000);
    
    if (oku > 0) {
      if (man > 0) {
        return `${oku}億${man}万円`;
      }
      return `${oku}億円`;
    } else if (man > 0) {
      return `${man}万円`;
    }
    return `${formatNumber(num)}円`;
  };

  useEffect(() => {
    if (!isFocused) {
      setDisplayValue(formatNumber(value));
    }
  }, [value, isFocused]);

  const handleChange = (e) => {
    const input = e.target.value;
    setDisplayValue(input);
    
    const numValue = parseNumber(input);
    if (numValue !== '' && !isNaN(numValue)) {
      // 入力中は範囲チェックせずに値をそのまま反映
      // 範囲チェックはhandleBlur（フォーカスが外れた時）で行う
      onChange({ target: { value: numValue } });
    } else if (input === '') {
      onChange({ target: { value: '' } });
    }
  };

  const handleIncrement = () => {
    const currentValue = value || 0;
    const newValue = currentValue + step;
    if (!max || newValue <= max) {
      onChange({ target: { value: newValue } });
    }
  };

  const handleDecrement = () => {
    const currentValue = value || 0;
    const newValue = Math.max(min, currentValue - step);
    onChange({ target: { value: newValue } });
  };

  const handleFocus = () => {
    setIsFocused(true);
    setDisplayValue(value ? value.toString() : '');
  };

  const handleBlur = () => {
    setIsFocused(false);
    // フォーカスが外れた時は値をフォーマットして表示するだけ
    // 範囲チェックは行わない（警告表示は別途行う）
    setDisplayValue(formatNumber(value));
  };

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      handleIncrement();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      handleDecrement();
    }
  };

  // 価格の状態を判定
  const getPriceStatus = () => {
    if (!value || value === '') return null;
    
    if (min !== undefined && value < min) {
      return {
        severity: 'error',
        icon: <ErrorIcon />,
        message: '失格リスク：最低制限価格を下回っています',
      };
    } else if (min !== undefined && value < min * 1.02) {
      return {
        severity: 'warning',
        icon: <WarningIcon />,
        message: '要注意：低入札価格調査の対象となる可能性があります',
      };
    } else if (max !== undefined && value > max) {
      return {
        severity: 'error',
        icon: <ErrorIcon />,
        message: '予定価格を超過しています',
      };
    } else if (max !== undefined && value > max * 0.95) {
      return {
        severity: 'warning',
        icon: <WarningIcon />,
        message: '価格競争力が低い可能性があります',
      };
    } else {
      return {
        severity: 'success',
        icon: <CheckCircleIcon />,
        message: '適正範囲内です',
      };
    }
  };

  const priceStatus = getPriceStatus();

  return (
    <Box>
      <TextField
        fullWidth={fullWidth}
        size={size}
        label={label}
        value={displayValue}
        onChange={handleChange}
        onFocus={handleFocus}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        placeholder={placeholder || '例: 100,000,000'}
        required={required}
        error={error}
        helperText={helperText}
        InputProps={{
          startAdornment: <InputAdornment position="start">¥</InputAdornment>,
          endAdornment: (
            <InputAdornment position="end">
              <Box sx={{ display: 'flex', flexDirection: 'column', mr: -1 }}>
                <Tooltip title={`+${formatNumber(step)}円`}>
                  <span>
                    <IconButton
                      size="small"
                      onClick={handleIncrement}
                      disabled={max && value >= max}
                      sx={{ p: 0.5 }}
                    >
                      <AddIcon fontSize="small" />
                    </IconButton>
                  </span>
                </Tooltip>
                <Tooltip title={`-${formatNumber(step)}円`}>
                  <span>
                    <IconButton
                      size="small"
                      onClick={handleDecrement}
                      disabled={value <= min}
                      sx={{ p: 0.5 }}
                    >
                      <RemoveIcon fontSize="small" />
                    </IconButton>
                  </span>
                </Tooltip>
              </Box>
            </InputAdornment>
          ),
        }}
      />
      {value && (
        <>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
            {formatInOku(value)}
          </Typography>
          {priceStatus && (
            <Alert 
              severity={priceStatus.severity} 
              icon={priceStatus.icon}
              sx={{ 
                mt: 1, 
                py: 0.5,
                '& .MuiAlert-message': {
                  fontSize: '0.875rem'
                }
              }}
            >
              {priceStatus.message}
            </Alert>
          )}
        </>
      )}
    </Box>
  );
}

export default PriceInput;