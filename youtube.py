import streamlit as st
import numpy as np
import pandas as pd
import datetime
import json
import matplotlib.pyplot as plt
from calendar import monthrange

def get_title(title):
    return title[18:]

def get_channel(subtitles):
    return subtitles[0]['name']

def get_channel_url(subtitles):
    return subtitles[0]['url']

def get_product(product):
    return product[0]

def get_year(dt):
    return dt.year

def get_month(dt):
    return dt.month

def get_day(dt):
    return dt.day

def get_weekday(dt):
    return dt.weekday

def get_hour(dt):
    return dt.hour

def count_rows(rows):
    return len(rows)

def first_monday(year,month):
    for i in range(1,8):
        if datetime.date(year,month,i).weekday()==0:
            return i

def f(x):
    return "Mon. "+str(x)

st.title("Youtube data")

tab1, tab2 = st.tabs(["Analyse your history","How to download your history"])

with tab1:
    st.header("1. Import your history :")
    st.sidebar.header("Parameters :")

    file = st.file_uploader("Upload your youtube history as a .json",'json')

with tab2:
    st.subheader("1. Go to takeout.google.com with your youtube account")
    st.subheader("2. Deselect all and scroll down to your youtube data")
    st.image('tuto picture/1.png')
    st.subheader("3. Change the history format to JSON")
    st.image('tuto picture/2.png')
    st.subheader("4. You can know export and download your data")
    st.subheader('5. Finnaly drag and drop the "watch-history.json" file to the app')

if file is not None:

    df_histo = pd.read_json(file)

    mask = pd.isna(df_histo["details"])
    df_histo = df_histo[mask]
    df_histo = df_histo.drop(columns=['products', 'activityControls', 'description', 'details', 'header'])
    df_histo["time"] = pd.to_datetime(df_histo["time"])
    df_histo["title"] = df_histo["title"].map(get_title)
    df_histo["channel"] = df_histo["subtitles"].map(get_channel, na_action='ignore')
    df_histo["channel_url"] = df_histo["subtitles"].map(get_channel_url, na_action='ignore')
    df_histo = df_histo.drop(["subtitles"],axis=1)
    df_histo["year"] = df_histo["time"].map(get_year)
    df_histo["month"] = df_histo["time"].map(get_month)
    df_histo["day"] = df_histo["time"].map(get_day)
    df_histo["weekday"] = df_histo["time"].map(get_weekday)
    df_histo["hour"] = df_histo["time"].map(get_hour)

    st.header("2. Look at your data :")
    st.subheader("You watch a total of "+str(len(df_histo))+" videos")
    by_year = df_histo.groupby(["year"]).apply(count_rows)
    fig, ax = plt.subplots()
    ax.bar(by_year.index,by_year.values)
    plt.xlabel('Year')
    plt.ylabel('Number of video')
    plt.title('Number of video viewed each year')
    st.pyplot(fig)

    #st.bar_chart(by_year)

    year = st.sidebar.selectbox("Choose a year :",np.append(by_year.index.array,"All"))

    col1,col2 = st.columns(2)

    # year chart
    with col1:

        if year=="All":
            df_year = df_histo
        else:
            df_year = df_histo[df_histo["year"]==int(year)]

        M = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        by_month = df_year.groupby(["month"]).apply(count_rows)
        months = [M[x-1] for x in by_month.index.array]

        st.subheader("In "+str(year)+" you watch a total of "+str(np.sum(by_month.values))+" videos :")

        fig, ax = plt.subplots()
        ax.bar(months,by_month.values)
        plt.xlabel('Month')
        plt.ylabel('Number of video')
        plt.title('Number of video viewed each month')
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
         rotation_mode="anchor")
        st.pyplot(fig)

    # last video
    with col2:
        st.subheader("most viewed video :")
        by_url = df_year.groupby(['titleUrl']).apply(count_rows)
        url = by_url.idxmax()
        st.video(url)

    #monthly chart
    col3, col4 = st.columns([2,1])
    month = st.sidebar.selectbox("Choose a month :",months+["All"])
    df_month = df_year
    if month!="All":
        df_month = df_year[df_year["month"]==M.index(month)+1]
    by_day = df_month.groupby(["day"]).apply(count_rows)
    mean_by_day = df_year.groupby(["day"]).apply(count_rows)
    mean_by_day = mean_by_day/(len(months)+1)
    df_graph = pd.DataFrame(columns=[month,"Mean"])
    df_graph[month] = by_day
    df_graph["Mean"] = mean_by_day

    with col3:
        st.subheader(str(np.sum(by_day.values))+" videos in "+month.lower()+" :")
        fig, ax = plt.subplots()
        ax.plot(df_graph[month],label="number of video in the month")
        ax.plot(df_graph["Mean"],label="mean over the year", alpha=0.5)
        plt.grid(visible=True, color='0.95')
        x=df_graph.index.array
        plt.xlim(x[0],x[-1])
        plt.legend()
        plt.xlabel("days of the month")
        st.pyplot(fig)

    with col4:
        st.subheader("Top channels this month :")
        by_channel = df_month.groupby(["channel"]).apply(count_rows)
        by_channel = by_channel.sort_values(ascending=False)
        top5 = by_channel.iloc[:5]
        itop5 = top5.index.array
        top5 = top5.values
        for i in range(5):
            with st.expander(str(itop5[i])):
                st.write(str(top5[i])+" videos viewed in "+month+" from the channel : "+str(itop5[i]))
                st.write(df_month[df_month["channel"]==str(itop5[i])]["channel_url"].iloc[0])

    #heatmap
    st.subheader("Heatmap over the selected month :")
    count = df_month[["day","hour"]].value_counts(sort=False)
    count = count.reset_index()

    y,m = year,month
    if year=="All":
        y="2020"
    if month=="All":
        m="January"
    n = monthrange(int(y),M.index(m)+1)[1]
    data = np.zeros((24, n))
    for i in range(len(count)):
        data[count["hour"].iloc[i],count["day"].iloc[i]-1] = count[0].iloc[i]

    h_start = 0
    data = np.concatenate((data[h_start:],data[:h_start]))
    hours = np.array([0,5,10,15,20])
    new_hours = (hours+h_start)%24

    fig, ax = plt.subplots()
    im = ax.imshow(data,origin="lower",cmap="Blues")
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Number of video in 1h", rotation=-90, va="bottom")
    ax.set_yticks(hours)
    ax.set_yticklabels(new_hours)

    days = np.array([0,7,14,21,28])
    if year!="All" and month!="All":
        days = days+first_monday(int(year),M.index(month)+1)-1
    mondays = days+1
    if mondays[-1]>n:
        mondays = mondays[:-1]
        days = days[:-1]
    if year!="All" and month!="All":
        mondays = list(map(f,mondays))
    ax.set_xticks(days)
    ax.set_xticklabels(mondays)
    plt.ylabel("hours")
    plt.title("Viewing habits in "+month)
    fig.tight_layout()
    st.pyplot(fig)

    #history
    with st.expander("Investigate further more :"):
        date = st.date_input("select a day :",df_histo["time"].iloc[0].date(),min_value=df_histo["time"].iloc[-1].date(),max_value=df_histo["time"].iloc[0].date())

        df_day = df_histo[(date.year==df_histo["year"]) & (date.month==df_histo["month"]) & (date.day==df_histo["day"])]
        st.subheader(str(len(df_day))+" video this day :")
        df_day = df_day.dropna()
        nb = len(df_day)
        cols = st.columns(3)
        for i in range(nb):
            with cols[i%3]:
                j=nb-1-i
                min = df_day["time"].iloc[j].minute
                if min<10:
                    min = "0"+str(min)
                else:
                    min = str(min)
                st.write("At "+str(df_day["time"].iloc[j].hour)+"h"+min)
                st.video(df_day["titleUrl"].iloc[j])
