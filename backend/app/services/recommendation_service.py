"""
Recommendation Service for personalized feed
Uses content-based filtering with sentence embeddings
"""
from typing import List, Dict
import logging
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Service for generating personalized post recommendations
    Uses sentence embeddings for semantic similarity
    """

    def __init__(self):
        try:
            print("=" * 60)
            print("LOADING AI RECOMMENDATION MODEL...")
            print("=" * 60)
            logger.info("=" * 60)
            logger.info("LOADING AI RECOMMENDATION MODEL...")
            logger.info("=" * 60)

            # Load lightweight sentence transformer model
            model_name = 'all-MiniLM-L6-v2'
            print(f"Model: {model_name}")
            print("Loading sentence transformer (TRAINED ML MODEL)...")
            logger.info(f"Model: {model_name}")
            logger.info("Loading sentence transformer (TRAINED ML MODEL)...")

            self.model = SentenceTransformer(model_name)

            print("=" * 60)
            print("SENTENCE EMBEDDING MODEL READY!")
            print(f"   - Model: {model_name}")
            print(f"   - Type: Transformer-based sentence embeddings (TRAINED ML MODEL)")
            print(f"   - Purpose: Semantic similarity for personalized recommendations")
            print("=" * 60)
            logger.info("=" * 60)
            logger.info("SENTENCE EMBEDDING MODEL READY!")
            logger.info(f"   - Model: {model_name}")
            logger.info(f"   - Type: Transformer-based sentence embeddings (TRAINED ML MODEL)")
            logger.info(f"   - Purpose: Semantic similarity for personalized recommendations")
            logger.info("=" * 60)
            self.use_embeddings = True
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            logger.warning("⚠️  Falling back to tag-based recommendation (NOT ML)")
            self.model = None
            self.use_embeddings = False

    def _create_post_text(self, post: Dict) -> str:
        """Create a text representation of a post for embedding"""
        content = post.get("content", "")
        tags = " ".join(post.get("tags", []))
        categories = " ".join(post.get("categories", []))
        return f"{content} {tags} {categories}".strip()

    def _create_user_profile_text(self, user_preferences: Dict, liked_posts: List[Dict] = None) -> str:
        """
        Create a text representation of user preferences
        Learns from both manual preferences and actual liked posts (behavior-based learning)
        """
        # Manual preferences (40% weight)
        favorite_tags = " ".join(user_preferences.get("favorite_tags", []))
        interests = " ".join(user_preferences.get("interests", []))
        manual_profile = f"{favorite_tags} {interests}".strip()

        # Learn from liked posts (60% weight - AI learns from actual user behavior)
        learned_profile = ""
        if liked_posts:
            learned_tags = []
            learned_categories = []
            learned_content = []
            for post in liked_posts:
                learned_tags.extend(post.get("tags", []))
                learned_categories.extend(post.get("categories", []))
                # Also learn from content of liked posts
                content = post.get("content", "")
                if content:
                    learned_content.append(content[:200])  # First 200 chars

            # Use frequency: most liked tags/categories appear more times
            learned_profile = " ".join(learned_tags + learned_categories + learned_content)

        # Combine: manual preferences + learned behavior (repeat learned to give it more weight)
        if learned_profile:
            return f"{manual_profile} {learned_profile} {learned_profile}".strip()
        return manual_profile

    def calculate_post_score(
        self,
        post: Dict,
        user_preferences: Dict,
        user_embedding: np.ndarray = None
    ) -> float:
        """
        Calculate relevance score for a post based on user preferences

        Args:
            post: Post document from database
            user_preferences: User preferences with favorite_tags and interests
            user_embedding: Pre-computed user preference embedding (optional)

        Returns:
            Score between 0 and 1
        """
        if self.use_embeddings and self.model is not None and user_embedding is not None:
            try:
                return self._calculate_score_with_embeddings(post, user_embedding)
            except Exception as e:
                logger.error(f"Embedding-based scoring failed: {e}, falling back to tag-based")
                return self._calculate_score_tag_based(post, user_preferences)
        else:
            return self._calculate_score_tag_based(post, user_preferences)

    def _calculate_score_with_embeddings(
        self,
        post: Dict,
        user_embedding: np.ndarray
    ) -> float:
        """
        Calculate score using sentence embeddings with advanced ranking
        Combines semantic similarity, engagement, and recency
        """
        # Create post text
        post_text = self._create_post_text(post)

        if not post_text:
            return 0.1  # Low score for empty posts

        # Get post embedding
        post_embedding = self.model.encode([post_text])[0]

        # Calculate cosine similarity
        similarity = cosine_similarity(
            user_embedding.reshape(1, -1),
            post_embedding.reshape(1, -1)
        )[0][0]

        # Normalize to 0-1 range (cosine similarity is -1 to 1)
        # Apply exponential boost for high similarity
        semantic_score = (similarity + 1) / 2
        # Boost high-similarity posts more aggressively
        semantic_score = semantic_score ** 0.7  # Makes high scores even higher

        # Engagement score (with logarithmic scaling to avoid dominance)
        likes = post.get("likes_count", 0)
        comments = post.get("comments_count", 0)
        total_engagement = likes * 0.7 + comments * 0.3
        # Log scale: 1 like = 0.3, 10 likes = 0.69, 100 likes = 1.0
        engagement_score = min(np.log1p(total_engagement) / np.log1p(100), 1.0) if total_engagement > 0 else 0.0

        # Recency score (newer posts get small boost)
        from datetime import datetime, timezone
        try:
            created_at = post.get("created_at")
            if created_at:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                age_days = (now - created_at).total_seconds() / 86400
                # Posts within 7 days get boost, older posts decay
                recency_score = max(0, 1 - (age_days / 30))  # Decays over 30 days
            else:
                recency_score = 0.5
        except Exception as e:
            logger.warning(f"Failed to calculate recency: {e}")
            recency_score = 0.5

        # Combined scoring with weights:
        # 70% semantic similarity (user preferences/behavior match)
        # 20% engagement (popular content)
        # 10% recency (fresh content)
        final_score = (
            semantic_score * 0.70 +
            engagement_score * 0.20 +
            recency_score * 0.10
        )

        return float(final_score)

    def _calculate_score_tag_based(
        self,
        post: Dict,
        user_preferences: Dict
    ) -> float:
        """Fallback tag-based scoring"""
        score = 0.0
        max_score = 0.0

        # Get user's favorite tags and interests
        favorite_tags = user_preferences.get("favorite_tags", [])
        interests = user_preferences.get("interests", [])

        post_tags = post.get("tags", [])
        post_categories = post.get("categories", [])

        # Score based on matching tags (40% weight)
        if favorite_tags:
            max_score += 0.4
            matching_tags = set(post_tags) & set(favorite_tags)
            if matching_tags:
                tag_score = len(matching_tags) / max(len(favorite_tags), len(post_tags))
                score += tag_score * 0.4

        # Score based on matching interests/categories (40% weight)
        if interests:
            max_score += 0.4
            matching_interests = set(post_categories) & set(interests)
            if matching_interests:
                interest_score = len(matching_interests) / max(len(interests), len(post_categories))
                score += interest_score * 0.4

        # Score based on engagement (20% weight)
        max_score += 0.2
        likes = post.get("likes_count", 0)
        comments = post.get("comments_count", 0)
        engagement_score = min((likes * 0.7 + comments * 0.3) / 100, 1.0)
        score += engagement_score * 0.2

        # Normalize score
        if max_score > 0:
            return score / max_score
        return 0.5  # Default score for posts with no preference match

    async def get_recommended_posts(
        self,
        all_posts: List[Dict],
        user_preferences: Dict,
        liked_posts: List[Dict] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get recommended posts sorted by relevance score
        Uses AI to learn from user's actual behavior (liked posts)
        Implements explore/exploit strategy with diversity injection

        Args:
            all_posts: List of all available posts
            user_preferences: User's manual preferences (favorite_tags, interests)
            liked_posts: Posts that user has liked (for behavior-based learning)
            limit: Maximum number of posts to return

        Returns:
            List of posts sorted by relevance with diversity
        """
        if not all_posts:
            return []

        # Pre-compute user embedding if using embeddings
        # AI learns from both manual preferences AND actual behavior (likes)
        user_embedding = None
        if self.use_embeddings and self.model is not None:
            try:
                user_profile_text = self._create_user_profile_text(user_preferences, liked_posts)
                if user_profile_text:
                    user_embedding = self.model.encode([user_profile_text])[0]
                    logger.info(f"AI learned from {len(liked_posts) if liked_posts else 0} liked posts")
            except Exception as e:
                logger.error(f"Failed to create user embedding: {e}")

        # Calculate score for each post
        scored_posts = []
        for post in all_posts:
            score = self.calculate_post_score(post, user_preferences, user_embedding)
            scored_posts.append({
                "post": post,
                "score": score
            })

        # Sort by score (highest first)
        scored_posts.sort(key=lambda x: x["score"], reverse=True)

        # Implement diversity injection (explore vs exploit)
        # Take top 80% by score (exploit), bottom 20% random (explore)
        import random
        exploit_count = int(limit * 0.85)  # 85% high-relevance
        explore_count = limit - exploit_count  # 15% diverse content

        final_posts = []

        # Add top scoring posts (exploitation)
        final_posts.extend([item["post"] for item in scored_posts[:exploit_count]])

        # Add some random diverse posts from lower scored items (exploration)
        # This prevents filter bubble and helps discover new interests
        if len(scored_posts) > exploit_count and explore_count > 0:
            # Get posts from 20-60th percentile for diversity
            diverse_pool_start = min(exploit_count, len(scored_posts) // 5)
            diverse_pool_end = min(len(scored_posts), len(scored_posts) * 3 // 5)
            diverse_pool = scored_posts[diverse_pool_start:diverse_pool_end]

            if diverse_pool:
                explore_posts = random.sample(
                    diverse_pool,
                    min(explore_count, len(diverse_pool))
                )
                final_posts.extend([item["post"] for item in explore_posts])

        # Shuffle slightly to avoid always same order
        # Keep top 5 fixed, shuffle the rest slightly
        if len(final_posts) > 5:
            top_5 = final_posts[:5]
            rest = final_posts[5:]
            random.shuffle(rest)
            final_posts = top_5 + rest

        return final_posts[:limit]

    async def get_similar_posts(
        self,
        post: Dict,
        all_posts: List[Dict],
        limit: int = 5
    ) -> List[Dict]:
        """
        Get posts similar to a given post

        Args:
            post: The reference post
            all_posts: All available posts
            limit: Maximum number of similar posts

        Returns:
            List of similar posts
        """
        post_id = post.get("id") or post.get("_id")

        if self.use_embeddings and self.model is not None:
            try:
                return self._get_similar_posts_with_embeddings(post, all_posts, limit, post_id)
            except Exception as e:
                logger.error(f"Embedding-based similarity failed: {e}, falling back to tag-based")
                return self._get_similar_posts_tag_based(post, all_posts, limit, post_id)
        else:
            return self._get_similar_posts_tag_based(post, all_posts, limit, post_id)

    def _get_similar_posts_with_embeddings(
        self,
        post: Dict,
        all_posts: List[Dict],
        limit: int,
        post_id: str
    ) -> List[Dict]:
        """Get similar posts using embeddings"""
        # Get reference post embedding
        post_text = self._create_post_text(post)
        if not post_text:
            return []

        post_embedding = self.model.encode([post_text])[0]

        # Calculate similarity for all posts
        similar_posts = []
        for candidate in all_posts:
            candidate_id = candidate.get("id") or candidate.get("_id")
            if candidate_id == post_id:
                continue

            candidate_text = self._create_post_text(candidate)
            if not candidate_text:
                continue

            candidate_embedding = self.model.encode([candidate_text])[0]

            # Calculate cosine similarity
            similarity = cosine_similarity(
                post_embedding.reshape(1, -1),
                candidate_embedding.reshape(1, -1)
            )[0][0]

            # Normalize to 0-1
            similarity_score = (similarity + 1) / 2

            if similarity_score > 0.3:  # Only include if somewhat similar
                similar_posts.append({
                    "post": candidate,
                    "score": float(similarity_score)
                })

        # Sort by similarity
        similar_posts.sort(key=lambda x: x["score"], reverse=True)

        return [item["post"] for item in similar_posts[:limit]]

    def _get_similar_posts_tag_based(
        self,
        post: Dict,
        all_posts: List[Dict],
        limit: int,
        post_id: str
    ) -> List[Dict]:
        """Fallback tag-based similarity"""
        post_tags = set(post.get("tags", []))
        post_categories = set(post.get("categories", []))

        similar_posts = []

        for candidate in all_posts:
            candidate_id = candidate.get("id") or candidate.get("_id")
            if candidate_id == post_id:
                continue

            # Calculate similarity based on tags and categories
            candidate_tags = set(candidate.get("tags", []))
            candidate_categories = set(candidate.get("categories", []))

            # Jaccard similarity for tags
            tag_similarity = 0
            if post_tags or candidate_tags:
                tag_intersection = len(post_tags & candidate_tags)
                tag_union = len(post_tags | candidate_tags)
                tag_similarity = tag_intersection / tag_union if tag_union > 0 else 0

            # Jaccard similarity for categories
            category_similarity = 0
            if post_categories or candidate_categories:
                category_intersection = len(post_categories & candidate_categories)
                category_union = len(post_categories | candidate_categories)
                category_similarity = category_intersection / category_union if category_union > 0 else 0

            # Combined similarity score
            similarity_score = (tag_similarity * 0.6 + category_similarity * 0.4)

            if similarity_score > 0:
                similar_posts.append({
                    "post": candidate,
                    "score": similarity_score
                })

        # Sort by similarity
        similar_posts.sort(key=lambda x: x["score"], reverse=True)

        return [item["post"] for item in similar_posts[:limit]]


# Singleton instance
recommendation_service = RecommendationService()
