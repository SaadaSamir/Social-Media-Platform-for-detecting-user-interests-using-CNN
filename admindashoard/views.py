from django.shortcuts import render
import pandas as pd
import numpy as np
from keras.models import load_model
from django.utils import timezone
from network.models import *
from .models import *
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split




# Create your views here.

def site_admindash(request):
    users = User.objects.all().order_by('-date_joined')
    num_users = User.objects.count()
    num_posts = Post.objects.count()
    num_like = Postlike.objects.count()
    num_save = Save.objects.count()
    context = {
            'users': users,
            'num_users': num_users,
            'num_posts': num_posts,
            'num_like': num_like,
            'num_save': num_save
        }
    return render(request, 'admin/user_interests.html', context)

from collections import defaultdict


def enrich(request):
    if request.method == 'POST':
        enrich_date = Enrich_date.objects.create(date=timezone.now())
        enrich_date.save()
        Interest_neuron.objects.all().delete()
        users = User.objects.all()
        le = LabelEncoder()
        scaler = StandardScaler()
        model = load_model("model.h5")
        predict_function = model.predict
        results = []
        for user in users:
            user_posts = Post.objects.filter(enrich_user=user).order_by('-date_created')
            if not user_posts.exists():
                continue
            df = preprocess_data(user_posts)
            df_original = df.copy()
            print(df)
            df['username'] = le.fit_transform(df['username'])
            df['subreddit'] = le.fit_transform(df['subreddit'])
            cols_to_scale = ['username','subreddit', 'num_interactions', 'avrg']
            scaler.fit(df[cols_to_scale])
            df[cols_to_scale] = scaler.transform(df[cols_to_scale])
            X = df[['username','subreddit', 'num_interactions', 'avrg']].to_numpy()
            X = X.reshape((X.shape[0], X.shape[1], 1))
            predictions = predict_function(X)
            for i in range(len(predictions)):
                if predictions[i] > 0.5:
                    obj = Interest_neuron(username=df_original.iloc[i]['username'], content=df_original.iloc[i]['subreddit'])
                    obj.save()
                    username = df_original.iloc[i]['username']
                    print("username",df_original.iloc[i]['username'])
                    print("subreddit",df_original.iloc[i]['subreddit'])
                    if username not in [result['username'] for result in results]:  # Only process new usernames
                        interest = [df_original.iloc[i]['subreddit']]  # Store interest as list
                        activity = []
                        for sub, count in df_original.loc[df_original['username'] == username, ['subreddit', 'num_interactions']].values:
                            activity.append(f"{sub} ({int(count)})")
                        results.append({'username': username, 'interest': interest, 'activity': activity})
                    else:
                        interest = df_original.iloc[i]['subreddit']
                        for result in results:
                            if result['username'] == username:
                                result['interest'].append(interest)

        return render(request, 'admin/enrich.html', {'results': results,'users':users})
    else:
        return render(request, 'admin/enrich.html')



def interests_by_user(request):
    interests = Interest.objects.all().order_by('user__username')
    context = {'interests': interests}
    return render(request, 'admin/custom_interests.html', context)



def preprocess_data(posts):
    data = []
    for post in posts:
        username = post.enrich_user.all().values_list('username', flat=True).first()
        content_text = post.content_text
        date_created = post.date_created
        data.append([username, content_text, date_created])

    df = pd.DataFrame(data, columns=['username', 'content_text', 'date'])
    df['date']=pd.to_datetime(df['date'])
    
    subreddit_counts = df.groupby(['username', 'content_text']).agg({'date': ['count', 'max']})
    subreddit_counts.columns = ['num_interactions', 'most_recent']
    subreddit_counts = subreddit_counts.reset_index()
    user_most_recent = df.groupby('username').agg({'date': 'max'})
    user_most_recent.columns = ['most_recent_interaction']
    user_most_recent = user_most_recent.reset_index()
    df = df.merge(subreddit_counts, on=['username', 'content_text'], how='left')
    df = df.merge(user_most_recent, on='username', how='left')

    df['most_recent_interaction'] = pd.to_datetime(df['most_recent_interaction'])
    df['most_recent'] = pd.to_datetime(df['most_recent'])
    df['time_diff'] = df['most_recent_interaction'] - df['most_recent']
    df['recency'] = df['time_diff'].apply(lambda x: 'recent' if x.days <= 30 else 'older')
    df['most_recent_interaction'] = pd.to_datetime(df['most_recent_interaction'])
    df['date'] = pd.to_datetime(df['date'])

    df['week_before_most_recent'] = df['most_recent_interaction'] - pd.Timedelta(days=30)
    week_interactions = df[(df['date'] >= df['week_before_most_recent']) & (df['date'] <= df['most_recent_interaction'])] \
                        .groupby(['username', 'content_text']) \
                        .agg({'date': 'count'}) \
                        .reset_index() \
                        .rename(columns={'date': 'num_interactions_week'})
    df = pd.merge(df, week_interactions, on=['username', 'content_text'], how='left')
    df['num_interactions_week'].fillna(0, inplace=True)

    df = df.sort_values('date', ascending=False).drop_duplicates(subset=['username', 'content_text'])
    
    avg_interactions = df[(df['date'] >= df['week_before_most_recent']) & (df['date'] <= df['most_recent_interaction'])] \
                        .groupby(['username'])['num_interactions_week'] \
                        .mean() \
                        .reset_index() \
                        .rename(columns={'num_interactions_week': 'avrg'})

    df = pd.merge(df, avg_interactions, on=['username'], how='left')
    df['binary_value'] = np.where((df['recency'] == 'recent') & (df['num_interactions'] > df['avrg']), 1, 0)   
    df = df.sort_values(['username', 'date'], ascending=[True, False]).drop_duplicates(subset=['username', 'content_text'])
    df = df.set_index('username').loc[df['username'].unique()].reset_index()
    df = df.rename(columns={'content_text': 'subreddit'})
    df.drop([ 'most_recent_interaction','time_diff','date','most_recent','week_before_most_recent','recency','binary_value'], axis=1, inplace=True)
    df = df.dropna()

    return df
