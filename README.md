## E-commerce Event Analysis Project

### Overview

This project aims to use eCommerce data to analyze users and classify them to make some operation suggestions.

### Methodology

The analysis method is NAPL classification, focusing on the order count and the active status of users.\
The operator can use these dynamic labels to analyze the components of users and make some decisions and marketing campaigns to specific classes by the insights from data analysis.

### Conclusion

This is the component of users:
![可愛的貓咪](/images/naplrs_result.png)

According to the users' component, These are 


#### In the short term:

Give priority to the groups that are larger and more mobile in the dynamic tags:

**1. Potential Customer (R) Introduction:**\
   Offer first-time purchase discounts, free shipping, and other shopping incentives, as well as maintain communication and product advertisement exposure.

**2. New Customer (N) Conversion:**\
  Through repurchase offers, convert new customers (N) into active customers (A) with a higher customer value, thereby expanding a more stable revenue source group and at the same time preventing new customers from becoming lost customers (L).

#### In the long term:

**1. Maintain Active Customers (A)**\
  Design a loyalty program or membership rewards mechanism, and continue to interact and communicate with active customers (A) to prevent the extension of their repurchase cycles.

**2. Combine Category and Product Data Mining to Adjust to User Preferences:**\
  Integrate segmentation results with purchase categories and product data to grasp the preferences of different groups and adjust product development and marketing strategies.

## Module Structure

```plaintext
root/
  |──src/
  |   |── __init__.py
  |   |── main.py
  |   |── utils.py
  |   └── EDA.ipynb 
  |── .gitignore
  |── README.md
  └── requirements.txt
```
