import axios from 'axios';
import { API_BASE_URL } from '../config';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター（認証トークンを自動添付）
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const tenderAPI = {
  // 入札案件を検索
  searchTenders: async (filters) => {
    const response = await api.get('/tenders/search', { params: filters });
    return response.data;
  },

  // 特定の入札案件を取得
  getTender: async (tenderId) => {
    const response = await api.get(`/tenders/${tenderId}`);
    return response.data;
  },

  // フィルターオプションを取得
  getFilterOptions: async () => {
    const response = await api.get('/filters/options');
    return response.data;
  },
};

export const predictionAPI = {
  // 単一案件の予測
  predictSingle: async (tenderId, bidAmount, companyName = 'いであ株式会社') => {
    const response = await api.post('/predict', {
      tender_id: tenderId,
      bid_amount: bidAmount,
      company_name: companyName,
    });
    return response.data;
  },

  // 複数案件の一括予測
  predictBulk: async (filters, bidAmount, companyName = 'いであ株式会社', useRatio = true, priceRange = null) => {
    const requestData = {
      ...filters,
      bid_amount: bidAmount,
      company_name: companyName,
      use_ratio: useRatio,
    };
    
    if (priceRange) {
      requestData.min_price = priceRange[0];
      requestData.max_price = priceRange[1];
    }
    
    const response = await api.post('/predict-bulk', requestData);
    return response.data;
  },
};

export const companyAPI = {
  // 自社の強みを取得
  getCompanyStrengths: async (companyName = '星田建設株式会社') => {
    try {
      const response = await api.get('/company/strengths');
      return response.data;
    } catch (error) {
      // エラー時はモックデータを返す
      console.error('Failed to fetch company strengths:', error);
      
      // 401エラーの場合は認証をリセット
      if (error.response && error.response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('company_name');
        localStorage.removeItem('company_id');
        // ページをリロードしてログイン画面に戻す
        window.location.reload();
        return null;
      }
      const currentCompanyName = localStorage.getItem('company_name') || '星田建設株式会社';
      return {
        company_name: currentCompanyName,
        total_awards: currentCompanyName === 'デモ建設株式会社' ? 150 : 200,
        total_amount: currentCompanyName === 'デモ建設株式会社' ? 45250000000 : 137450000000,
        avg_amount: currentCompanyName === 'デモ建設株式会社' ? 301666667 : 687250000,
        avg_win_rate: currentCompanyName === 'デモ建設株式会社' ? 88.0 : 90.0,
        strongest_prefecture: currentCompanyName === 'デモ建設株式会社' ? '神奈川県' : '東京都',
        prefectures: currentCompanyName === 'デモ建設株式会社' ? 
          {'神奈川県': 45, '千葉県': 38, '埼玉県': 32, '東京都': 25, '茨城県': 10} :
          {'東京都': 80, '神奈川県': 45, '千葉県': 35, '埼玉県': 30, '茨城県': 10},
        strongest_use_type: currentCompanyName === 'デモ建設株式会社' ? '庁舎' : '学校',
        use_types: currentCompanyName === 'デモ建設株式会社' ?
          {'庁舎': 60, '文化施設': 40, '学校': 30, '体育施設': 20} :
          {'学校': 85, '庁舎': 60, '文化施設': 35, '体育施設': 20},
        bid_methods: currentCompanyName === 'デモ建設株式会社' ?
          {'一般競争入札': 90, '総合評価方式': 60} :
          {'一般競争入札': 120, '総合評価方式': 80},
        avg_tech_score: currentCompanyName === 'デモ建設株式会社' ? 75.5 : 85.5
      };
    }
  },
};

export default api;