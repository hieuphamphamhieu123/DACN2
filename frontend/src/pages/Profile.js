import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { postsAPI, authAPI } from '../services/api';
import PostCard from '../components/PostCard';
import '../styles/Profile.css';

const Profile = () => {
  const { user, setUser } = useAuth();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showPreferences, setShowPreferences] = useState(false);
  const [preferences, setPreferences] = useState({
    favorite_tags: [],
    interests: []
  });
  const [newTag, setNewTag] = useState('');
  const [newInterest, setNewInterest] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) {
      fetchUserPosts();
      fetchPreferences();
    }
  }, [user]);

  const fetchUserPosts = async () => {
    try {
      const response = await postsAPI.getPosts({ user_id: user.id });
      setPosts(response.data.posts);
    } catch (err) {
      console.error('Failed to fetch user posts:', err);
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

  const handlePostDeleted = (postId) => {
    setPosts(posts.filter(post => post.id !== postId));
  };

  const handlePostUpdated = (updatedPost) => {
    setPosts(posts.map(post => post.id === updatedPost.id ? updatedPost : post));
  };

  const addTag = () => {
    if (newTag.trim() && !preferences.favorite_tags.includes(newTag.trim())) {
      setPreferences({
        ...preferences,
        favorite_tags: [...preferences.favorite_tags, newTag.trim()]
      });
      setNewTag('');
    }
  };

  const removeTag = (tag) => {
    setPreferences({
      ...preferences,
      favorite_tags: preferences.favorite_tags.filter(t => t !== tag)
    });
  };

  const addInterest = () => {
    if (newInterest.trim() && !preferences.interests.includes(newInterest.trim())) {
      setPreferences({
        ...preferences,
        interests: [...preferences.interests, newInterest.trim()]
      });
      setNewInterest('');
    }
  };

  const removeInterest = (interest) => {
    setPreferences({
      ...preferences,
      interests: preferences.interests.filter(i => i !== interest)
    });
  };

  const savePreferences = async () => {
    try {
      setSaving(true);
      const response = await authAPI.updatePreferences(preferences);
      setUser(response.data);
      alert('Preferences saved! Your "For You" feed will now be personalized.');
      setShowPreferences(false);
    } catch (err) {
      console.error('Failed to save preferences:', err);
      alert('Failed to save preferences');
    } finally {
      setSaving(false);
    }
  };

  if (!user) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <div className="profile-avatar-large">
          {user.username[0].toUpperCase()}
        </div>
        <div className="profile-info">
          <h1>{user.full_name || user.username}</h1>
          <p className="username">@{user.username}</p>
          {user.email && <p className="email">{user.email}</p>}
          {user.bio && <p className="bio">{user.bio}</p>}
        </div>
      </div>

      <div className="profile-stats">
        <div className="stat">
          <span className="stat-number">{posts.length}</span>
          <span className="stat-label">Posts</span>
        </div>
      </div>

      <div className="profile-actions">
        <button onClick={() => setShowPreferences(!showPreferences)} className="btn-preferences">
          {showPreferences ? 'Hide Preferences' : 'Edit Preferences'}
        </button>
      </div>

      {showPreferences && (
        <div className="preferences-section">
          <h2>Your Preferences for AI Recommendations</h2>
          <p className="preferences-hint">
            Set your favorite tags and interests to personalize your "For You" feed!
          </p>

          <div className="preference-group">
            <h3>Favorite Tags</h3>
            <p className="hint">Tags you enjoy (e.g., tech, food, travel)</p>
            <div className="tag-input-group">
              <input
                type="text"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addTag()}
                placeholder="Add a tag..."
                className="tag-input"
              />
              <button onClick={addTag} className="btn-add">Add</button>
            </div>
            <div className="tags-list">
              {preferences.favorite_tags.map(tag => (
                <span key={tag} className="tag-item">
                  #{tag}
                  <button onClick={() => removeTag(tag)} className="btn-remove">×</button>
                </span>
              ))}
              {preferences.favorite_tags.length === 0 && (
                <p className="empty-state">No tags added yet</p>
              )}
            </div>
          </div>

          <div className="preference-group">
            <h3>Interests</h3>
            <p className="hint">Topics you're interested in (e.g., programming, cooking, sports)</p>
            <div className="tag-input-group">
              <input
                type="text"
                value={newInterest}
                onChange={(e) => setNewInterest(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addInterest()}
                placeholder="Add an interest..."
                className="tag-input"
              />
              <button onClick={addInterest} className="btn-add">Add</button>
            </div>
            <div className="tags-list">
              {preferences.interests.map(interest => (
                <span key={interest} className="tag-item">
                  {interest}
                  <button onClick={() => removeInterest(interest)} className="btn-remove">×</button>
                </span>
              ))}
              {preferences.interests.length === 0 && (
                <p className="empty-state">No interests added yet</p>
              )}
            </div>
          </div>

          <div className="preference-actions">
            <button onClick={savePreferences} disabled={saving} className="btn-save">
              {saving ? 'Saving...' : 'Save Preferences'}
            </button>
            <button onClick={() => setShowPreferences(false)} className="btn-cancel">
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="profile-section">
        <h2>Your Posts</h2>
        {loading ? (
          <div className="loading">Loading posts...</div>
        ) : posts.length > 0 ? (
          <div className="posts-grid">
            {posts.map(post => (
              <PostCard
                key={post.id}
                post={post}
                onDelete={handlePostDeleted}
                onUpdate={handlePostUpdated}
                onLike={() => {}} // No-op callback for profile page
              />
            ))}
          </div>
        ) : (
          <p className="no-posts">You haven't created any posts yet.</p>
        )}
      </div>
    </div>
  );
};

export default Profile;
