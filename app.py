import psycopg2
import pandas as pd
import numpy as np
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
