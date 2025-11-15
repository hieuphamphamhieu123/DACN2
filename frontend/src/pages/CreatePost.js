import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { postsAPI } from '../services/api';
import '../styles/CreatePost.css';

const CreatePost = () => {
  const [content, setContent] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [tags, setTags] = useState('');
  const [categories, setCategories] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [moderationResult, setModerationResult] = useState(null);
  const navigate = useNavigate();

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Please select a valid image file');
        return;
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('Image size should be less than 5MB');
        return;
      }

      setImageFile(file);
      setError(null);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setImageFile(null);
    setImagePreview(null);
    setImageUrl('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setModerationResult(null);

    try {
      setLoading(true);

      let finalImageUrl = imageUrl;

      // If user uploaded a file, convert to base64
      if (imageFile && !imageUrl) {
        const reader = new FileReader();
        finalImageUrl = await new Promise((resolve, reject) => {
          reader.onloadend = () => resolve(reader.result);
          reader.onerror = reject;
          reader.readAsDataURL(imageFile);
        });
      }

      const postData = {
        content,
        image_url: finalImageUrl || null,
        tags: tags ? tags.split(',').map(t => t.trim()).filter(t => t) : [],
        categories: categories ? categories.split(',').map(c => c.trim()).filter(c => c) : [],
      };

      const response = await postsAPI.createPost(postData);
      const post = response.data;

      // Show moderation results
      if (post.moderation_result) {
        setModerationResult(post.moderation_result);
      }

      if (post.is_approved) {
        // Post approved, redirect to home
        setTimeout(() => {
          navigate('/');
        }, 2000);
      } else {
        // Post blocked due to moderation
        setError('Your post was blocked due to content policy violations.');
      }
    } catch (err) {
      console.error('Failed to create post:', err);
      setError(err.response?.data?.detail || 'Failed to create post');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-post-container">
      <div className="create-post-card">
        <h1>Create New Post</h1>

        {error && <div className="error-message">{error}</div>}

        {moderationResult && (
          <div className={`moderation-result ${moderationResult.is_toxic || moderationResult.is_spam || moderationResult.is_hate_speech ? 'warning' : 'success'}`}>
            <h3>AI Moderation Result</h3>
            <p><strong>Status:</strong> {moderationResult.details}</p>
            <div className="moderation-scores">
              <div>Toxic: {moderationResult.is_toxic ? 'Yes' : 'No'}</div>
              <div>Spam: {moderationResult.is_spam ? 'Yes' : 'No'}</div>
              <div>Hate Speech: {moderationResult.is_hate_speech ? 'Yes' : 'No'}</div>
              <div>Confidence: {(moderationResult.confidence_score * 100).toFixed(1)}%</div>
            </div>
            {!error && (
              <p className="success-text">Your post has been created successfully and will redirect shortly...</p>
            )}
          </div>
        )}

        <form onSubmit={handleSubmit} className="create-post-form">
          <div className="form-group">
            <label htmlFor="content">Content *</label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="What's on your mind?"
              required
              disabled={loading}
              rows="6"
            />
          </div>

          <div className="form-group">
            <label>Image (optional)</label>

            {/* Image Preview */}
            {imagePreview && (
              <div className="image-preview">
                <img src={imagePreview} alt="Preview" />
                <button
                  type="button"
                  onClick={removeImage}
                  className="remove-image-btn"
                  disabled={loading}
                >
                  ✕ Remove
                </button>
              </div>
            )}

            {/* File Upload */}
            {!imagePreview && (
              <div className="image-upload-section">
                <label htmlFor="imageFile" className="file-upload-label">
                  <div className="upload-placeholder">
                    <span className="upload-icon">📷</span>
                    <span>Click to upload image</span>
                    <span className="upload-hint">JPG, PNG, GIF (Max 5MB)</span>
                  </div>
                  <input
                    type="file"
                    id="imageFile"
                    accept="image/*"
                    onChange={handleImageChange}
                    disabled={loading}
                    style={{ display: 'none' }}
                  />
                </label>

                <div className="or-divider">
                  <span>OR</span>
                </div>

                {/* URL Input as alternative */}
                <input
                  type="url"
                  id="imageUrl"
                  value={imageUrl}
                  onChange={(e) => {
                    setImageUrl(e.target.value);
                    if (e.target.value) {
                      setImagePreview(e.target.value);
                    }
                  }}
                  placeholder="Paste image URL"
                  disabled={loading}
                  className="image-url-input"
                />
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="tags">Tags (comma-separated)</label>
            <input
              type="text"
              id="tags"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="tech, ai, programming"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="categories">Categories (comma-separated)</label>
            <input
              type="text"
              id="categories"
              value={categories}
              onChange={(e) => setCategories(e.target.value)}
              placeholder="technology, lifestyle"
              disabled={loading}
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="btn-secondary"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={loading || !content.trim()}
            >
              {loading ? 'Creating...' : 'Create Post'}
            </button>
          </div>
        </form>

        <div className="ai-info">
          <p><strong>Note:</strong> Your post will be automatically checked by AI for inappropriate content including toxic language, spam, and hate speech.</p>
        </div>
      </div>
    </div>
  );
};

export default CreatePost;
