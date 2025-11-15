import React, { useState, useEffect } from 'react';
import { commentsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import '../styles/CommentSection.css';

const CommentSection = ({ postId, onCommentAdded, onCommentDeleted }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    fetchComments();
  }, [postId]);

  const fetchComments = async () => {
    try {
      const response = await commentsAPI.getComments(postId);
      setComments(response.data.comments);
    } catch (err) {
      console.error('Failed to fetch comments:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      setSubmitting(true);
      const response = await commentsAPI.createComment(postId, {
        content: newComment,
      });
      setComments([response.data, ...comments]);
      setNewComment('');
      onCommentAdded();
    } catch (err) {
      console.error('Failed to create comment:', err);
      alert('Failed to post comment');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (commentId) => {
    if (!window.confirm('Delete this comment?')) return;

    try {
      await commentsAPI.deleteComment(commentId);
      setComments(comments.filter(c => c.id !== commentId));
      onCommentDeleted();
    } catch (err) {
      console.error('Failed to delete comment:', err);
      alert('Failed to delete comment');
    }
  };

  if (loading) {
    return <div className="comments-loading">Loading comments...</div>;
  }

  return (
    <div className="comment-section">
      <form onSubmit={handleSubmit} className="comment-form">
        <input
          type="text"
          placeholder="Write a comment..."
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          disabled={submitting}
          className="comment-input"
        />
        <button
          type="submit"
          disabled={submitting || !newComment.trim()}
          className="comment-submit-btn"
        >
          {submitting ? 'Posting...' : 'Post'}
        </button>
      </form>

      <div className="comments-list">
        {comments.map((comment) => (
          <div key={comment.id} className="comment">
            <div className="comment-header">
              <div className="comment-author">
                <span className="author-avatar-small">
                  {comment.username[0].toUpperCase()}
                </span>
                <span className="comment-username">{comment.username}</span>
                <span className="comment-date">
                  {new Date(comment.created_at).toLocaleDateString()}
                </span>
              </div>
              {user && user.id === comment.user_id && (
                <button
                  className="comment-delete-btn"
                  onClick={() => handleDelete(comment.id)}
                >
                  ×
                </button>
              )}
            </div>
            <p className="comment-content">{comment.content}</p>
          </div>
        ))}
      </div>

      {comments.length === 0 && (
        <p className="no-comments">No comments yet. Be the first to comment!</p>
      )}
    </div>
  );
};

export default CommentSection;
