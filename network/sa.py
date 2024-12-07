from django.shortcuts import render
import pandas as pd
import numpy as np
from django.utils import timezone
from network.models import *
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
    users_interests = []
    for user in User.objects.all():
        interests = set()
        for post in user.posts.all():
            if post.content_text:
                 interests.add(f"Post: {post.content_text} ({post.date_created.strftime('%Y-%m-%d %H:%M:%S')})")
        for like in user.postlikes.all():
            if like.post.content_text:
                interests.add(f"Like: {like.post.content_text} ({like.date_likes.strftime('%Y-%m-%d %H:%M:%S')})")
        for save in user.postsaves.all():
            if save.post.content_text:
                interests.add(f"Save: {save.post.content_text} ({save.date_saved.strftime('%Y-%m-%d %H:%M:%S')})")
        users_interests.append({
            'user': user,
            'interests': ', '.join(interests)
         })
    users = User.objects.all()  
    num_users = User.objects.count()
    num_posts = Post.objects.count()
    num_like = Postlike.objects.count()
    num_save = Save.objects.count()
    context = {
            'users_interests': users_interests,
            'users': users,
            'num_users': num_users,
            'num_posts': num_posts,
            'num_like': num_like,
            'num_save': num_save
    }
    return render(request, 'admin/enrich.html', context)


def interests_by_user(request):
    interests = Interest.objects.all()
    context = {'interests': interests}
    return render(request, 'admin/custom_interests.html', context)




    # Get all posts from the database
    posts = Post.objects.all()

    # Create an empty list to store the data
    data = []

    # Loop through all posts and extract the data
    for post in posts:
        # Get the username of the enrich_user
        username = post.enrich_user.all().values_list('username', flat=True).first()

        # Get the content_text and date_created of the post
        content_text = post.content_text
        date_created = post.date_created

        # Append the data to the list
        data.append([username, content_text, date_created])

    # Create a pandas dataframe from the list of data
    df = pd.DataFrame(data, columns=['username', 'content_text', 'date'])

    # data preprocessing
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

    # Calculate the number of interactions for each subreddit in the past week
    df['most_recent_interaction'] = pd.to_datetime(df['most_recent_interaction'])
    df['date'] = pd.to_datetime(df['date'])
    df['week_before_most_recent'] = df['most_recent_interaction'] - pd.Timedelta(days=30)

    week_interactions = df[(df['date'] >= df['week_before_most_recent']) & (df['date'] <= df['most_recent_interaction'])] \
                        .groupby(['username', 'subreddit']) \
                        .agg({'date': 'count'}) \
                        .reset_index() \
                        .rename(columns={'date': 'num_interactions_week'})

    # Merge the new column with the main dataframe
    df = pd.merge(df, week_interactions, on=['username', 'subreddit'], how='left')
    df['num_interactions_week'].fillna(0, inplace=True)

    # Calculate the average interaction count in the past week for each user
    avg_interactions = df[(df['date'] >= df['week_before_most_recent']) & (df['date'] <= df['most_recent_interaction'])] \
                        .groupby(['username'])['num_interactions_week'] \
                        .mean() \
                        .reset_index() \
                        .rename(columns={'num_interactions_week': 'avrg'})

    # Merge the average interaction count with the main dataframe
    df = pd.merge(df, avg_interactions, on=['username'], how='left')

    # Calculate the binary value based on whether the number of interactions is greater than the average interaction count and whether the interaction is recent
    df['binary_value'] = np.where((df['recency'] == 'recent') & (df['num_interactions'] > df['avrg']), 1, 0)

    df.drop(['num_interactions_week', 'most_recent_interaction','time_diff','date','most_recent','avrg','binary_value'], axis=1, inplace=True)
    df = df.dropna()
