import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { postsAPI, likesAPI } from '../services/api';
import CommentSection from './CommentSection';
import '../styles/PostCard.css';

const PostCard = ({ post, onDelete, onUpdate, onLike }) => {
  const { user } = useAuth();
  const [showComments, setShowComments] = useState(false);
  const [isLiked, setIsLiked] = useState(post.is_liked_by_user);
  const [likesCount, setLikesCount] = useState(post.likes_count);
  const [commentsCount, setCommentsCount] = useState(post.comments_count);
  const [isDeleting, setIsDeleting] = useState(false);

  const isOwner = user && user.id === post.user_id;

  const handleLike = async () => {
    try {
      const response = await likesAPI.toggleLike(post.id);
      setIsLiked(response.data.is_liked);
      setLikesCount(response.data.likes_count);

      // Notify parent component that a like happened
      if (onLike) {
        onLike();
      }
    } catch (err) {
      console.error('Failed to toggle like:', err);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this post?')) {
      return;
    }

    try {
      setIsDeleting(true);
      await postsAPI.deletePost(post.id);
      onDelete(post.id);
    } catch (err) {
      console.error('Failed to delete post:', err);
      alert('Failed to delete post');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCommentAdded = () => {
    setCommentsCount(prev => prev + 1);
  };

  const handleCommentDeleted = () => {
    setCommentsCount(prev => Math.max(0, prev - 1));
  };

  return (
    <div className="post-card">
      <div className="post-header">
        <div className="post-author">
          <div className="author-avatar">{post.username[0].toUpperCase()}</div>
          <div>
            <div className="author-name">{post.username}</div>
            <div className="post-date">
              {new Date(post.created_at).toLocaleDateString()}
            </div>
          </div>
        </div>
        {isOwner && (
          <button
            className="delete-btn"
            onClick={handleDelete}
            disabled={isDeleting}
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
        )}
      </div>

      <div className="post-content">
        <p>{post.content}</p>
        {post.image_url && (
          <img src={post.image_url} alt="Post" className="post-image" />
        )}
      </div>

      {post.tags && post.tags.length > 0 && (
        <div className="post-tags">
          {post.tags.map((tag, index) => (
            <span key={index} className="tag">#{tag}</span>
          ))}
        </div>
      )}

      {post.moderation_result && !post.is_approved && (
        <div className="moderation-warning">
          <strong>Content Warning:</strong> {post.moderation_result.details}
        </div>
      )}

      <div className="post-actions">
        <button
          className={`action-btn ${isLiked ? 'liked' : ''}`}
          onClick={handleLike}
        >
          <span className="icon">{isLiked ? '❤️' : '🤍'}</span>
          <span>{likesCount}</span>
        </button>
        <button
          className="action-btn"
          onClick={() => setShowComments(!showComments)}
        >
          <span className="icon">💬</span>
          <span>{commentsCount}</span>
        </button>
      </div>

      {showComments && (
        <CommentSection
          postId={post.id}
          onCommentAdded={handleCommentAdded}
          onCommentDeleted={handleCommentDeleted}
        />
      )}
    </div>
  );
};

export default PostCard;
