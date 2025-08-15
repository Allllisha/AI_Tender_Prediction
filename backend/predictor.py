import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from ai_analyzer import AIAnalyzer
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class BidPredictor:
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.ai_analyzer = None
        try:
            self.ai_analyzer = AIAnalyzer()
        except Exception as e:
            print(f"AI Analyzer initialization failed: {e}")
            self.ai_analyzer = None
        
    def predict_single(self, tender_id: str, bid_amount: int, company_name: str) -> Dict:
        """単一案件の落札確率を予測"""
        tender = self.data_loader.get_tender_by_id(tender_id)
        if not tender:
            raise ValueError(f"Tender {tender_id} not found")
            
        # 類似案件を取得（予定価格も考慮）
        similar_awards = self.data_loader.get_similar_awards(
            prefecture=tender['prefecture'],
            use_type=tender['use_type'],
            floor_area=tender.get('floor_area_m2'),
            bid_method=tender['bid_method'],
            estimated_price=tender['estimated_price']
        )
        
        # 自社の強みを取得
        company_strengths = self.data_loader.get_company_strengths(company_name)
        
        # 予測を実行
        rank, win_prob, confidence = self._calculate_prediction(
            bid_amount, tender, similar_awards, company_strengths
        )
        
        # 根拠データを生成
        basis = self._generate_basis(bid_amount, tender, similar_awards)
        
        # AI分析を実行（利用可能な場合）
        ai_analysis = {}
        if self.ai_analyzer:
            avg_participants = 0
            if 'participants_count' in similar_awards.columns and len(similar_awards) > 0:
                avg_val = similar_awards['participants_count'].mean()
                avg_participants = avg_val if not pd.isna(avg_val) else 0
            
            similar_awards_summary = {
                'count': len(similar_awards),
                'median': int(similar_awards['contract_amount'].median()) if len(similar_awards) > 0 else 0,
                'min': int(similar_awards['contract_amount'].min()) if len(similar_awards) > 0 else 0,
                'max': int(similar_awards['contract_amount'].max()) if len(similar_awards) > 0 else 0,
                'avg_participants': avg_participants
            }
            ai_analysis = self.ai_analyzer.analyze_bid_risks(tender, bid_amount, similar_awards_summary, company_strengths)
            
            # AI分析による信頼度調整
            if ai_analysis.get('confidence_adjustment'):
                win_prob = max(0.0, min(1.0, win_prob + ai_analysis['confidence_adjustment']))
        
        # AI分析が利用可能な場合はAI分析を優先、そうでない場合はフォールバック
        if ai_analysis.get('risk_factors'):
            # AI分析のリスクをメインとして使用
            risk_notes = []
            for risk in ai_analysis['risk_factors']:
                # リスクが文字列であることを確認
                if isinstance(risk, str):
                    risk_notes.append(risk)
        else:
            # AI分析が利用できない場合のみハードコードされた分析を使用
            risk_notes = self._analyze_risks(bid_amount, tender, similar_awards, company_strengths)
        
        # 判断理由を生成
        judgment_reason = self._generate_judgment_reason(rank, win_prob, bid_amount, tender, similar_awards, company_strengths)
        
        # 類似案件の詳細情報を取得
        similar_cases_details = self._get_similar_cases_details(similar_awards)
        
        # 推奨事項を生成（AIが利用可能な場合はAIを使用）
        if self.ai_analyzer and ai_analysis:
            # AIに詳細情報を渡して推奨事項を生成
            recommendation = self.ai_analyzer.generate_detailed_recommendation(
                rank, win_prob, ai_analysis, tender, basis, company_strengths
            )
        else:
            recommendation = self._generate_recommendation(rank, win_prob, risk_notes)
        
        return {
            'tender_id': tender_id,
            'title': tender['title'],  # Changed from project_name to match model
            'rank': rank,
            'win_probability': win_prob,
            'confidence': confidence,
            'basis': basis,
            'judgment_reason': judgment_reason,  # 判断理由を追加
            'risk_notes': risk_notes,
            'similar_cases': similar_cases_details,  # 類似案件の詳細を追加
            'recommendation': recommendation,
            'top_factors': [  # Added to match model requirements
                {'name': 'price_competitiveness', 'direction': '+' if rank in ['A', 'B'] else '-', 'impact': 0.3},
                {'name': 'company_strength', 'direction': '+', 'impact': 0.2},
                {'name': 'local_presence', 'direction': '-' if len(company_strengths.get('prefectures', {})) == 0 else '+', 'impact': 0.15}
            ]
        }
        
    def predict_bulk(self, search_params: Dict, bid_amount: int, company_name: str, 
                     use_ratio: bool = False, min_price: int = None, max_price: int = None) -> List[Dict]:
        """複数案件の一括予測（並行処理版）
        
        Args:
            search_params: 検索条件
            bid_amount: 入札額または予定価格比率（use_ratio=Trueの場合は%値）
            company_name: 会社名
            use_ratio: Trueの場合、bid_amountを予定価格比率(%)として扱う
            min_price: 入札額の最小値フィルター
            max_price: 入札額の最大値フィルター
        """
        start_time = time.time()
        tenders = self.data_loader.search_tenders(**search_params)
        results = []
        
        # 処理対象の案件を準備
        target_tenders = []
        for tender in tenders[:20]:  # 最大20件まで
            # 予定価格比率モードの場合、各案件の予定価格から入札額を計算
            if use_ratio:
                actual_bid_amount = int(tender['estimated_price'] * bid_amount / 100)
            else:
                actual_bid_amount = bid_amount
            
            # 価格レンジフィルターの適用
            if min_price and actual_bid_amount < min_price:
                continue
            if max_price and actual_bid_amount > max_price:
                continue
                
            target_tenders.append((tender, actual_bid_amount))
        
        # 並行処理で予測を実行
        def predict_wrapper(tender_data):
            tender, actual_bid_amount = tender_data
            try:
                return self.predict_single(tender['tender_id'], actual_bid_amount, company_name)
            except Exception as e:
                print(f"Prediction error for {tender['tender_id']}: {e}")
                return None
        
        # ThreadPoolExecutorで並行実行（最大8スレッド）
        with ThreadPoolExecutor(max_workers=min(8, len(target_tenders))) as executor:
            # 全ての予測タスクを投入
            future_to_tender = {executor.submit(predict_wrapper, tender_data): tender_data 
                              for tender_data in target_tenders}
            
            # 完了したタスクから結果を収集
            for future in as_completed(future_to_tender):
                result = future.result()
                if result:
                    results.append(result)
        
        # 勝率の高い順にソート
        results.sort(key=lambda x: x['win_probability'], reverse=True)
        
        elapsed_time = time.time() - start_time
        print(f"Bulk prediction completed: {len(results)} predictions in {elapsed_time:.2f} seconds")
        
        return results
        
    def _calculate_prediction(self, bid_amount: int, tender: Dict, 
                            similar_awards: pd.DataFrame, company_strengths: Dict) -> Tuple[str, float, str]:
        """予測計算のコアロジック"""
        
        # 基準価格の計算（類似案件の中央値）
        if len(similar_awards) > 0:
            median_price = similar_awards['contract_amount'].median()
            n_similar = len(similar_awards)
        else:
            # 類似案件がない場合は予定価格の90%を基準とする
            median_price = tender['estimated_price'] * 0.9
            n_similar = 0
            
        # 価格差の計算
        price_gap = bid_amount - median_price
        price_gap_ratio = price_gap / median_price if median_price > 0 else 0
        
        # 予定価格との比率も考慮
        estimated_ratio = bid_amount / tender['estimated_price'] if tender['estimated_price'] > 0 else 1.0
        
        # 基本勝率の計算（価格ベース）
        # より現実的な分布にするため、予定価格との比率も考慮
        if estimated_ratio < 0.75:  # 予定価格の75%未満
            base_win_prob = 0.90
            rank = 'A'
        elif estimated_ratio < 0.82:  # 予定価格の82%未満
            base_win_prob = 0.75
            rank = 'A'
        elif estimated_ratio < 0.88:  # 予定価格の88%未満
            base_win_prob = 0.65
            rank = 'B'
        elif estimated_ratio < 0.92:  # 予定価格の92%未満
            base_win_prob = 0.55
            rank = 'B'
        elif estimated_ratio < 0.96:  # 予定価格の96%未満
            base_win_prob = 0.45
            rank = 'C'
        elif estimated_ratio < 0.99:  # 予定価格の99%未満
            base_win_prob = 0.35
            rank = 'C'
        elif estimated_ratio < 1.02:  # 予定価格の102%未満
            base_win_prob = 0.25
            rank = 'D'
        elif estimated_ratio < 1.05:  # 予定価格の105%未満
            base_win_prob = 0.15
            rank = 'D'
        else:  # 予定価格の105%以上
            base_win_prob = 0.08
            rank = 'E'
            
        # 自社の強みによる補正
        win_prob = base_win_prob
        
        # 地域での実績による補正
        if company_strengths['prefectures'].get(tender['prefecture'], 0) > 10:
            win_prob += 0.10  # 該当地域で10件以上の実績があれば+10%
        elif company_strengths['prefectures'].get(tender['prefecture'], 0) > 5:
            win_prob += 0.05  # 5件以上なら+5%
            
        # 用途での実績による補正
        if company_strengths['use_types'].get(tender['use_type'], 0) > 15:
            win_prob += 0.08  # 該当用途で15件以上の実績があれば+8%
        elif company_strengths['use_types'].get(tender['use_type'], 0) > 8:
            win_prob += 0.04  # 8件以上なら+4%
            
        # 総合評価方式での技術力補正
        if tender['bid_method'] == '総合評価方式' and company_strengths.get('avg_tech_score'):
            if company_strengths['avg_tech_score'] and company_strengths['avg_tech_score'] > 80:
                win_prob += 0.12  # 技術点が高ければ+12%
                
        # 最低制限価格との関係
        if tender.get('minimum_price') and bid_amount < tender['minimum_price']:
            win_prob = 0.0  # 最低制限価格未満は失格
            rank = 'E'
        
        # ランクの最終調整（勝率に基づいて）
        if win_prob >= 0.70:
            rank = 'A'
        elif win_prob >= 0.50:
            rank = 'B'
        elif win_prob >= 0.35:
            rank = 'C'
        elif win_prob >= 0.20:
            rank = 'D'
        else:
            rank = 'E'
            
        # 勝率を0-1の範囲に制限
        win_prob = max(0.0, min(1.0, win_prob))
        
        # 信頼度の判定
        if n_similar >= 15:
            confidence = 'high'
        elif n_similar >= 5:
            confidence = 'medium'
        else:
            confidence = 'low'
            
        return rank, round(win_prob, 3), confidence
        
    def _generate_basis(self, bid_amount: int, tender: Dict, similar_awards: pd.DataFrame) -> Dict:
        """予測根拠の生成"""
        basis = {
            'n_similar': len(similar_awards),
            'similar_median': int(similar_awards['contract_amount'].median()) if len(similar_awards) > 0 else 0,
            'similar_min': int(similar_awards['contract_amount'].min()) if len(similar_awards) > 0 else 0,
            'similar_max': int(similar_awards['contract_amount'].max()) if len(similar_awards) > 0 else 0,
            'price_gap': bid_amount - int(similar_awards['contract_amount'].median()) if len(similar_awards) > 0 else 0,
            'estimated_price': tender['estimated_price'],
            'minimum_price': tender['minimum_price'],
            'bid_vs_estimated_ratio': round(bid_amount / tender['estimated_price'] * 100, 1)
        }
        return basis
        
    def _analyze_risks(self, bid_amount: int, tender: Dict, similar_awards: pd.DataFrame, 
                      company_strengths: Dict) -> List[str]:
        """リスク要因の分析（フォールバック用）"""
        # AIが利用できない場合のみの最小限のフォールバック
        risks = []
        
        # 最低制限価格チェック（失格リスクのみ）
        if tender.get('minimum_price') and bid_amount < tender['minimum_price']:
            risks.append("入札額が最低制限価格を下回っています（失格）")
            
        # 基本的なリスク判定のみ
        if len(similar_awards) > 0:
            median_price = similar_awards['contract_amount'].median()
            price_ratio = bid_amount / median_price
            
            if price_ratio > 1.2:
                risks.append("価格競争力に課題がある可能性があります")
            elif price_ratio < 0.8:
                risks.append("採算性に注意が必要です")
                
        if not risks:
            risks.append("詳細なリスク分析は利用できません")
                
        return risks
        
    def _generate_judgment_reason(self, rank: str, win_prob: float, bid_amount: int, 
                                 tender: Dict, similar_awards: pd.DataFrame, 
                                 company_strengths: Dict) -> str:
        """判断理由の生成"""
        reasons = []
        
        # 予定価格との比率を計算
        estimated_ratio = bid_amount / tender['estimated_price'] if tender['estimated_price'] > 0 else 1.0
        estimated_ratio_pct = round(estimated_ratio * 100, 1)
        
        # 類似案件の中央値との比較
        if len(similar_awards) > 0:
            median_price = similar_awards['contract_amount'].median()
            price_diff = bid_amount - median_price
            price_diff_pct = round((price_diff / median_price) * 100, 1) if median_price > 0 else 0
        else:
            median_price = tender['estimated_price'] * 0.9
            price_diff = bid_amount - median_price
            price_diff_pct = round((price_diff / median_price) * 100, 1) if median_price > 0 else 0
        
        # ランクに応じた判断理由を生成
        if rank == 'A':
            reasons.append(f"非常に有望と判断しました（勝率{int(win_prob * 100)}%）")
            reasons.append(f"入札額は予定価格の{estimated_ratio_pct}%で、価格競争力が非常に高いです")
            if len(similar_awards) > 0:
                reasons.append(f"類似{len(similar_awards)}件の落札額中央値より{abs(price_diff)/1000000:.1f}百万円低く設定されています")
            
            # 自社の強みを評価
            if tender['prefecture'] in company_strengths.get('prefectures', {}):
                count = company_strengths['prefectures'][tender['prefecture']]
                if count > 5:
                    reasons.append(f"当地域での{count}件の落札実績が信頼性を高めています")
                    
        elif rank == 'B':
            reasons.append(f"有望な案件と判断しました（勝率{int(win_prob * 100)}%）")
            reasons.append(f"入札額は予定価格の{estimated_ratio_pct}%で、適切な価格競争力があります")
            if len(similar_awards) > 0:
                if price_diff < 0:
                    reasons.append(f"類似{len(similar_awards)}件の中央値より{abs(price_diff)/1000000:.1f}百万円低く、競争優位性があります")
                else:
                    reasons.append(f"類似{len(similar_awards)}件の中央値に近い適正価格帯です")
                    
        elif rank == 'C':
            reasons.append(f"標準的な勝率の案件です（勝率{int(win_prob * 100)}%）")
            reasons.append(f"入札額は予定価格の{estimated_ratio_pct}%で、平均的な価格設定です")
            if price_diff > 0:
                reasons.append(f"類似案件より{price_diff/1000000:.1f}百万円高く、価格面での改善余地があります")
            else:
                reasons.append("価格設定は妥当ですが、技術評価等での差別化が重要です")
                
        elif rank == 'D':
            reasons.append(f"やや厳しい予測となりました（勝率{int(win_prob * 100)}%）")
            reasons.append(f"入札額が予定価格の{estimated_ratio_pct}%と高めの設定です")
            if price_diff > 0:
                reasons.append(f"類似案件より{price_diff/1000000:.1f}百万円高く、価格競争力に課題があります")
            reasons.append("価格戦略の見直しまたは技術提案での差別化が必要です")
            
        else:  # rank == 'E'
            reasons.append(f"落札可能性が低いと判断しました（勝率{int(win_prob * 100)}%）")
            if tender.get('minimum_price') and bid_amount < tender['minimum_price']:
                reasons.append("最低制限価格を下回っており、失格となる可能性があります")
            elif estimated_ratio > 1.0:
                reasons.append(f"入札額が予定価格の{estimated_ratio_pct}%と予定価格を超過しています")
            else:
                reasons.append(f"入札額が予定価格の{estimated_ratio_pct}%と高く、競争力が不足しています")
            reasons.append("大幅な価格見直しが必要です")
        
        # 総合評価方式の場合の追記
        if tender.get('bid_method') == '総合評価方式':
            if company_strengths.get('avg_tech_score') and company_strengths['avg_tech_score'] > 80:
                reasons.append("総合評価方式での高い技術評価実績が加点要因となります")
            else:
                reasons.append("総合評価方式のため、技術提案の充実が重要です")
        
        return " ".join(reasons)
    
    def _get_similar_cases_details(self, similar_awards: pd.DataFrame) -> List[Dict]:
        """類似案件の詳細情報を取得"""
        cases = []
        
        if len(similar_awards) == 0:
            return cases
        
        # 最大10件まで詳細を返す
        for idx, row in similar_awards.head(10).iterrows():
            case = {
                'contractor': row.get('contractor', '非公開'),
                'contract_amount': int(row['contract_amount']),
                'contract_amount_display': f"{int(row['contract_amount']/1000000):,}百万円",
                'prefecture': row.get('prefecture', ''),
                'use_type': row.get('use_type', ''),
                'bid_method': row.get('bid_method', ''),
                'award_date': row.get('award_date', '').strftime('%Y年%m月') if pd.notna(row.get('award_date')) else '',
                'participants_count': int(row.get('participants_count', 0)) if pd.notna(row.get('participants_count')) else None
            }
            cases.append(case)
        
        return cases
    
    def _generate_recommendation(self, rank: str, win_prob: float, risks: List[str]) -> str:
        """推奨事項の生成（フォールバック用）"""
        # AIが利用できない場合のみの最小限のフォールバック
        if win_prob >= 0.5:
            return f"勝率{int(win_prob * 100)}%の案件です。"
        else:
            return f"勝率{int(win_prob * 100)}%の案件です。価格戦略の見直しを検討してください。"