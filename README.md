# E-commerce Event Analysis Project

## Overview

This project aims to analyze users using eCommerce data and classify them in order to provide operational suggestions.

## Methodology

The analysis method used is NAPL classification, which focuses on the order count and the active status of users.\
Operators can use these dynamic labels to analyze user segments and make decisions, as well as create targeted marketing campaigns based on insights from the data analysis.

## Conclusion

This is the component of users:
![NAPLSR result](/images/naplrs_result.png)

### In the short term:

Give priority to the groups that are larger and more mobile in the dynamic tags.

* Potential Customer (R) Introduction\
   Offer first-time purchase discounts, free shipping, and other shopping incentives, as well as maintain communication and product advertisement exposure.

* New Customer (N) Conversion\
  Through repurchase offers, convert new customers (N) into active customers (A) with a higher customer value, thereby expanding a more stable revenue source group and at the same time preventing new customers from becoming lost customers (L).

### In the long term:

* Maintain Active Customers (A)\
  Design a loyalty program or membership rewards mechanism, and continue to interact and communicate with active customers (A) to prevent the extension of their repurchase cycles.

* Combine Category and Product Data Mining to Adjust to User Preferences\
  Integrate segmentation results with purchase categories and product data to grasp the preferences of different groups and adjust product development and marketing strategies.

## Module Structure

```plaintext
root/
  |──src/
  |   |── __init__.py
  |   |── main.py
  |   |── utils.py
  |   └── EDA.ipynb
  |── images/
  |   |── naplrs_result.png
  |── .gitignore
  |── README.md
  └── requirements.txt
```

## Dataset

[Link](https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-cosmetics-shop)
