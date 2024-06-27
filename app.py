import streamlit as st
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import calendar
from datetime import datetime
from database import insert_period, get_all_periods, get_period

# Constants
expenses = ['Accommodation', 'Food and Drinks', 'Transport', 'Entertainment', 'Shopping', 'Miscellaneous']
currency = 'RS'
page_title = "Trip Expense Tracker"
page_icon = ':money_with_wings:'  # webfx.com
layout = "centered"

# Configure the page
st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

years = [datetime.today().year, datetime.today().year - 1]
months = list(calendar.month_name[1:])

# Hide Streamlit style
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Navigation
selected = option_menu(menu_title=None,
                       options=['Data Entry', 'Data Visualization'],
                       icons=['pencil-fill', 'bar-chart-fill'],  # bootstrap icons
                       orientation='horizontal',
)

# Initialize session state variables if they don't exist
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'total_income' not in st.session_state:
    st.session_state.total_income = 0
if 'num_persons' not in st.session_state:
    st.session_state.num_persons = 1
if 'persons' not in st.session_state:
    st.session_state.persons = []

# Input section
if selected == 'Data Entry':
    st.header(f'Data Entry in Rupees')

    if st.session_state.step == 1:
        with st.form('initial_form'):
            col1, col2 = st.columns(2)
            month = col1.selectbox('Select Month:', months)
            year = col2.selectbox('Select Year:', years)

            total_income = st.number_input('Total Income for the Trip:', min_value=0, format='%i', step=10)
            num_persons = st.number_input('Number of Persons:', min_value=1, value=1)
            submitted = st.form_submit_button('Next')

            if submitted:
                st.session_state.step = 2
                st.session_state.month = month
                st.session_state.year = year
                st.session_state.total_income = total_income
                st.session_state.num_persons = num_persons
    
    if st.session_state.step == 2:
        st.session_state.persons = []
        with st.form('persons_form'):
            st.write('Enter the names of the persons:')
            for i in range(st.session_state.num_persons):
                person_name = st.text_input(f'Name of Person {i + 1}', key=f'person_{i}')
                st.session_state.persons.append(person_name)
            submitted = st.form_submit_button('Next')
            if submitted:
                st.session_state.step = 3

    if st.session_state.step == 3:
        with st.form('expenses_form'):
            payer = st.selectbox('Select the Payment Maker:', st.session_state.persons, key='payer')

            person_expenses = {person: {} for person in st.session_state.persons}

            with st.expander('Expenses'):
                for expense in expenses:
                    for person in st.session_state.persons:
                        person_expenses[person][expense] = st.number_input(f'{expense} by {person}:', min_value=0, format='%i', step=10, key=f'{expense}_{person}_{expense}')

            with st.expander('Extras'):
                for person in st.session_state.persons:
                    person_expenses[person]['extra'] = st.number_input(f'Extra Expenses by {person}:', min_value=0, format='%i', step=10, key=f'extra_{person}')
            
            with st.expander('Comment'):
                comment = st.text_area("Comment", placeholder='Enter a comment here -----')

            submitted = st.form_submit_button('Save Data')
            if submitted:
                period = f"{st.session_state.year}_{st.session_state.month}"
                total_income = st.session_state.total_income
                persons = st.session_state.persons
                
                if insert_period(period, total_income, persons, payer, person_expenses, comment):
                    st.success('Data Saved')
                    st.session_state.step = 1
                else:
                    st.error('Failed to save data')

def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

# Data visualization section
if selected == 'Data Visualization':
    st.header('Data Visualization')
    with st.form('saved_periods'):
        periods = get_all_periods()
        if not periods:
            st.error('No periods found in the database.')
        else:
            period = st.selectbox('Select Period:', periods)
            submitted = st.form_submit_button('Plot Period')
            if submitted:
                period_data = get_period(period)
                if not period_data:
                    st.error('No data found for the selected period.')
                else:
                    # Initialize totals
                    total_income = 0
                    total_expense = 0
                    payer = ""
                    comment = ""
                    latest_entry = max(period_data, key=lambda x: x[1])  # Assuming created_at is at index 1

                    # Initialize aggregated data
                    aggregated_data = {}

                    total_income = safe_int(latest_entry[2])  # Assuming total_income is at index 2
                    payer = latest_entry[3]  # Assuming payer is at index 3
                    comment = latest_entry[12]  # Assuming comment is at index 12

                    for data in period_data:
                        if data[1] == latest_entry[1]:  # Assuming created_at is at index 1
                            person = data[0]  # Assuming name is at index 0
                            if person not in aggregated_data:
                                aggregated_data[person] = {expense: 0 for expense in expenses + ['Extra']}

                            aggregated_data[person]['Accommodation'] += safe_int(data[4])  # Assuming accommodation is at index 4
                            aggregated_data[person]['Food and Drinks'] += safe_int(data[5])  # Assuming food_drinks is at index 5
                            aggregated_data[person]['Transport'] += safe_int(data[6])  # Assuming transport is at index 6
                            aggregated_data[person]['Entertainment'] += safe_int(data[7])  # Assuming entertainment is at index 7
                            aggregated_data[person]['Shopping'] += safe_int(data[8])  # Assuming shopping is at index 8
                            aggregated_data[person]['Miscellaneous'] += safe_int(data[9])  # Assuming miscellaneous is at index 9
                            aggregated_data[person]['Extra'] += safe_int(data[10])  # Assuming extra is at index 10

                            total_expense += sum(aggregated_data[person].values())

                    remaining_budget = total_income - total_expense

                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    col1.metric('Total Income', f'{currency} {total_income:,}')
                    col2.metric('Total Expense', f'{currency} {total_expense:,}')
                    col3.metric('Remaining Budget', f'{currency} {remaining_budget:,}')
                    st.text(f'Comment: {comment}')

                    # Calculate the amount owed by each person
                    amount_owed = {
                        person: sum(aggregated_data[person].values())
                        for person in aggregated_data if person != payer
                    }

                    st.write(f'Amount Owed to the Payment Maker ({payer}):')
                    for person, amount in amount_owed.items():
                        st.write(f'{person}: {currency} {amount:,}')

                    # Prepare data for the Sankey chart
                    persons = list(aggregated_data.keys())
                    labels = ['Total Income'] + persons + expenses + ['Total Expense', 'Remaining Budget']
                    source = [0] * len(persons) + [labels.index(person) for person in persons for _ in expenses] + [0, 0]
                    target = list(range(1, 1 + len(persons))) + [labels.index(expense) for _ in persons for expense in expenses] + [labels.index('Total Expense'), labels.index('Remaining Budget')]
                    values = [total_income / len(persons) if len(persons) > 0 else 0] * len(persons) + [aggregated_data[person][expense] for person in persons for expense in expenses] + [total_expense, remaining_budget]

                    link = dict(source=source, target=target, value=values)
                    node = dict(label=labels, pad=20, thickness=30, color='cyan')
                    data = go.Sankey(link=link, node=node)

                    fig = go.Figure(data)
                    fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
                    st.plotly_chart(fig, use_container_width=True)
