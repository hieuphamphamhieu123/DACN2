"""
Script to add more diverse posts to Firebase Firestore for testing recommendation system
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

# Expanded test data with diverse topics
ADDITIONAL_POSTS = [
    # Tech & Programming (20 posts)
    {"content": "Just learned about GraphQL and it's amazing! The flexibility compared to REST is incredible. #graphql #api", "tags": ["graphql", "api", "webdev"], "categories": ["technology", "programming"]},
    {"content": "TypeScript has completely changed how I write JavaScript. Type safety is a game changer! #typescript #javascript", "tags": ["typescript", "javascript", "webdev"], "categories": ["technology", "programming"]},
    {"content": "Docker containers make deployment so much easier. No more 'works on my machine' problems! #docker #devops", "tags": ["docker", "devops", "containers"], "categories": ["technology", "devops"]},
    {"content": "Exploring Rust for the first time. The ownership model is mind-bending but powerful! #rust #programming", "tags": ["rust", "programming", "systems"], "categories": ["technology", "programming"]},
    {"content": "CI/CD pipelines with GitHub Actions have streamlined our development workflow tremendously #cicd #github", "tags": ["cicd", "github", "devops"], "categories": ["technology", "devops"]},
    {"content": "Vue 3 Composition API is so elegant! Building reactive UIs has never been this clean #vue #frontend", "tags": ["vue", "frontend", "javascript"], "categories": ["technology", "programming"]},
    {"content": "Kubernetes orchestration at scale - learning the hard way but it's worth it! #kubernetes #devops", "tags": ["kubernetes", "devops", "cloud"], "categories": ["technology", "devops"]},
    {"content": "Flutter cross-platform development is incredible. One codebase, multiple platforms! #flutter #mobile", "tags": ["flutter", "mobile", "dart"], "categories": ["technology", "mobile"]},
    {"content": "PostgreSQL query optimization tips that saved us 80% execution time #database #sql", "tags": ["postgresql", "database", "sql"], "categories": ["technology", "database"]},
    {"content": "WebAssembly is the future of web performance. Near-native speed in the browser! #wasm #performance", "tags": ["webassembly", "performance", "web"], "categories": ["technology", "programming"]},
    {"content": "Microservices vs Monolith: Why we chose microservices for our new project #architecture #microservices", "tags": ["microservices", "architecture", "backend"], "categories": ["technology", "architecture"]},
    {"content": "Redis caching strategies that improved our API response time by 10x #redis #cache", "tags": ["redis", "cache", "performance"], "categories": ["technology", "database"]},
    {"content": "Machine Learning model deployment with FastAPI - it's surprisingly simple! #ml #fastapi", "tags": ["machinelearning", "fastapi", "python"], "categories": ["technology", "ai"]},
    {"content": "Next.js 14 server components are revolutionary for React apps #nextjs #react", "tags": ["nextjs", "react", "frontend"], "categories": ["technology", "programming"]},
    {"content": "MongoDB vs PostgreSQL: When to use which database? My experience #database #nosql", "tags": ["mongodb", "postgresql", "database"], "categories": ["technology", "database"]},
    {"content": "Tailwind CSS has completely replaced my custom CSS. Productivity through the roof! #tailwind #css", "tags": ["tailwind", "css", "frontend"], "categories": ["technology", "design"]},
    {"content": "Git workflow best practices that every developer should know #git #workflow", "tags": ["git", "workflow", "development"], "categories": ["technology", "programming"]},
    {"content": "AWS Lambda serverless functions - scale to zero, pay for what you use! #aws #serverless", "tags": ["aws", "serverless", "cloud"], "categories": ["technology", "cloud"]},
    {"content": "Testing strategies: Unit tests, Integration tests, E2E tests explained #testing #quality", "tags": ["testing", "quality", "development"], "categories": ["technology", "programming"]},
    {"content": "Svelte vs React: Why I'm switching to Svelte for my next project #svelte #frontend", "tags": ["svelte", "react", "frontend"], "categories": ["technology", "programming"]},

    # Food & Cooking (15 posts)
    {"content": "Made the perfect carbonara today! The secret is timing the egg mixture perfectly 🍝 #cooking #italian", "tags": ["cooking", "italian", "pasta"], "categories": ["food", "cooking"]},
    {"content": "Homemade sourdough bread journey - day 30 and my starter is finally perfect! #baking #bread", "tags": ["baking", "bread", "sourdough"], "categories": ["food", "baking"]},
    {"content": "Vietnamese pho from scratch. The broth simmered for 12 hours - worth every minute! #pho #vietnamese", "tags": ["pho", "vietnamese", "soup"], "categories": ["food", "cooking"]},
    {"content": "Vegan chocolate cake that tastes better than the original recipe! #vegan #dessert", "tags": ["vegan", "dessert", "baking"], "categories": ["food", "vegan"]},
    {"content": "Mastering the art of French omelette. Technique matters more than ingredients! #french #breakfast", "tags": ["french", "breakfast", "eggs"], "categories": ["food", "cooking"]},
    {"content": "Homemade ramen with chashu pork. Restaurant quality at home! #ramen #japanese", "tags": ["ramen", "japanese", "noodles"], "categories": ["food", "cooking"]},
    {"content": "Mediterranean salad with feta and olives - healthy and delicious! #mediterranean #salad", "tags": ["mediterranean", "salad", "healthy"], "categories": ["food", "healthy"]},
    {"content": "Korean kimchi fried rice - the ultimate comfort food #korean #friedrice", "tags": ["korean", "rice", "kimchi"], "categories": ["food", "cooking"]},
    {"content": "Croissants from scratch! 3 days of work but the buttery layers are perfection #baking #french", "tags": ["croissants", "baking", "french"], "categories": ["food", "baking"]},
    {"content": "Thai green curry that's better than takeout! #thai #curry", "tags": ["thai", "curry", "spicy"], "categories": ["food", "cooking"]},
    {"content": "Homemade pizza with 72-hour fermented dough. Game changer! #pizza #italian", "tags": ["pizza", "italian", "baking"], "categories": ["food", "cooking"]},
    {"content": "Sushi rolling techniques - finally got the rice texture right! #sushi #japanese", "tags": ["sushi", "japanese", "seafood"], "categories": ["food", "cooking"]},
    {"content": "Indian butter chicken with homemade naan bread #indian #curry", "tags": ["indian", "curry", "chicken"], "categories": ["food", "cooking"]},
    {"content": "Chocolate soufflé - intimidating but surprisingly doable! #dessert #french", "tags": ["dessert", "french", "chocolate"], "categories": ["food", "baking"]},
    {"content": "Mexican street tacos with homemade tortillas. Authenticity matters! #mexican #tacos", "tags": ["mexican", "tacos", "street-food"], "categories": ["food", "cooking"]},

    # Travel & Adventure (15 posts)
    {"content": "Hiking the Inca Trail to Machu Picchu was life-changing! #travel #peru #hiking", "tags": ["travel", "peru", "hiking"], "categories": ["travel", "adventure"]},
    {"content": "Tokyo street food tour - best takoyaki and okonomiyaki ever! #tokyo #japan #food", "tags": ["tokyo", "japan", "food"], "categories": ["travel", "food"]},
    {"content": "Scuba diving in the Great Barrier Reef. The underwater world is magical! #diving #australia", "tags": ["diving", "australia", "ocean"], "categories": ["travel", "adventure"]},
    {"content": "Northern Lights in Iceland - nature's most spectacular light show #iceland #aurora", "tags": ["iceland", "aurora", "nature"], "categories": ["travel", "nature"]},
    {"content": "Safari in Tanzania - seeing lions in the wild is unforgettable #safari #africa", "tags": ["safari", "africa", "wildlife"], "categories": ["travel", "adventure"]},
    {"content": "Backpacking through Europe - 15 countries in 3 months! #backpacking #europe", "tags": ["backpacking", "europe", "adventure"], "categories": ["travel", "adventure"]},
    {"content": "Santorini sunset views are worth all the hype! #greece #santorini", "tags": ["greece", "santorini", "sunset"], "categories": ["travel", "photography"]},
    {"content": "Trekking to Everest Base Camp - altitude sickness is real! #nepal #everest #trekking", "tags": ["nepal", "everest", "trekking"], "categories": ["travel", "adventure"]},
    {"content": "Bali rice terraces at sunrise. Pure serenity #bali #indonesia #nature", "tags": ["bali", "indonesia", "nature"], "categories": ["travel", "nature"]},
    {"content": "Road trip across New Zealand - both islands are breathtaking! #newzealand #roadtrip", "tags": ["newzealand", "roadtrip", "adventure"], "categories": ["travel", "adventure"]},
    {"content": "Street photography in Marrakech - colors and culture everywhere #morocco #photography", "tags": ["morocco", "photography", "culture"], "categories": ["travel", "photography"]},
    {"content": "Surfing in Hawaii - caught my first real wave today! #surfing #hawaii", "tags": ["surfing", "hawaii", "ocean"], "categories": ["travel", "sports"]},
    {"content": "Ancient temples of Angkor Wat at dawn. Mystical experience #cambodia #temples", "tags": ["cambodia", "temples", "history"], "categories": ["travel", "culture"]},
    {"content": "Patagonia glaciers - climate change is visible here #patagonia #chile #nature", "tags": ["patagonia", "chile", "nature"], "categories": ["travel", "nature"]},
    {"content": "Dubai desert safari - sand dunes and starry nights #dubai #desert", "tags": ["dubai", "desert", "adventure"], "categories": ["travel", "adventure"]},

    # Fitness & Sports (12 posts)
    {"content": "Marathon training week 12 - ran my first 30km! #running #marathon", "tags": ["running", "marathon", "fitness"], "categories": ["sports", "fitness"]},
    {"content": "Deadlift PR: 150kg! Consistency pays off #powerlifting #gym", "tags": ["powerlifting", "gym", "strength"], "categories": ["sports", "fitness"]},
    {"content": "Yoga for flexibility - finally touched my toes after 3 months! #yoga #flexibility", "tags": ["yoga", "flexibility", "wellness"], "categories": ["sports", "wellness"]},
    {"content": "CrossFit WOD crushed me today but I finished! #crossfit #fitness", "tags": ["crossfit", "fitness", "workout"], "categories": ["sports", "fitness"]},
    {"content": "Swimming technique improvement - breathing is everything #swimming #technique", "tags": ["swimming", "technique", "fitness"], "categories": ["sports", "fitness"]},
    {"content": "Rock climbing V5 send! Mental game is as important as strength #climbing #bouldering", "tags": ["climbing", "bouldering", "sports"], "categories": ["sports", "adventure"]},
    {"content": "Cycling 100km for the first time. Legs are jelly but worth it! #cycling #endurance", "tags": ["cycling", "endurance", "fitness"], "categories": ["sports", "fitness"]},
    {"content": "Boxing training - cardio and self-defense in one! #boxing #martial-arts", "tags": ["boxing", "martial-arts", "fitness"], "categories": ["sports", "fitness"]},
    {"content": "Trail running in the mountains beats treadmill any day #trailrunning #nature", "tags": ["trailrunning", "nature", "running"], "categories": ["sports", "nature"]},
    {"content": "Tennis lessons paying off - finally won a set! #tennis #sports", "tags": ["tennis", "sports", "racquet"], "categories": ["sports", "fitness"]},
    {"content": "Meal prep for muscle gain - hitting protein targets consistently #nutrition #bodybuilding", "tags": ["nutrition", "bodybuilding", "meal-prep"], "categories": ["sports", "nutrition"]},
    {"content": "Triathlon training - swim, bike, run. Triple the challenge! #triathlon #endurance", "tags": ["triathlon", "endurance", "multisport"], "categories": ["sports", "fitness"]},

    # Photography & Art (10 posts)
    {"content": "Golden hour portrait photography tips that transformed my shots #photography #portraits", "tags": ["photography", "portraits", "lighting"], "categories": ["photography", "art"]},
    {"content": "Landscape photography in the Swiss Alps - nature's masterpiece #landscape #photography", "tags": ["landscape", "photography", "nature"], "categories": ["photography", "nature"]},
    {"content": "Street photography ethics - candid vs staged moments #photography #ethics", "tags": ["photography", "street", "ethics"], "categories": ["photography", "art"]},
    {"content": "Long exposure astrophotography - captured the Milky Way! #astrophotography #stars", "tags": ["astrophotography", "stars", "night"], "categories": ["photography", "astronomy"]},
    {"content": "Watercolor painting techniques for beginners #art #watercolor", "tags": ["art", "watercolor", "painting"], "categories": ["art", "creativity"]},
    {"content": "Digital illustration workflow in Procreate #digitalart #illustration", "tags": ["digitalart", "illustration", "procreate"], "categories": ["art", "digital"]},
    {"content": "Macro photography of insects - a whole new world up close #macro #nature", "tags": ["macro", "nature", "photography"], "categories": ["photography", "nature"]},
    {"content": "Film photography revival - shot my first roll with a vintage camera #film #analog", "tags": ["film", "analog", "vintage"], "categories": ["photography", "art"]},
    {"content": "Urban sketching in the city - capturing architecture quickly #sketching #urban", "tags": ["sketching", "urban", "art"], "categories": ["art", "creativity"]},
    {"content": "Photography composition rules: Rule of thirds explained #photography #composition", "tags": ["photography", "composition", "tutorial"], "categories": ["photography", "education"]},

    # Music & Entertainment (8 posts)
    {"content": "Learning guitar - finally played my first song all the way through! #guitar #music", "tags": ["guitar", "music", "learning"], "categories": ["music", "hobby"]},
    {"content": "Jazz improvisation techniques that opened my musical mind #jazz #piano", "tags": ["jazz", "piano", "improvisation"], "categories": ["music", "art"]},
    {"content": "Electronic music production with Ableton Live #production #electronic", "tags": ["production", "electronic", "ableton"], "categories": ["music", "technology"]},
    {"content": "Classical music appreciation - discovering Beethoven's symphonies #classical #music", "tags": ["classical", "music", "appreciation"], "categories": ["music", "culture"]},
    {"content": "Singing lessons transformed my voice - breath control is key #singing #vocals", "tags": ["singing", "vocals", "music"], "categories": ["music", "learning"]},
    {"content": "Drums practice routine that actually works #drums #practice", "tags": ["drums", "practice", "music"], "categories": ["music", "learning"]},
    {"content": "Music theory basics every musician should know #theory #education", "tags": ["theory", "education", "music"], "categories": ["music", "education"]},
    {"content": "Vinyl record collecting - the warmth of analog sound #vinyl #audiophile", "tags": ["vinyl", "audiophile", "music"], "categories": ["music", "hobby"]},

    # Books & Learning (8 posts)
    {"content": "Reading 'Atomic Habits' changed how I build routines #books #productivity", "tags": ["books", "productivity", "self-improvement"], "categories": ["books", "education"]},
    {"content": "Learning Spanish with immersion method - 3 months in! #language #spanish", "tags": ["language", "spanish", "learning"], "categories": ["education", "language"]},
    {"content": "Philosophy 101: Stoicism for modern life #philosophy #stoicism", "tags": ["philosophy", "stoicism", "wisdom"], "categories": ["books", "philosophy"]},
    {"content": "Science fiction recommendations - my top 10 must-read books #scifi #books", "tags": ["scifi", "books", "reading"], "categories": ["books", "entertainment"]},
    {"content": "Online course on Machine Learning - best investment in my career #learning #ai", "tags": ["learning", "ai", "education"], "categories": ["education", "technology"]},
    {"content": "History podcast binge - WW2 from multiple perspectives #history #podcast", "tags": ["history", "podcast", "education"], "categories": ["education", "history"]},
    {"content": "Creative writing workshop - finding my voice as an author #writing #creativity", "tags": ["writing", "creativity", "books"], "categories": ["books", "art"]},
    {"content": "Economics explained - supply and demand in real life #economics #education", "tags": ["economics", "education", "finance"], "categories": ["education", "finance"]},

    # Lifestyle & Wellness (10 posts)
    {"content": "Minimalism changed my life - less stuff, more happiness #minimalism #lifestyle", "tags": ["minimalism", "lifestyle", "simple"], "categories": ["lifestyle", "wellness"]},
    {"content": "Meditation practice - 30 days of consistency and feeling calmer #meditation #mindfulness", "tags": ["meditation", "mindfulness", "wellness"], "categories": ["wellness", "mental-health"]},
    {"content": "Morning routine that sets up a productive day #productivity #routine", "tags": ["productivity", "routine", "lifestyle"], "categories": ["lifestyle", "productivity"]},
    {"content": "Plant-based diet benefits I noticed after 6 months #vegan #health", "tags": ["vegan", "health", "nutrition"], "categories": ["health", "nutrition"]},
    {"content": "Financial independence journey - saving 50% of income #finance #saving", "tags": ["finance", "saving", "money"], "categories": ["finance", "lifestyle"]},
    {"content": "Gardening therapy - growing your own vegetables is rewarding #gardening #wellness", "tags": ["gardening", "wellness", "nature"], "categories": ["lifestyle", "wellness"]},
    {"content": "Sleep optimization techniques that actually work #sleep #health", "tags": ["sleep", "health", "wellness"], "categories": ["health", "wellness"]},
    {"content": "Decluttering journey - KonMari method results #declutter #organization", "tags": ["declutter", "organization", "minimalism"], "categories": ["lifestyle", "organization"]},
    {"content": "Cold showers for 30 days - unexpected benefits #wellness #challenge", "tags": ["wellness", "challenge", "health"], "categories": ["wellness", "health"]},
    {"content": "Digital detox weekend - reconnecting with real life #detox #mindfulness", "tags": ["detox", "mindfulness", "lifestyle"], "categories": ["lifestyle", "wellness"]},
]

def initialize_firebase():
    """Initialize Firebase connection"""
    try:
        cred_path = os.path.join(os.path.dirname(__file__), "firebase-credentials.json")

        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Firebase credentials file not found at: {cred_path}")

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        db = firestore.client()
        print("[SUCCESS] Connected to Firebase Firestore")
        return db

    except Exception as e:
        print(f"[ERROR] Failed to connect to Firestore: {e}")
        raise

def get_random_user(db):
    """Get a random user from database"""
    users_ref = db.collection('users')
    users = list(users_ref.stream())

    if not users:
        raise ValueError("No users found in database. Please run populate_test_data.py first.")

    user_doc = random.choice(users)
    return {
        "id": user_doc.id,
        "username": user_doc.to_dict()['username']
    }

def add_posts(db):
    """Add additional posts to database"""
    print(f"\n{'='*60}")
    print(f"ADDING {len(ADDITIONAL_POSTS)} POSTS TO FIREBASE")
    print(f"{'='*60}")

    posts_ref = db.collection('posts')
    added_count = 0

    for i, post_data in enumerate(ADDITIONAL_POSTS, 1):
        # Get random user
        user = get_random_user(db)

        # Random creation time within last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        created_at = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)

        # Random likes and comments
        likes_count = random.randint(0, 50)
        comments_count = random.randint(0, 20)

        post_dict = {
            "user_id": user["id"],
            "content": post_data["content"],
            "tags": post_data["tags"],
            "categories": post_data["categories"],
            "image_url": None,
            "moderation_result": {
                "is_toxic": False,
                "is_spam": False,
                "is_hate_speech": False,
                "confidence_score": 0.95,
                "details": "Content approved - safe",
                "passed": True
            },
            "image_moderation_passed": True,
            "is_approved": True,
            "likes_count": likes_count,
            "comments_count": comments_count,
            "created_at": created_at,
            "updated_at": created_at
        }

        timestamp, doc_ref = posts_ref.add(post_dict)
        added_count += 1

        if added_count % 10 == 0:
            print(f"   ✓ Added {added_count}/{len(ADDITIONAL_POSTS)} posts")

    print(f"\n{'='*60}")
    print(f"✅ Successfully added {added_count} posts!")
    print(f"{'='*60}")
    print(f"\nPost distribution:")
    print(f"   - Tech & Programming: 20 posts")
    print(f"   - Food & Cooking: 15 posts")
    print(f"   - Travel & Adventure: 15 posts")
    print(f"   - Fitness & Sports: 12 posts")
    print(f"   - Photography & Art: 10 posts")
    print(f"   - Music & Entertainment: 8 posts")
    print(f"   - Books & Learning: 8 posts")
    print(f"   - Lifestyle & Wellness: 10 posts")
    print(f"\nTotal categories: 8 major topics")
    print(f"Total unique tags: 200+ tags")

def main():
    print("=" * 60)
    print("ADD MORE POSTS TO FIREBASE")
    print("=" * 60)

    db = initialize_firebase()
    add_posts(db)

    print("\n✅ Done! Your database now has diverse content for testing recommendations.")
    print("   Run your app and test the 'For You' feed with different user preferences!")

if __name__ == "__main__":
    main()
