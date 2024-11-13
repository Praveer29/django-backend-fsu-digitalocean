

# try:
#     from nltk.corpus import stopwords
# except LookupError:
#     import nltk
#     nltk.download('stopwords')
#     from nltk.corpus import stopwords

# stopwords will be downloaded as per build.sh file
import nltk
nltk.data.path.append('./nltk_data') # relative path for nltk data, (downloaded in root directory) 

from nltk.corpus import stopwords



import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
# import nltk

from langdetect import detect

# nltk.download('stopwords')     # need to download it if not

def read_transcript(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    segments = re.split(r'\n(?=\d+:\d+ to \d+:\d+)', content)
    return [segment.strip() for segment in segments if segment.strip()]

def process_transcript(segments):
    timestamps = []
    texts = []
    
    for segment in segments:
        match = re.match(r'(\d+:\d+ to \d+:\d+) - (.*)', segment, re.DOTALL)
        if match:
            timestamps.append(match.group(1))
            texts.append(match.group(2))
    
    return timestamps, texts

def calculate_num_topics(num_samples):
    # Calculate num_topics based on num_samples
    # Ensure num_topics is always less than num_samples.
    if num_samples < 5:
        return 2
    elif num_samples < 10:
        return num_samples - 1
    else:
        return min(15, num_samples // 2)

def get_stop_words(texts):
    try:
        # Detect language from the text content
        sample_text = " ".join(texts[:3])  # Use a sample from the first few segments
        language = detect(sample_text)
        print(f"Detected language: {language}")
        stop_words = stopwords.words(language)
    except:
        # Default to English if detection fails
        stop_words = stopwords.words('english')
    return stop_words

def extract_topics(texts, num_samples, num_words=5):
    num_topics = calculate_num_topics(num_samples)
    print(f'num topics = {num_topics}')

    stop_words = get_stop_words(texts)
    
    vectorizer = TfidfVectorizer(stop_words=stop_words)
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    kmeans = KMeans(n_clusters=num_topics, random_state=42)
    kmeans.fit(tfidf_matrix)
    
    feature_names = vectorizer.get_feature_names_out()
    topics = []
    
    for cluster_center in kmeans.cluster_centers_:
        top_words_idx = cluster_center.argsort()[-num_words:][::-1]
        top_words = [(feature_names[i], cluster_center[i]) for i in top_words_idx]
        topics.append(top_words)
    
    return [topics[label] for label in kmeans.labels_]

def save_output(timestamps, topics, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for timestamp, topic in zip(timestamps, topics):
            file.write(f"{timestamp}\n")
            for word, score in topic:
                file.write(f"- {word}: {score:.4f}\n")
            file.write("\n")

def extracting_major_topics():
    input_file = r"transcript.txt"
    output_file = r"major_topics.txt"
    
    segments = read_transcript(input_file)
    timestamps, texts = process_transcript(segments)
    topics = extract_topics(texts, len(texts))
    save_output(timestamps, topics, output_file)
    
    print(f"Topics extracted and saved to {output_file}")

if __name__ == "__main__":
    extracting_major_topics()
