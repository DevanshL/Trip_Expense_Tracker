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
                    comment = period_data.get('comment')
                    expense_data = period_data

                    total_income = expense_data['total_income']
                    persons = expense_data['persons']
                    payer = expense_data['payer']
                    person_expenses = expense_data['person_expenses']

                    # Correct calculation of total expenses
                    total_expense = sum(sum(person.values()) for person in person_expenses.values())
                    remaining_budget = total_income - total_expense

                    col1, col2, col3 = st.columns(3)
                    col1.metric('Total Income', f'{currency} {total_income}')
                    col2.metric('Total Expense', f'{currency} {total_expense}')
                    col3.metric('Remaining Budget', f'{currency} {remaining_budget}')
                    st.text(f'Comment: {comment}')

                    # Calculate the amount owed by each person
                    amount_owed = {
                        person: sum(person_expenses[person].values())
                        for person in persons if person != payer
                    }

                    st.write(f'Amount Owed to the Payment Maker:({payer})')
                    for person, amount in amount_owed.items():
                        st.write(f'{person}: {currency} {amount:.2f}')

                    # Sankey Chart
                    label = ['Total Income'] + persons + expenses + ['Total Expense', 'Remaining Budget']
                    source = [0] * len(persons) + [label.index(person) for person in persons for _ in expenses] + [0, 0]
                    target = list(range(1, 1 + len(persons))) + [label.index(expense) for _ in persons for expense in expenses] + [label.index('Total Expense'), label.index('Remaining Budget')]
                    value = [total_income / len(persons)] * len(persons) + [person_expenses[person][expense] for person in persons for expense in expenses] + [total_expense, remaining_budget]

                    link = dict(source=source, target=target, value=value)
                    node = dict(label=label, pad=20, thickness=30, color='cyan')
                    data = go.Sankey(link=link, node=node)

                    fig = go.Figure(data)
                    fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
                    st.plotly_chart(fig, use_container_width=True)

