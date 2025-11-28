# Import python packages
import streamlit as st
import requests as rqs;
import pandas as pd;
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f"Customize your smoothie :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom smoothie!
  """
)

name = st.text_input("Name on smoothie:")
st.write("The name on your smoothie will be:", name)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'), col('search_on'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

# panda dataframe
pd_df = my_dataframe.to_pandas()

ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections = 5
    #default=["Apples", "Strawberries"],
)

if ingredients:
    ingredients_str = ''
    for fruit_chosen in ingredients:
        ingredients_str += fruit_chosen + ' '

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        st.subheader(fruit_chosen + ' nutrition information')
        smoothiefroot_response = rqs.get("https://my.smoothiefroot.com/api/fruit/{search_on}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    #st.write(ingredients_str)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values('""" + ingredients_str + """', '""" + name + """')"""

    #st.write(my_insert_stmt)
    #st.stop()
    time_to_insert = st.button("Submit order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your smoothie is ordered, ' + name + '!', icon="✅")
