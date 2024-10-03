import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


def get_conn():
    HOST = 'ep-green-butterfly-a26qo6f3.eu-central-1.aws.neon.tech'
    PORT = 5432
    DATABASE = 'datadb'
    USER = 'datadb_owner'
    PASSWORD = 'BmV3l0GArdNT'

    connection = psycopg2.connect(
        host = HOST,
        port = PORT,
        database = DATABASE,
        user = USER,
        password = PASSWORD,
    )
    return connection

connection = get_conn()

cursor = connection.cursor()
query = """select to_char(i.infdata, 'YYYY') as year, round(avg(i.inflation), 2) as inflation 
from cd.inflation i 
group by to_char(i.infdata, 'YYYY')
order by to_char(i.infdata, 'YYYY');"""
cursor.execute(query)
data = cursor.fetchall()
cursor.close()
InfDf = pd.DataFrame(data, columns = ['years', 'inflation'])

st.subheader('График инфляции')

plt.figure(figsize=(15,5))
axes = sns.lineplot(data=InfDf, x="years", y="inflation")
plt.title('График инфляции', fontsize=30)
axes.set_xlabel('Год', fontsize=25)
axes.set_ylabel('Инфляция', fontsize=25)
plt.grid(True)
plt.tight_layout()
st.pyplot(plt)

cursor = connection.cursor()
query = """select * 
from cd.nameprof n;"""
cursor.execute(query)
data = cursor.fetchall()
cursor.close()
profName = pd.DataFrame(data = data, columns = ['nameid', 'name'])

listName = tuple(profName['name'])

def get_salary(name):
    connection = get_conn()
    cursor = connection.cursor()
    query = "select p.profid, n.nameprof, p.salary, to_char(p.salarydata, 'YYYY') from cd.profession p join cd.nameprof n on p.profnameid = n.nameid where n.nameprof = %s;"
    cursor.execute(query, (name, ))
    data = cursor.fetchall()
    cursor.close()
    dataProf = pd.DataFrame(data = data, columns = ['nameid', 'nameprof', 'salary', 'years'])
    return dataProf

option = st.selectbox(
    "Посмотреть зарплату",
    listName,
    index=None,
    placeholder="Выберите профессию",
)

dataProf = None

if option is not None:
    st.write(f'Зарплата: {option}')
    dataProf = get_salary(option)
    dataProf['true_salary'] = dataProf['salary'] * 1000
    plt.figure(figsize = (15,5))
    axes = sns.barplot(data=dataProf, x = 'years', y = 'true_salary')
    plt.title('График зарплат', fontsize = 30)
    axes.set_xlabel('Год', fontsize = 25)
    axes.set_ylabel('Зарплата', fontsize = 25)
    plt.tight_layout()
    st.pyplot(plt)

if dataProf is not None:
    st.subheader('График зарплат и инфляции в одном графике')
    InfDf['year'] = (pd.to_datetime(InfDf['years']) - pd.DateOffset(years=1)).dt.year
    dataProf['year'] = (pd.to_datetime(dataProf['years'])).dt.year
    newDf = pd.merge(InfDf[['inflation','year']], dataProf[['nameprof','salary','year']], how = 'inner', on = 'year')
    newDf['true_salary'] = newDf['salary'] * 1000
    newDf['newSalary'] = newDf['true_salary'] * (1 + newDf['inflation'] / 100)
    newDf['new_salary'] = pd.concat([pd.Series(newDf.iloc[0,4]),newDf[:-1]['newSalary']], ignore_index = True)
    # График
    fig, axes = plt.subplots(1, 1, figsize=(15, 5))
    sns.lineplot(data=newDf, x='year', y='true_salary', label="Средняя зарплата", ax=axes)
    axes = sns.lineplot(data=newDf, x='year', y='new_salary', label="Зарплата по инфляции", ax=axes)
    axes.set_xlabel('Год', fontsize=25)
    axes.set_ylabel('Зарплата', fontsize=25)
    plt.legend()
    st.pyplot(plt)