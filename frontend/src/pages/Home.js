import React, { useState, useEffect } from 'react';
import { postsAPI, authAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import PostCard from '../components/PostCard';
import '../styles/Home.css';

const Home = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [feedType, setFeedType] = useState('all'); // 'all' or 'personalized'
  const { user, setUser } = useAuth();

  // Preferences state
  const [preferences, setPreferences] = useState({
    favorite_tags: [],
    interests: []
  });
  const [showPreferencesEdit, setShowPreferencesEdit] = useState(false);
  const [newTag, setNewTag] = useState('');
  const [savingPreferences, setSavingPreferences] = useState(false);

  // Popular tags for suggestions
  const popularTags = [
    'tech', 'programming', 'javascript', 'python', 'react', 'nodejs',
    'food', 'cooking', 'recipes', 'travel', 'adventure', 'photography',
    'fitness', 'sports', 'health', 'art', 'design', 'music'
  ];

  useEffect(() => {
    fetchPosts();
  }, [feedType, page, user?.preferences]);

  useEffect(() => {
    if (user) {
      fetchPreferences();
    }
  }, [user]);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const endpoint = feedType === 'personalized' ? postsAPI.getFeed : postsAPI.getPosts;
      const response = await endpoint({ page, page_size: 20 });

      if (page === 1) {
        setPosts(response.data.posts);
      } else {
        setPosts(prev => [...prev, ...response.data.posts]);
      }

      setHasMore(response.data.has_more);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch posts:', err);
      setError('Failed to load posts');
    } finally {
      setLoading(false);
    }
  };

  const fetchPreferences = async () => {
    try {
      const response = await authAPI.getPreferences();
      setPreferences(response.data);
    } catch (err) {
      console.error('Failed to fetch preferences:', err);
    }
  };

  const toggleTag = (tag) => {
    const isFavorite = preferences.favorite_tags.includes(tag);
    const newTags = isFavorite
      ? preferences.favorite_tags.filter(t => t !== tag)
      : [...preferences.favorite_tags, tag];

    setPreferences({
      ...preferences,
      favorite_tags: newTags
    });
  };

  const addCustomTag = () => {
    if (newTag.trim() && !preferences.favorite_tags.includes(newTag.trim())) {
      setPreferences({
        ...preferences,
        favorite_tags: [...preferences.favorite_tags, newTag.trim()]
      });
      setNewTag('');
    }
  };

  const savePreferences = async () => {
    try {
      setSavingPreferences(true);
      const response = await authAPI.updatePreferences(preferences);
      setUser(response.data);
      setShowPreferencesEdit(false);
      // Refresh feed to apply new preferences
      setPage(1);
      fetchPosts();
    } catch (err) {
      console.error('Failed to save preferences:', err);
      alert('Failed to save preferences');
    } finally {
      setSavingPreferences(false);
    }
  };

  const handlePostDeleted = (postId) => {
    setPosts(posts.filter(post => post.id !== postId));
  };

  const handlePostUpdated = (updatedPost) => {
    setPosts(posts.map(post => post.id === updatedPost.id ? updatedPost : post));
  };

  const handlePostLiked = () => {
    // Refresh personalized feed when user likes a post
    // This allows the recommendation system to re-rank based on new engagement
    if (feedType === 'personalized') {
      setPage(1);
      fetchPosts();
    }
  };

  const loadMore = () => {
    setPage(prev => prev + 1);
  };

  const switchFeed = (type) => {
    setFeedType(type);
    setPage(1);
    setPosts([]);
  };

  return (
    <div className="home-container">
      <div className="feed-header">
        <h1>Feed</h1>
        <div className="feed-toggle">
          <button
            className={feedType === 'all' ? 'active' : ''}
            onClick={() => switchFeed('all')}
          >
            All Posts
          </button>
          <button
            className={feedType === 'personalized' ? 'active' : ''}
            onClick={() => switchFeed('personalized')}
          >
            For You
          </button>
        </div>
      </div>

      {/* Compact Preferences Section - Only show for "For You" feed */}
      {feedType === 'personalized' && (
        <div className="preferences-compact">
          <div className="preferences-compact-header">
            <div className="preferences-title">
              <span className="preferences-icon">✨</span>
              <h3>Your Interests</h3>
              <span className="preferences-subtitle">
                ({preferences.favorite_tags.length} selected)
              </span>
            </div>
            <button
              className="btn-edit-preferences"
              onClick={() => setShowPreferencesEdit(!showPreferencesEdit)}
            >
              {showPreferencesEdit ? 'Done' : 'Customize'}
            </button>
          </div>

          {showPreferencesEdit && (
            <div className="preferences-edit-section">
              <div className="custom-tag-input">
                <input
                  type="text"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addCustomTag()}
                  placeholder="Add custom interest..."
                  className="tag-input-field"
                />
                <button onClick={addCustomTag} className="btn-add-tag">+</button>
              </div>
              <p className="popular-tags-label">Popular interests:</p>
            </div>
          )}

          <div className="tags-cloud">
            {showPreferencesEdit ? (
              // Show popular tags for selection when editing
              popularTags.map(tag => (
                <button
                  key={tag}
                  className={`tag-chip ${preferences.favorite_tags.includes(tag) ? 'selected' : ''}`}
                  onClick={() => toggleTag(tag)}
                >
                  {tag}
                  {preferences.favorite_tags.includes(tag) && <span className="check-mark">✓</span>}
                </button>
              ))
            ) : (
              // Show only selected tags when not editing
              preferences.favorite_tags.length > 0 ? (
                preferences.favorite_tags.map(tag => (
                  <span key={tag} className="tag-chip selected">
                    {tag}
                  </span>
                ))
              ) : (
                <p className="no-preferences-message">
                  Click "Customize" to select your interests and get personalized recommendations!
                </p>
              )
            )}
          </div>

          {showPreferencesEdit && (
            <div className="preferences-actions">
              <button
                onClick={savePreferences}
                disabled={savingPreferences}
                className="btn-save-preferences"
              >
                {savingPreferences ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          )}
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      <div className="posts-grid">
        {posts.map(post => (
          <PostCard
            key={post.id}
            post={post}
            onDelete={handlePostDeleted}
            onUpdate={handlePostUpdated}
            onLike={handlePostLiked}
          />
        ))}
      </div>

      {loading && <div className="loading">Loading posts...</div>}

      {!loading && posts.length === 0 && (
        <div className="no-posts">
          <p>No posts yet. Be the first to post!</p>
        </div>
      )}

      {!loading && hasMore && (
        <button onClick={loadMore} className="load-more-btn">
          Load More
        </button>
      )}
    </div>
  );
};

export default Home;
