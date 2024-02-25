import pandas as pd
import logging
from datetime import datetime
from .utils import (read_data, get_calculate_list, calculate_purchase_cycle,
                    customer_seg, viewer_seg, labeled_data_in_dict, order_value_component,
                    hot_brand_in_class, component_of_class_s, earning_component)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s-%(name)s-%(levelname)s-%(message)s")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.info('started')

    data = read_data()
    logger.info('finished reading data, start classfication')

    current_date = datetime(2020, 3, 5)
    label_list = ['N', 'A', 'P', 'L', 'S', 'R']

    calculate_list = get_calculate_list(data)
    purchase_cycle, avg_cycle = calculate_purchase_cycle(data, calculate_list)
    print(f'\n消費者平均購物週期 = {round(avg_cycle, 2)}\n')

    buyer_list = customer_seg(purchase_cycle, avg_cycle)
    view_r = viewer_seg(data, avg_cycle)

    naplsr_label_list = pd.merge(buyer_list, view_r, how='outer')
    naplsr_label_list = naplsr_label_list[['user_id', 'label']]

    naplsr_percentage = naplsr_label_list['label'].value_counts().to_frame('count').reset_index(drop=False)
    naplsr_percentage['count_%'] = round(naplsr_percentage['count']/naplsr_percentage['count'].sum()*100, 2)
    print(naplsr_percentage)

    logger.info('\nfinished classfication, start EDA')
  
    data_by_label = labeled_data_in_dict(label_list, data, naplsr_label_list)
    order_value_component(label_list, data_by_label)
    hot_brand_in_class(label_list, data_by_label)
    component_of_class_s(buyer_list)
    earning_component(data, buyer_list, '2020-02-01', '2020-02-29', 'Feb')

    logger.info('finished')

