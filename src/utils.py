import os
import pandas as pd
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from datetime import datetime

logging.basicConfig(format="%(asctime)s-%(name)s-%(levelname)s-%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

current_date = datetime(2020, 3, 5)

def read_data() -> pd.DataFrame:
    '''
    Read the columns we need in raw data.
    '''
    DATASET = os.path.join(os.getcwd(), "data")
        
    data = {}
    for filename in os.listdir(DATASET):
        data_tmp = pd.read_csv(f'{DATASET}/{filename}')
        data[filename] = data_tmp
        logger.info(f'{filename} is read')

    data_all = pd.DataFrame()
    for key in data.keys():
        data_all = pd.concat([data_all, data[key]])
        
    data_all = data_all.sort_values(by='event_time').reset_index(drop=True)

    data_all['event_time'] = pd.to_datetime(data_all['event_time']).dt.tz_localize(None)
    data_all['event_type'] = data_all['event_type'].astype('str')
    data_all['category_code'] = data_all['category_code'].astype('str')
    data_all['brand'] = data_all['brand'].astype('str')

    return data_all


def get_calculate_list(data: pd.DataFrame) -> pd.DataFrame:
    '''
    Get the customer list that will be used to calculate average purchase cycle.
    '''
    buyer = data[data['event_type']=='purchase']
    buyer_session_record = buyer[['user_id', 'user_session']].drop_duplicates(subset=['user_id', 'user_session']).reset_index(drop=True)
    user_purchase_count = buyer_session_record.groupby('user_id')['user_session'].count().to_frame('count').reset_index(drop=False)

    purchase_count = buyer_session_record.groupby('user_id')['user_session'].count()
    purchase_count = purchase_count.value_counts().to_frame('count').reset_index(drop=False).sort_values(by='user_session', ascending=True)
    purchase_count = purchase_count.rename(columns={'user_session':'purchase_count'}).reset_index(drop=True)
    purchase_count['count_%'] = round(purchase_count['count']/purchase_count['count'].sum()*100, 2)
    threshold_value = purchase_count[purchase_count['count_%'] > 0.1]['purchase_count'].iloc[-1]

    calculate_list = user_purchase_count[(user_purchase_count['count']>1) & (user_purchase_count['count']<=threshold_value)]

    return calculate_list


def calculate_purchase_cycle(data: pd.DataFrame, calculate_list: list) -> (pd.DataFrame, float):
    '''
    Calculate the average purchase cycle and return a dataframe containing personal purchase cycle.
    '''
    purchase_data = data[data['event_type']=='purchase']
    purchase_data = purchase_data[['event_time', 'user_id', 'user_session']].drop_duplicates(subset=['event_time', 'user_id', 'user_session'])
    purchase_data['date'] = purchase_data['event_time'].dt.date
    purchase_data = purchase_data.sort_values(['user_id', 'event_time'], ascending=True).reset_index(drop=True)
    
    buyer_list = list(purchase_data['user_id'].unique())
    buyer_list.sort()

    cycle_list = []
    order_count_list = []
    last_order_date_list = []
    
    for i in tqdm(buyer_list):
        data_tmp = purchase_data[purchase_data['user_id']== i]
        order_count = len(data_tmp)
        last_order_date = data_tmp['event_time'].iloc[-1]
        
        order_count_list.append(order_count)
        last_order_date_list.append(last_order_date)

        if order_count == 1:           
            personal_cycle = (current_date - last_order_date.replace(tzinfo=None)).days + 1
            cycle_list.append(personal_cycle)
            continue
        
        else:
            total_diff = 0
            for j in range(1, order_count):
                days_diff = ((data_tmp['event_time'].iloc[j] - data_tmp['event_time'].iloc[j-1]).days) + 1
                total_diff += days_diff

            personal_cycle = total_diff/order_count
            cycle_list.append(personal_cycle)
            
    purchase_cycle = pd.DataFrame({'user_id': buyer_list, 
                                   'purchase_cycle': cycle_list, 
                                   'order_count': order_count_list, 
                                   'last_order':last_order_date_list})
    
    purchase_cycle['last_order'] = purchase_cycle['last_order'].dt.tz_localize(None)
    purchase_cycle['newest_cycle'] = (current_date - purchase_cycle['last_order']).dt.days + 1

    purchase_cycle_cal = purchase_cycle[purchase_cycle['user_id'].isin(calculate_list['user_id'])]
    avg_cycle = purchase_cycle_cal['purchase_cycle'].mean()

    return purchase_cycle, avg_cycle


def customer_seg(purchase_cycle: pd.DataFrame, avg_cycle: float) -> pd.DataFrame:
    '''
    Segment the customer based on their order count and last order date.
    '''
    buyer_list = purchase_cycle.copy()
    purchase_cycle_3_times = avg_cycle * 3
    
    buyer_list.loc[(buyer_list['order_count'] == 1) & (buyer_list['newest_cycle'] < purchase_cycle_3_times), 'label'] = 'N'
    buyer_list.loc[(buyer_list['order_count'] > 1) & (buyer_list['newest_cycle'] < purchase_cycle_3_times), 'label'] = 'A'
    buyer_list.loc[(buyer_list['order_count'] > 1) & (buyer_list['newest_cycle'] > purchase_cycle_3_times), 'label'] = 'P'
    buyer_list.loc[(buyer_list['order_count'] == 1) & (buyer_list['newest_cycle'] > purchase_cycle_3_times), 'label'] = 'L'
    buyer_list.loc[buyer_list['newest_cycle'] >90, 'label'] = 'S'

    return buyer_list


def viewer_seg(data: pd.DataFrame, avg_cycle) -> pd.DataFrame:
    '''
    Get 'ready to buy users' from data that have not been purchased but have been added products into cart recently.
    '''
    cart_list = data.loc[data['event_type'] == 'cart', 'user_id']
    purchase_list = data.loc[data['event_type'] == 'purchase', 'user_id']
    user_ready_to_buy = pd.DataFrame(cart_list[~cart_list.isin(purchase_list.unique())].unique()).rename(columns={0:'user_id'})

    data_cart = data[data['user_id'].isin(user_ready_to_buy['user_id'])]
    last_data_cart = data_cart.sort_values('event_time').groupby('user_id').last().reset_index()
    last_data_cart['event_time'] = last_data_cart['event_time'].dt.tz_localize(None)
    last_data_cart['last_cart_days'] = (current_date - last_data_cart['event_time']).dt.days + 1

    label_r = last_data_cart[last_data_cart['last_cart_days'] < avg_cycle]
    label_r = pd.DataFrame(label_r['user_id'].unique()).rename(columns={0:'user_id'})
    label_r['label'] = 'R'

    return label_r


def get_labeled_data(data:pd.DataFrame, naplsr_label_list:pd.DataFrame, target_label:str) -> pd.DataFrame:
    '''
    Get the data that belongs to the target label.
    '''
    target_user = naplsr_label_list[naplsr_label_list['label']==target_label]
    target_data = data[data['user_id'].isin(target_user['user_id'])] 

    return target_data


def get_labeled_order_value(data_by_label:dict, label_list:list) -> dict:
    '''
    Get the single order's value in each label.
    '''
    order_value_dict = {}
    for label in label_list:
        purchase_data = data_by_label[label].loc[data_by_label[label]['event_type'] == 'purchase']
        order_value_data = purchase_data.groupby('user_session')['price'].sum().sort_values(ascending=False).to_frame().reset_index(drop=False).rename(columns={'price':'order_value'})
        order_value_data = order_value_data[order_value_data['order_value']>0]
        order_value_data = order_value_data[order_value_data['order_value'] < order_value_data['order_value'].quantile(0.95)]
        order_value_dict[label] = order_value_data
    
    return order_value_dict


def get_labeled_data(data:pd.DataFrame, naplsr_label_list:pd.DataFrame, target_label:str) -> pd.DataFrame:
    '''
    Get the data that belongs to the target label.
    '''       
    target_user = naplsr_label_list[naplsr_label_list['label']==target_label]
    target_data = data[data['user_id'].isin(target_user['user_id'])] 

    return target_data


def labeled_data_in_dict(label_list: list, data: pd.DataFrame, naplsr_label_list: pd.DataFrame) -> dict:
    '''
    Get the data that belongs to the target label in dict.
    '''
    data_by_label = {}
    for label in label_list:
        data_by_label[label] = get_labeled_data(data, naplsr_label_list, label)

    return data_by_label


def order_value_component(label_list: list, data_by_label: dict) -> None:
    '''
    Plot the component of order value in each label.
    '''
    order_value_dict = get_labeled_order_value(data_by_label, label_list)
    all_order_value = pd.concat([df.assign(label=label) for label, df in order_value_dict.items()])

    plt.figure(figsize=(5, 3))
    sns.boxplot(x='label', y='order_value', hue='label', data=all_order_value, palette="muted")
    # plt.legend([],[], frameon=False)
    
    plt.title('Order value by Label')
    plt.xlabel('Label')
    plt.ylabel('Order value')
    plt.show() 

    return None


def hot_brand_in_class(label_list:list, data_by_label:dict) -> None:
    '''
    Top 10 hot brand in each class.
    '''
    hot_brand = {}

    for label in label_list:
        if label != 'R':
            data_by_label[label] = data_by_label[label].loc[data_by_label[label]['event_type']=='purchase']
            hot_brand[label] = data_by_label[label]['brand'].value_counts().head(11).to_frame('count').reset_index(drop=False)
        else:
            data_by_label[label] = data_by_label[label].loc[data_by_label[label]['event_type']=='cart']
            hot_brand[label] = data_by_label[label]['brand'].value_counts().head(11).to_frame('count').reset_index(drop=False)

    wide_format_df = pd.DataFrame()

    for key, df in hot_brand.items():
        wide_format_df[key] = df['brand'].reset_index(drop=True)

    wide_format_df.drop(index=0, inplace=True)
    return None


def component_of_class_s(buyer_list: pd.DataFrame) -> None:
    '''
    Plot the component of class S.
    '''
    buyer_list_s = buyer_list[buyer_list['label']=='S']

    class_s_from_a = buyer_list_s.loc[buyer_list_s['order_count'] > 1, 'user_id'].count()
    class_s_from_n = buyer_list_s.loc[buyer_list_s['order_count'] == 1, 'user_id'].count()

    labels = ['Order count > 1', 'Order count = 1']
    sizes = [class_s_from_a, class_s_from_n]
    colors = ['slateblue', 'slategray']

    plt.figure(figsize=(4, 4))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title("Single customer's order count in class S")
    plt.show()   

    return None 


def earning_component(data:pd.DataFrame, buyer_list:list,  start_date:str, end_date:str, period:str) -> None:
    '''
    Plot the component of revenue in the period.
    '''
    period_data = data[(data['event_time']>=start_date) & (data['event_time']<=end_date)]
    period_purchase_data = period_data[period_data['event_type']=='purchase']
    period_purchase_data['label'] = period_purchase_data['user_id'].map(buyer_list.set_index('user_id')['label'])
    period_purchase_count = period_purchase_data['label'].value_counts().to_frame('count').reset_index(drop=False)
    period_purchase_price = period_purchase_data.groupby('label')['price'].sum().to_frame('price').reset_index(drop=False)
    period_purchase_record = pd.merge(period_purchase_count, period_purchase_price, how='outer')

    plt.figure(figsize=(2, 4))
    plt.bar(period_purchase_record['label'], period_purchase_record['count'], label='Count', alpha=0.5, color='slateblue')
    plt.ylabel('Total')
    plt.title(f'# of buyers in {period}')
    plt.show()

    plt.figure(figsize=(2, 4))
    plt.bar(period_purchase_record['label'], period_purchase_record['price'], label='Count', alpha=0.5, color='slateblue')
    plt.ylabel('Total')
    plt.title(f'Revenue in {period}')
    plt.show()

    return None

