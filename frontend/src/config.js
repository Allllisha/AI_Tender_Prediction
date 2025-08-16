// API URL configuration
const getApiUrl = () => {
  // 環境変数から取得（Vite用）
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // 本番環境の場合はAzureのURLを使用
  if (window.location.hostname.includes('azurewebsites.net')) {
    return 'https://app-bid-kacho-backend.azurewebsites.net';
  }
  
  // ローカル開発環境
  return 'http://localhost:8000';
};

export const API_BASE_URL = getApiUrl();

export default {
  API_BASE_URL
};