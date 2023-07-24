import pandas as pd
from PublicDataReader.config.database import engine
from sqlalchemy import text
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# 폰트 적용
plt.rcParams['font.family'] = 'AppleGothic'

# 데이터를 불러오는 함수
def load_data(type="무관|전세|월세"):
    conn = engine.connect()
    query = """
            SELECT *
            FROM offi_rent_contract
            """

    if type == "전세":
        query += " WHERE monthly_rent = 0"
    elif type == "월세":
        query += " WHERE monthly_rent != 0"

    result = conn.execute(text(query)).fetchall()
    contract_data = pd.DataFrame(result)

    #contract_end_date가 None인 행 제거
    contract_data = contract_data.dropna(subset=['contract_end_date'])
    
    return contract_data

# 데이터 전처리 함수
def preprocess_data(data):
    # 날짜 열을 datetime 객체로 변환
    date_columns = ['contract_date', 'contract_end_date']
    for col in date_columns:
        data[col] = pd.to_datetime(data[col])
        data[col] = data[col].map(pd.Timestamp.timestamp)
    
    # (contract_end_date - contract_date)로 duration 계산
    data['duration'] = data['contract_end_date'] - data['contract_date']

    # 계약 기간을 월(Month) 로 변환
    data['duration_months'] = data['duration'] / (60 * 60 * 24 * 30)

    return data

def main():
    test_type = ["무관"]
    for type in test_type:
        contract_data = load_data(type)
        contract_data = preprocess_data(contract_data)

        # 변수들 간의 상관계수 계산
        correlation_matrix = contract_data.corr()

        # 계약기간과 상관계수 출력
        duration_correlation = correlation_matrix['duration'].to_dict()
        print("계약기간과 각 피쳐들의 상관계수:")
        for feature, corr in duration_correlation.items():
            print(f"{feature}: {corr}")

        # Create the Box Plot
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='building_id', y='duration_months', data=contract_data)
        plt.xlabel('오피스텔 ID')
        plt.ylabel('계약기간 (월)')
        plt.title('오피스텔 ID와 계약기간의 상관관계')
        plt.xticks(rotation=90)
        plt.show()
        

        
        
        

if __name__ == "__main__":
    main()