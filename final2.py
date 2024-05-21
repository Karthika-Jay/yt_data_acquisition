import re
import sqlite3
import googleapiclient.discovery
import streamlit as st
import pandas as pd

# Define your API key
API_KEY = "AIzaSyCPaNPL8uEpM85sifhqR5ZYDrS9YRS4kPU"
# Function to create tables in SQLite database
def create_tables():
    conn = sqlite3.connect("youtube_data.db")
    c = conn.cursor()
    
    # Create channel table
    c.execute('''CREATE TABLE IF NOT EXISTS channel (
                 channel_id VARCHAR(255) PRIMARY KEY,
                 channel_name VARCHAR(255),
                 channel_type VARCHAR(255),
                 channel_views INT,
                 channel_description TEXT,
                 channel_status VARCHAR(255)
                 )''')
    
    # Create playlist table
    c.execute('''CREATE TABLE IF NOT EXISTS playlist (
                 playlist_id VARCHAR(255),
                 channel_id VARCHAR(255),
                 playlist_name VARCHAR(255),
                 PRIMARY KEY (playlist_id, channel_id),
                 FOREIGN KEY (channel_id) REFERENCES channel(channel_id)
                 )''')
    
    # Create video table
    c.execute('''CREATE TABLE IF NOT EXISTS video (
                 video_id VARCHAR(255) PRIMARY KEY,
                 playlist_id VARCHAR(255),
                 channel_id VARCHAR(255),
                 video_name VARCHAR(255),
                 video_description TEXT,
                 published_date DATETIME,
                 view_count INT,
                 like_count INT,
                 dislike_count INT,
                 favourite_count INT,
                 comment_count INT,
                 duration INT,
                 thumbnail VARCHAR(255),
                 caption_status VARCHAR(255),
                 FOREIGN KEY (playlist_id) REFERENCES playlist(playlist_id),
                 FOREIGN KEY (channel_id) REFERENCES channel(channel_id)
                 )''')

    # Create comment table
    c.execute('''CREATE TABLE IF NOT EXISTS comment (
                 comment_id VARCHAR(255) PRIMARY KEY,
                 video_id VARCHAR(255),
                 comment_text TEXT,
                 comment_author VARCHAR(255),
                 comment_published_date DATETIME,
                 FOREIGN KEY (video_id) REFERENCES video(video_id)
                 )''')

    conn.commit()
    conn.close()

# Call function to create tables
create_tables()

# Define the Streamlit app
def main():
    st.title("YouTube Channel Analyzer")

    # Add dropdown menu to the sidebar
    page = st.sidebar.selectbox("Navigation", ["Home", "Q/A", "Tables"])
    
    if page == "Home":
        # Input field for entering YouTube channel ID or URL
        channel_id_input = st.text_input("Enter YouTube Channel ID or Channel URL:")

        # Button to retrieve channel data
        if st.button("Retrieve Channel Data"):
            if channel_id_input:
                # Extract channel ID from URL if provided
                channel_id = extract_channel_id(channel_id_input)
                if channel_id:
                    # Call function to retrieve channel data
                    channel_data = retrieve_channel_data(channel_id)
                    if channel_data:
                        # Display channel data
                        st.write("Channel Name:", channel_data["Channel_Name"])
                        st.write("Subscribers:", channel_data["Subscription_Count"])
                        st.write("Total Video Count:", channel_data["Total_Video_Count"])
                        st.write("Playlist ID:", channel_data["Playlist_Id"])
                        st.write("Latest Videos:")
                        for video_id, video_info in channel_data["Latest_Videos"].items():
                            st.write("Video ID:", video_id)
                            st.write("Video Name:", video_info["Video_Name"])
                            st.write("Published At:", video_info["PublishedAt"])
                            st.write("View Count:", video_info["View_Count"])
                            st.write("Like Count:", video_info["Like_Count"])
                            st.write("Dislike Count:", video_info["Dislike_Count"])
                            st.write("Comment Count:", video_info["Comment_Count"])
                            st.write("---")
                        # Store channel data in database
                        store_channel_data(channel_data)
                    else:
                        st.error("Error: Unable to retrieve channel data. Please try again later.")
                else:
                    st.error("Error: Invalid YouTube channel ID or URL.")
            else:
                st.warning("Please enter a YouTube channel ID.")

    elif page == "Q/A":
        st.header("Answers to Questions")
    
        # Define the questions
        questions = [
            "1. What are the names of all the videos and their corresponding channels?",
            "2. Which channels have the most number of videos, and how many videos do they have?",
            "3. What are the top 10 most viewed videos and their respective channels?",
            "4. How many comments were made on each video, and what are their corresponding video names?",
            "5. Which videos have the highest number of likes, and what are their corresponding channel names?",
            "6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
            "7. What is the total number of views for each channel, and what are their corresponding channel names?",
            "8. What are the names of all the channels that have published videos in the year 2022?",
            "9. What is the average duration of all videos in each channel, and what are their corresponding channel names?",
            "10. Which videos have the highest number of comments, and what are their corresponding channel names?",
            "11. Display comments for a selected video"
        ]

        # Add a dropdown to select a question
        selected_question = st.selectbox("Select a question", questions)
        
        # Establish database connection
        conn = sqlite3.connect("youtube_data.db")
        c = conn.cursor()

        # Display the result based on the selected question
        if selected_question == questions[0]:
            st.subheader(questions[0])
            c.execute('''SELECT video_name, channel_name FROM video 
                         INNER JOIN channel ON video.channel_id = channel.channel_id''')
            q1_result = c.fetchall()
            st.table(q1_result)

        elif selected_question == questions[1]:
            st.subheader(questions[1])
            c.execute('''SELECT channel_name, COUNT(video_id) AS num_videos FROM video 
                         INNER JOIN channel ON video.channel_id = channel.channel_id
                         GROUP BY video.channel_id 
                         ORDER BY num_videos DESC''')
            q2_result = c.fetchall()
            st.table(q2_result)

        elif selected_question == questions[2]:
            st.subheader(questions[2])
            c.execute('''SELECT video_name, channel_name, view_count FROM video 
                         INNER JOIN channel ON video.channel_id = channel.channel_id
                         ORDER BY view_count DESC 
                         LIMIT 10''')
            q3_result = c.fetchall()
            st.table(q3_result)

        elif selected_question == questions[3]:
            st.subheader(questions[3])
            c.execute('''SELECT video_name, COUNT(comment_id) AS num_comments FROM video 
                         INNER JOIN comment ON video.video_id = comment.video_id
                         GROUP BY video.video_id''')
            q4_result = c.fetchall()
            st.table(q4_result)

        elif selected_question == questions[4]:
            st.subheader(questions[4])
            c.execute('''SELECT video_name, channel_name, like_count FROM video 
                         INNER JOIN channel ON video.channel_id = channel.channel_id
                         ORDER BY like_count DESC''')
            q5_result = c.fetchall()
            st.table(q5_result)

        elif selected_question == questions[5]:
            st.subheader(questions[5])
            c.execute('''SELECT video_name, (like_count + dislike_count) AS total_reactions FROM video 
                         ORDER BY total_reactions DESC''')
            q6_result = c.fetchall()
            st.table(q6_result)

        elif selected_question == questions[6]:
            st.subheader(questions[6])
            c.execute('''SELECT channel_name, SUM(view_count) AS total_views FROM video 
                         INNER JOIN channel ON video.channel_id = channel.channel_id
                         GROUP BY video.channel_id 
                         ORDER BY total_views DESC''')
            q7_result = c.fetchall()
            st.table(q7_result)

        elif selected_question == questions[7]:
            st.subheader(questions[7])
            c.execute('''SELECT channel_name FROM video 
                         INNER JOIN channel ON video.channel_id = channel.channel_id
                         WHERE published_date LIKE '2022%' ''')
            q8_result = c.fetchall()
            st.table(q8_result)

        elif selected_question == questions[8]:
            st.subheader(questions[8])
            c.execute('''SELECT channel_name, AVG(duration) AS avg_duration FROM video 
                         INNER JOIN channel ON video.channel_id = channel.channel_id
                         GROUP BY video.channel_id''')
            q9_result = c.fetchall()
            st.table(q9_result)

        elif selected_question == questions[9]:
            st.subheader(questions[9])
            # try:
            c.execute('''SELECT channel_name, AVG(duration) AS avg_duration FROM video 
                 INNER JOIN channel ON video.channel_id = channel.channel_id
                 GROUP BY video.channel_id''')
            q9_result = c.fetchall()
            st.table(q9_result)
            # except Exception as e:
            #     st.error(f"An error occurred: {str(e)}")
            


        elif selected_question == questions[10]:
                st.subheader(questions[10])
            # Add a dropdown to select a video for comments
                c.execute('SELECT video_name, video_id FROM video')
                videos = c.fetchall()
                video_options = {name: vid for name, vid in videos} #where name represents the video name column and vid represents the video ID column.
                selected_video_name = st.selectbox("Select a video", list(video_options.keys()))
                selected_video_id = video_options[selected_video_name]
            
            # Fetch and display comments for the selected video
                c.execute('SELECT comment_text, comment_author, comment_published_date FROM comment WHERE video_id = ?', (selected_video_id,))
                comments = c.fetchall()
                st.table(comments)

                conn.close()
    
    elif page == "Tables":
        st.header("Database Tables")
        conn = sqlite3.connect("youtube_data.db")
        c = conn.cursor()

        # Retrieve all table names
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()
        
        # Display each table with its data
        for table_name in tables:
            st.subheader(f"Table: {table_name[0]}")
            c.execute(f"PRAGMA table_info({table_name[0]})")
            columns = c.fetchall()
            col_names = [col[1] for col in columns]
            c.execute(f"SELECT * FROM {table_name[0]}")
            rows = c.fetchall()
            df = pd.DataFrame(rows, columns=col_names)
            st.table(df)
        
        conn.close()

# Function to extract channel ID from URL or input
def extract_channel_id(input_text):
    # Regular expressions for different YouTube channel URL formats
    channel_id_match = re.match(r'^[A-Za-z0-9_-]{24}$', input_text)
    if channel_id_match:
        return input_text
    channel_url_match = re.match(r'^https?://(?:www\.)?youtube\.com/(?:channel/|user/|c/)?([A-Za-z0-9_-]{24})', input_text)
    if channel_url_match:
        return channel_url_match.group(1)
    return None

def retrieve_channel_data(channel_id):
    try:
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)

        # Retrieve channel data
        channel_response = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=channel_id
        ).execute()

        if "items" not in channel_response or not channel_response["items"]:
            st.error("Error: Invalid channel ID or channel not found.")
            return None

        # Retrieve playlist data
        playlist_response = youtube.channels().list(
            part="contentDetails",
            id=channel_id
        ).execute()

        if "items" not in playlist_response or not playlist_response["items"]:
            st.error("Error: Unable to retrieve playlist data for this channel.")
            return None

        # Retrieve latest videos from the playlist
        playlist_id = playlist_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        playlist_items = []
        next_page_token = None

        while True:
            # Fetch a page of playlist items
            request = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,  # Maximum number of results per page
                pageToken=next_page_token
            )
            response = request.execute()

            # Append fetched items to the list
            playlist_items.extend(response.get("items", []))

            # Check if there are more pages available
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break  # No more pages, exit the loop

        # Extract relevant data
        channel_name = channel_response["items"][0]["snippet"]["title"]
        subscription_count = channel_response["items"][0]["statistics"].get("subscriberCount", "N/A")
        total_video_count = channel_response["items"][0]["statistics"].get("videoCount")
        latest_videos = {}
        for item in playlist_items:
            video_id = item["snippet"]["resourceId"]["videoId"]
            video_name = item["snippet"]["title"]
            published_at = item["snippet"]["publishedAt"]

            # Retrieve video statistics
            video_response = youtube.videos().list(
                part="statistics",
                id=video_id
            ).execute()

            # Extract view count, like count, dislike count, and comment count with error handling
            view_count = video_response["items"][0]["statistics"].get("viewCount", 0)
            like_count = video_response["items"][0]["statistics"].get("likeCount", 0)
            dislike_count = video_response["items"][0]["statistics"].get("dislikeCount", 0)
            comment_count = video_response["items"][0]["statistics"].get("commentCount", 0)

            # Retrieve comments for the video
            comments = []
            try:
                comments_response = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100  # Adjust this value to retrieve more or fewer comments
                ).execute()

                for comment_item in comments_response.get("items", []):
                    comment = comment_item["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "Comment_Id": comment_item["id"],
                        "Video_Id": video_id,
                        "Comment_Text": comment["textDisplay"],
                        "Comment_Author": comment["authorDisplayName"],
                        "Comment_Published_Date": comment["publishedAt"]
                    })
            except googleapiclient.errors.HttpError as e:
                # Skip videos with disabled comments
                if e.resp.status == 403:
                    st.warning(f"Comments are disabled for the video: {video_id}")
                    continue  # Skip to the next video
                else:
                    raise e  # Re-raise other HttpError exceptions

            latest_videos[video_id] = {
                "Video_Name": video_name,
                "PublishedAt": published_at,
                "View_Count": view_count,
                "Like_Count": like_count,
                "Dislike_Count": dislike_count,
                "Comment_Count": comment_count,
                "Comments": comments  # Include comments in the dictionary
            }

        # Construct the channel data dictionary
        channel_data = {
            "Channel_Id": channel_id,
            "Channel_Name": channel_name,
            "Subscription_Count": subscription_count,  # Include subscription count
            "Total_Video_Count": total_video_count,
            "Playlist_Id": playlist_id,
            "Latest_Videos": latest_videos
        }

        return channel_data

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Function to store channel data in the database
def store_channel_data(channel_data):
    conn = sqlite3.connect("youtube_data.db")
    c = conn.cursor()

    # Insert channel data into the channel table
    c.execute('''INSERT OR REPLACE INTO channel 
                 (channel_id, channel_name, channel_type, channel_views, channel_description, channel_status) 
                 VALUES (?, ?, ?, ?, ?, ?)''',
                 (channel_data["Channel_Id"], channel_data["Channel_Name"], "Type_placeholder", 
                 channel_data["Subscription_Count"], "Description_placeholder", "Status_placeholder"))

    # Insert playlist data into the playlist table
    c.execute('''INSERT OR REPLACE INTO playlist 
                 (playlist_id, channel_id, playlist_name) 
                 VALUES (?, ?, ?)''',
                 (channel_data["Playlist_Id"], channel_data["Channel_Id"], "Playlist_name_placeholder"))

    # Insert video data into the video table
    for video_id, video_info in channel_data["Latest_Videos"].items():
        c.execute('''INSERT OR REPLACE INTO video 
                     (video_id, playlist_id, channel_id, video_name, video_description, published_date, view_count, 
                     like_count, dislike_count, favourite_count, comment_count, duration, thumbnail, caption_status) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (video_id, channel_data["Playlist_Id"], channel_data["Channel_Id"], video_info["Video_Name"], "Description_placeholder", 
                     video_info["PublishedAt"], video_info["View_Count"], video_info["Like_Count"], 
                     video_info["Dislike_Count"], 0, video_info["Comment_Count"], 0, "Thumbnail_placeholder", 
                     "Caption_status_placeholder"))

        # Insert comment data into the comment table
        for comment in video_info["Comments"]:
            c.execute('''INSERT OR REPLACE INTO comment 
                         (comment_id, video_id, comment_text, comment_author, comment_published_date) 
                         VALUES (?, ?, ?, ?, ?)''',
                         (comment["Comment_Id"], comment["Video_Id"], comment["Comment_Text"], 
                         comment["Comment_Author"], comment["Comment_Published_Date"]))

    conn.commit()
    conn.close()

# Run the Streamlit app
if __name__ == "__main__":
    main()