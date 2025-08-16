import os
from typing import Dict, List
import json

class AIAnalyzer:
    def __init__(self):
        try:
            from openai import AzureOpenAI
            
            # API version
            api_version = os.getenv('AZURE_OPENAI_API_VERSION')
            endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            api_key = os.getenv('AZURE_OPENAI_API_KEY')
            
            if not all([api_version, endpoint, api_key]):
                raise ValueError("Azure OpenAI environment variables are required")
            
            self.client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version=api_version
            )
            self.deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
            if not self.deployment_name:
                raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME is required")
            print(f"AI Analyzer initialized successfully with API version: {api_version}")
        except Exception as e:
            print(f"AI Analyzer initialization failed: {e}")
            self.client = None
            self.deployment_name = None
    
    def analyze_bid_risks(self, tender: Dict, bid_amount: int, similar_awards: Dict, company_strengths: Dict) -> Dict:
        """AIを使用して詳細なリスク分析を行う"""
        
        if not self.client:
            return {
                "risk_factors": [],
                "opportunities": [],
                "strategic_advice": "",
                "confidence_adjustment": 0
            }
        
        # プロンプトの構築
        prompt = self._build_risk_analysis_prompt(tender, bid_amount, similar_awards, company_strengths)
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "あなたは建設業界の入札分析専門家です。過去のデータと企業の実績から、入札のリスクと戦略を分析してください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # レスポンスの解析
            analysis_text = response.choices[0].message.content
            
            # デフォルトの分析結果
            analysis = {
                "risk_factors": [],
                "opportunities": [],
                "strategic_advice": "",
                "confidence_adjustment": 0
            }
            
            # JSONとして解析を試みる
            try:
                # ```json や ``` を除去
                cleaned_text = analysis_text.strip()
                if '```json' in cleaned_text:
                    json_start = cleaned_text.find('```json') + 7
                    json_end = cleaned_text.rfind('```')
                    if json_end > json_start:
                        cleaned_text = cleaned_text[json_start:json_end].strip()
                elif cleaned_text.startswith('```'):
                    lines = cleaned_text.split('\n')
                    # 最初と最後の```を除去
                    if lines[0].strip() == '```' or lines[0].strip().startswith('```'):
                        lines = lines[1:]
                    if lines and (lines[-1].strip() == '```' or lines[-1].strip().startswith('```')):
                        lines = lines[:-1]
                    cleaned_text = '\n'.join(lines)
                
                # JSONパース
                parsed = json.loads(cleaned_text)
                
                # 必要なキーが存在することを確認し、正しい型であることを確認
                if isinstance(parsed, dict):
                    # リスク要因が配列であることを確認
                    if 'risk_factors' in parsed and isinstance(parsed['risk_factors'], list):
                        # 文字列のみを保持
                        parsed['risk_factors'] = [r for r in parsed['risk_factors'] if isinstance(r, str)]
                    # opportunitiesも同様に処理
                    if 'opportunities' in parsed and isinstance(parsed['opportunities'], list):
                        parsed['opportunities'] = [o for o in parsed['opportunities'] if isinstance(o, str)]
                    # strategic_adviceが文字列であることを確認
                    if 'strategic_advice' in parsed and not isinstance(parsed['strategic_advice'], str):
                        parsed['strategic_advice'] = str(parsed['strategic_advice'])
                    # confidence_adjustmentが数値であることを確認
                    if 'confidence_adjustment' in parsed:
                        try:
                            parsed['confidence_adjustment'] = float(parsed['confidence_adjustment'])
                        except:
                            parsed['confidence_adjustment'] = 0
                    
                    analysis = parsed
                    
            except Exception as e:
                # パースエラーの場合はデフォルト値を使用
                print(f"AI response parsing error: {e}")
                print(f"Raw response: {analysis_text[:500]}...")  # デバッグ用
            
            return analysis
            
        except Exception as e:
            print(f"AI Analysis error: {e}")
            # エラー時はフォールバック
            return {
                "risk_factors": [],
                "opportunities": [],
                "strategic_advice": "",
                "confidence_adjustment": 0
            }
    
    def _build_risk_analysis_prompt(self, tender: Dict, bid_amount: int, similar_awards: Dict, company_strengths: Dict) -> str:
        """リスク分析用のプロンプトを構築"""
        
        prompt = f"""
以下の入札案件について、詳細なリスク分析を行ってください。

## 案件情報
- 案件名: {tender.get('title', 'N/A')}
- 地域: {tender.get('prefecture', 'N/A')} {tender.get('municipality', 'N/A')}
- 予定価格: {tender.get('estimated_price', 0):,}円
- 最低制限価格: {tender.get('minimum_price', 0):,}円
- 入札方式: {tender.get('bid_method', 'N/A')}
- 用途: {tender.get('use_type', 'N/A')}
- 延床面積: {tender.get('floor_area_m2', 0):,}㎡

## 入札額
- 提案入札額: {bid_amount:,}円
- 予定価格比: {(bid_amount / tender.get('estimated_price', 1) * 100):.1f}%

## 類似案件の落札実績
- 分析対象件数: {similar_awards.get('count', 0)}件
- 落札額中央値: {int(similar_awards.get('median', 0)):,}円
- 落札額最小値: {int(similar_awards.get('min', 0)):,}円
- 落札額最大値: {int(similar_awards.get('max', 0)):,}円
- 平均参加社数: {float(similar_awards.get('avg_participants', 0)):.1f}社

## 自社の実績
- 総落札件数: {company_strengths.get('total_awards', 0)}件
- 該当地域での実績: {company_strengths.get('prefectures', {}).get(tender.get('prefecture', ''), 0)}件
- 該当用途での実績: {company_strengths.get('use_types', {}).get(tender.get('use_type', ''), 0)}件
- 平均落札率: {float(company_strengths.get('avg_win_rate', 0) or 0):.1f}%

以下の観点から分析し、**純粋なJSON形式のみで**回答してください。マークダウンのコードブロック（```）は使用しないでください：

1. risk_factors: リスク要因のリスト（最大5つ）
2. opportunities: 有利な点・チャンスのリスト（最大3つ）
3. strategic_advice: 具体的な戦略アドバイス（200文字以内）
4. confidence_adjustment: 信頼度の調整値（-0.2〜+0.2の範囲）

以下のようなJSON形式で回答してください（```は付けないこと）：
{{
    "risk_factors": [
        "地域での実績が少なく、地元企業が優位",
        "類似案件の平均参加社数が多く、競争激化の可能性"
    ],
    "opportunities": [
        "価格設定が類似案件の中央値に近く競争力あり",
        "該当用途での豊富な実績"
    ],
    "strategic_advice": "技術提案書で差別化を図り、過去の類似実績を強調することを推奨",
    "confidence_adjustment": 0.05
}}
"""
        return prompt
    
    def generate_detailed_recommendation(self, rank: str, win_prob: float, analysis: Dict, 
                                        tender: Dict, basis: Dict, company_strengths: Dict) -> str:
        """AIの分析結果を基に推奨事項を生成"""
        
        if not self.client:
            # フォールバック
            if rank in ['A', 'B']:
                return "有望な案件です。技術提案書の充実と、過去実績のアピールを重視して入札準備を進めてください。"
            elif rank == 'C':
                return "妥当な価格設定ですが、競合分析を強化し、差別化ポイントを明確にすることを推奨します。"
            else:
                return "リスクが高い案件です。価格戦略の見直しか、他案件への注力を検討してください。"
        
        prompt = f"""
入札案件の詳細データと分析結果に基づいて、詳細で実践的な推奨事項を生成してください。

## 案件情報
- 案件名: {tender.get('title', 'N/A')}
- 地域: {tender.get('prefecture', 'N/A')} {tender.get('municipality', 'N/A')}
- 入札方式: {tender.get('bid_method', 'N/A')}
- 用途: {tender.get('use_type', 'N/A')}

## 予測結果
- ランク: {rank}
- 勝率: {win_prob * 100:.0f}%
- 予定価格比: {basis.get('bid_vs_estimated_ratio', 0):.1f}%

## 類似案件データ
- 分析件数: {basis.get('n_similar', 0)}件
- 落札額中央値: {basis.get('similar_median', 0):,}円
- 価格差: {basis.get('price_gap', 0):,}円

## 自社実績
- 総落札件数: {company_strengths.get('total_awards', 0)}件
- 該当地域実績: {company_strengths.get('prefectures', {}).get(tender.get('prefecture', ''), 0)}件
- 該当用途実績: {company_strengths.get('use_types', {}).get(tender.get('use_type', ''), 0)}件

## AI分析結果
- リスク要因: {', '.join(analysis.get('risk_factors', []))}
- 有利な点: {', '.join(analysis.get('opportunities', []))}
- 戦略アドバイス: {analysis.get('strategic_advice', '')}

以下の5つのセクションで具体的な推奨事項を作成してください。各セクションは必ず含めてください：

### 推奨事項

#### 1. **価格戦略**
類似案件の落札データを踏まえ、現在の入札額が適切か、調整が必要かを具体的に説明（100-150文字）

#### 2. **競争優位性の確立**  
自社の実績を踏まえ、他社との差別化を図る具体的な方法（100-150文字）

#### 3. **技術提案書のポイント**
特に強調すべき技術面、実績面、地域貢献などを箇条書きで3-4項目（各項目50文字程度）

#### 4. **リスク対策**
特定されたリスクへの具体的な対応方法を箇条書きで2-3項目（各項目50文字程度）

#### 5. **今後のアクション**
入札までに行うべき具体的な準備や検討事項を箇条書きで2-3項目（各項目50文字程度）

文体は専門的でありながら分かりやすく、実務担当者がすぐに行動できるレベルで記述してください。
各セクションは完結させ、途中で切れないようにしてください。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "建設業界の入札戦略アドバイザーとして、簡潔で実践的なアドバイスを提供してください。必ず指定されたフォーマットに従い、各セクションを完結させてください。文字数制限を守り、途中で切れないようにしてください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Recommendation generation error: {e}")
            # フォールバック
            if rank in ['A', 'B']:
                return "有望な案件です。技術提案書の充実と、過去実績のアピールを重視して入札準備を進めてください。"
            elif rank == 'C':
                return "妥当な価格設定ですが、競合分析を強化し、差別化ポイントを明確にすることを推奨します。"
            else:
                return "リスクが高い案件です。価格戦略の見直しか、他案件への注力を検討してください。"
    
    def generate_recommendation(self, rank: str, win_prob: float, analysis: Dict) -> str:
        """シンプルな推奨事項を生成（互換性のため）"""
        # generate_detailed_recommendationを呼び出す
        return self.generate_detailed_recommendation(rank, win_prob, analysis, {}, {}, {})