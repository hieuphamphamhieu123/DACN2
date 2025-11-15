"""
Script to populate Firebase Firestore with test data
"""
import sys
import os
import io

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(__file__))

from datetime import datetime, timedelta
import random
import firebase_admin
from firebase_admin import credentials, firestore
from app.utils.security import get_password_hash

# Sample test data
USERS = [
    {
        "username": "techguy",
        "email": "techguy@test.com",
        "password": "test123",
        "full_name": "Tech Enthusiast",
        "bio": "I love technology and AI",
        "preferences": {
            "favorite_tags": ["tech", "ai", "machinelearning", "python", "webdev"],
            "interests": ["technology", "programming", "artificial intelligence"]
        }
    },
    {
        "username": "foodlover",
        "email": "foodlover@test.com",
        "password": "test123",
        "full_name": "Food Lover",
        "bio": "Passionate about cooking and trying new restaurants",
        "preferences": {
            "favorite_tags": ["food", "cooking", "restaurant", "baking"],
            "interests": ["food", "cooking", "dining", "recipes"]
        }
    },
    {
        "username": "traveler",
        "email": "traveler@test.com",
        "password": "test123",
        "full_name": "World Traveler",
        "bio": "Exploring the world one country at a time",
        "preferences": {
            "favorite_tags": ["travel", "adventure", "vacation", "culture"],
            "interests": ["travel", "adventure", "culture", "photography"]
        }
    },
    {
        "username": "athlete",
        "email": "athlete@test.com",
        "password": "test123",
        "full_name": "Fitness Enthusiast",
        "bio": "Health is wealth! Gym, yoga, running",
        "preferences": {
            "favorite_tags": ["sports", "fitness", "health", "running", "yoga"],
            "interests": ["sports", "fitness", "health", "wellness"]
        }
    },
]

POSTS = [
    # Tech posts
    {
        "content": "Just finished building a machine learning model for image classification using PyTorch and transformers. The results are amazing! Accuracy reached 95% on the test set. Anyone interested in discussing neural network architectures?",
        "tags": ["tech", "ai", "machinelearning", "python", "pytorch"],
        "categories": ["technology", "programming"],
        "user_index": 0
    },
    {
        "content": "New React 18 features are game-changing! Concurrent rendering makes everything so smooth. The automatic batching and startTransition API are incredible. Love building modern web apps!",
        "tags": ["tech", "react", "javascript", "webdev", "frontend"],
        "categories": ["technology", "programming"],
        "user_index": 0
    },
    {
        "content": "Started learning Docker and Kubernetes today. Container orchestration is fascinating! Setting up microservices architecture. Any tips for beginners in DevOps?",
        "tags": ["tech", "docker", "kubernetes", "devops", "cloud"],
        "categories": ["technology", "cloud"],
        "user_index": 0
    },
    {
        "content": "Built a REST API with FastAPI and it's so fast! Python backend development has never been easier. The automatic documentation with Swagger is a huge plus!",
        "tags": ["tech", "python", "fastapi", "backend", "api"],
        "categories": ["technology", "programming"],
        "user_index": 0
    },
    {
        "content": "Exploring GraphQL vs REST API. GraphQL's flexibility is impressive but REST is simpler for small projects. What do you prefer for your backend?",
        "tags": ["tech", "graphql", "rest", "api", "backend"],
        "categories": ["technology", "programming"],
        "user_index": 0
    },

    # Food posts
    {
        "content": "Made the best pho bo today! The secret is simmering the beef bones for 24 hours. The broth is incredibly rich and flavorful. Added fresh herbs, bean sprouts, and lime. Perfect comfort food!",
        "tags": ["food", "vietnamese", "cooking", "pho", "homemade"],
        "categories": ["food", "cooking"],
        "user_index": 1
    },
    {
        "content": "Just tried this amazing sushi restaurant in downtown. The omakase menu was incredible! Fresh tuna melts in your mouth. The chef's selection was perfect. Highly recommend!",
        "tags": ["food", "sushi", "japanese", "restaurant", "omakase"],
        "categories": ["food", "dining"],
        "user_index": 1
    },
    {
        "content": "Baked homemade sourdough bread for the first time. The crust is perfectly crispy, inside is soft and airy. The fermentation process took 3 days but so worth it! Proud baker moment!",
        "tags": ["food", "baking", "bread", "homemade", "sourdough"],
        "categories": ["food", "cooking"],
        "user_index": 1
    },
    {
        "content": "Tried making Thai green curry from scratch. The paste with lemongrass, galangal, and kaffir lime is so aromatic! Paired with jasmine rice. Delicious!",
        "tags": ["food", "thai", "cooking", "curry", "asian"],
        "categories": ["food", "cooking"],
        "user_index": 1
    },
    {
        "content": "Coffee tasting session today. Compared Ethiopian vs Colombian beans. The fruity notes in Ethiopian coffee are amazing! What's your favorite coffee origin?",
        "tags": ["food", "coffee", "tasting", "beans", "brew"],
        "categories": ["food", "beverages"],
        "user_index": 1
    },

    # Travel posts
    {
        "content": "Visited Da Lat this weekend. The weather was perfect, flowers blooming everywhere! The coffee plantations tour was educational. Don't miss the Crazy House and waterfalls!",
        "tags": ["travel", "vietnam", "dalat", "vacation", "nature"],
        "categories": ["travel", "adventure"],
        "user_index": 2
    },
    {
        "content": "Backpacking through Southeast Asia. Thailand is amazing! The beaches in Krabi are paradise - crystal clear water and limestone cliffs. Next stop: Cambodia temples!",
        "tags": ["travel", "thailand", "backpacking", "beach", "adventure"],
        "categories": ["travel", "adventure"],
        "user_index": 2
    },
    {
        "content": "Solo travel to Japan was life-changing. Tokyo is so modern yet traditional. Kyoto temples are breathtaking! The bullet train experience was incredible. Will definitely return!",
        "tags": ["travel", "japan", "solo", "culture", "temples"],
        "categories": ["travel", "culture"],
        "user_index": 2
    },
    {
        "content": "Explored the ancient town of Hoi An. The lanterns at night create magical atmosphere! Tailors here make custom clothes in 24 hours. Rich history and great food!",
        "tags": ["travel", "vietnam", "hoian", "culture", "history"],
        "categories": ["travel", "culture"],
        "user_index": 2
    },
    {
        "content": "Trekking in Sapa rice terraces. The landscape is stunning! Met local H'mong people, learned about their culture. Sunrise view from Fansipan peak was unforgettable!",
        "tags": ["travel", "vietnam", "sapa", "trekking", "nature"],
        "categories": ["travel", "adventure"],
        "user_index": 2
    },

    # Sports posts
    {
        "content": "Ran my first 10K race today! Finished in 52 minutes. The training for the past 3 months paid off. Feeling accomplished and already planning for half marathon!",
        "tags": ["sports", "running", "fitness", "health", "marathon"],
        "categories": ["sports", "fitness"],
        "user_index": 3
    },
    {
        "content": "Amazing football match! Manchester United vs Liverpool was intense. That last minute goal was incredible! Premier League never disappoints. Best league in the world!",
        "tags": ["sports", "football", "soccer", "premierleague", "manutd"],
        "categories": ["sports", "entertainment"],
        "user_index": 3
    },
    {
        "content": "Started doing yoga every morning. My flexibility improved so much in just 2 weeks. Highly recommend for stress relief and mental clarity. Namaste!",
        "tags": ["sports", "yoga", "fitness", "wellness", "health"],
        "categories": ["sports", "health"],
        "user_index": 3
    },
    {
        "content": "Hit new personal record at the gym today! Deadlift 150kg. Strength training journey is paying off. Proper form and progressive overload are key!",
        "tags": ["sports", "gym", "fitness", "strength", "workout"],
        "categories": ["sports", "fitness"],
        "user_index": 3
    },
    {
        "content": "Completed my first triathlon! Swimming, cycling, and running. It was tough but crossing that finish line felt amazing. Already signed up for the next one!",
        "tags": ["sports", "triathlon", "fitness", "swimming", "cycling"],
        "categories": ["sports", "fitness"],
        "user_index": 3
    },

    # Photography posts
    {
        "content": "Captured the sunrise at the beach today. Golden hour lighting is magical! Shot with Sony A7III, 24-70mm lens at f/8. The colors were breathtaking!",
        "tags": ["photography", "landscape", "sunrise", "nature", "sony"],
        "categories": ["photography", "art"],
        "user_index": 2
    },
    {
        "content": "Street photography in Hanoi Old Quarter. The energy, the people, the colors - so vibrant! Candid shots tell amazing stories. Love this city's character!",
        "tags": ["photography", "street", "hanoi", "vietnam", "urban"],
        "categories": ["photography", "culture"],
        "user_index": 2
    },

    # Music posts
    {
        "content": "Learning to play guitar. Just mastered my first song - Hotel California! Fingers hurt but so worth it. The chord progressions are beautiful!",
        "tags": ["music", "guitar", "learning", "hobby", "practice"],
        "categories": ["music", "entertainment"],
        "user_index": 0
    },
    {
        "content": "Went to an amazing jazz concert last night. The saxophone solo gave me chills. Live music hits different! The energy in the venue was electric!",
        "tags": ["music", "jazz", "concert", "live", "saxophone"],
        "categories": ["music", "entertainment"],
        "user_index": 1
    },
]

def create_users(db):
    """Create test users in Firestore"""
    print("\n1. Creating users...")
    users_ref = db.collection('users')
    created_users = []

    for user_data in USERS:
        # Check if user exists
        existing = users_ref.where('username', '==', user_data['username']).limit(1).get()

        if existing:
            print(f"   → User already exists: {user_data['username']}")
            user_doc = existing[0]
            user_id = user_doc.id
        else:
            # Create new user
            user_dict = {
                "username": user_data["username"],
                "email": user_data["email"],
                "password_hash": get_password_hash(user_data["password"]),
                "full_name": user_data["full_name"],
                "bio": user_data.get("bio"),
                "avatar_url": None,
                "preferences": user_data.get("preferences", {"favorite_tags": [], "interests": []})
            }

            timestamp, doc_ref = users_ref.add(user_dict)
            user_id = doc_ref.id
            print(f"   ✓ Created user: {user_data['username']} (ID: {user_id})")

        created_users.append({
            "id": user_id,
            "username": user_data["username"]
        })

    return created_users

def create_posts(db, users):
    """Create test posts in Firestore"""
    print(f"\n2. Creating {len(POSTS)} sample posts...")
    posts_ref = db.collection('posts')
    created_posts = []

    for i, post_data in enumerate(POSTS):
        user = users[post_data["user_index"]]

        # Create post with timestamp variation (posts from last 7 days)
        days_ago = random.randint(0, 7)
        created_at = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))

        post_dict = {
            "user_id": user["id"],
            "content": post_data["content"],
            "image_url": None,
            "tags": post_data["tags"],
            "categories": post_data["categories"],
            "moderation_result": {
                "toxicity": 0.01,
                "severe_toxicity": 0.001,
                "obscene": 0.002,
                "threat": 0.001,
                "insult": 0.002,
                "identity_hate": 0.001,
                "passed": True
            },
            "image_moderation_passed": True,
            "is_approved": True,
            "likes_count": 0,
            "comments_count": 0,
            "created_at": created_at,
            "updated_at": created_at
        }

        timestamp, doc_ref = posts_ref.add(post_dict)
        post_id = doc_ref.id
        created_posts.append({"id": post_id, "user_id": user["id"]})

        tags_str = ", ".join(post_data["tags"][:3])
        print(f"   ✓ Post {i+1} by {user['username']}: [{tags_str}]")

    return created_posts

def add_likes(db, posts, users):
    """Add random likes to posts"""
    print(f"\n3. Adding likes to posts...")
    likes_ref = db.collection('likes')
    posts_ref = db.collection('posts')

    like_count = 0

    # Each post gets 0-5 random likes
    for post in posts:
        num_likes = random.randint(0, 5)

        # Randomly select users to like this post
        liking_users = random.sample(users, min(num_likes, len(users)))

        for user in liking_users:
            # Don't let user like their own post
            if user["id"] == post["user_id"]:
                continue

            like_dict = {
                "user_id": user["id"],
                "post_id": post["id"],
                "created_at": datetime.utcnow()
            }

            likes_ref.add(like_dict)
            like_count += 1

        # Update post likes_count
        if num_likes > 0:
            posts_ref.document(post["id"]).update({"likes_count": num_likes})

    print(f"   ✓ Added {like_count} likes")

def add_comments(db, posts, users):
    """Add random comments to posts"""
    print(f"\n4. Adding comments to posts...")
    comments_ref = db.collection('comments')
    posts_ref = db.collection('posts')

    sample_comments = [
        "Great post! Thanks for sharing!",
        "This is really interesting!",
        "Love this! Keep it up!",
        "Amazing content!",
        "Very informative, thank you!",
        "I totally agree with this!",
        "This is so cool!",
        "Can't wait to try this!",
        "Awesome work!",
        "This made my day!",
    ]

    comment_count = 0

    # Add 0-3 comments to each post
    for post in posts:
        num_comments = random.randint(0, 3)

        for _ in range(num_comments):
            user = random.choice(users)

            comment_dict = {
                "post_id": post["id"],
                "user_id": user["id"],
                "content": random.choice(sample_comments),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            comments_ref.add(comment_dict)
            comment_count += 1

        # Update post comments_count
        if num_comments > 0:
            posts_ref.document(post["id"]).update({"comments_count": num_comments})

    print(f"   ✓ Added {comment_count} comments")

def initialize_firebase():
    """Initialize Firebase connection"""
    try:
        # Path to Firebase credentials file
        cred_path = os.path.join(os.path.dirname(__file__), "firebase-credentials.json")

        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Firebase credentials file not found at: {cred_path}")

        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        # Get Firestore client
        db = firestore.client()
        print("[SUCCESS] Connected to Firebase Firestore")
        return db

    except Exception as e:
        print(f"[ERROR] Failed to connect to Firestore: {e}")
        raise

def main():
    print("=" * 60)
    print("POPULATING FIREBASE FIRESTORE WITH TEST DATA")
    print("=" * 60)

    # Initialize Firebase and get database connection
    db = initialize_firebase()

    # Create data
    users = create_users(db)
    posts = create_posts(db, users)
    add_likes(db, posts, users)
    add_comments(db, posts, users)

    print("\n" + "=" * 60)
    print("TEST DATA CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"✓ Users: {len(users)}")
    print(f"✓ Posts: {len(posts)}")
    print(f"✓ Categories: technology, food, travel, sports, photography, music")
    print(f"✓ Tags: {len(set([tag for post in POSTS for tag in post['tags']]))} unique tags")
    print("\nTest users (password: test123):")
    for user in users:
        print(f"   - {user['username']}")
    print("\nYou can now:")
    print("1. Login with any test user")
    print("2. Click 'For You' to see AI-powered recommendations")
    print("3. Each user has different preferences for personalized feed")
    print("=" * 60)

if __name__ == "__main__":
    main()
