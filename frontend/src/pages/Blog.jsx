import React, { useEffect, useState } from 'react';
import { Calendar, ArrowRight, BookOpen } from 'lucide-react';
import { Link } from 'react-router-dom';
import { fetchBlogPosts } from '../api';

export default function Blog() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Track which blog card is currently being hovered
  const [hoveredPostId, setHoveredPostId] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const loadPosts = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await fetchBlogPosts();

        if (isMounted) {
          setPosts(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        console.error('Failed to fetch blog posts:', err);

        if (isMounted) {
          setError(
            'Unable to load blog posts right now. Please try again later.'
          );
          setPosts([]);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadPosts();

    return () => {
      isMounted = false;
    };
  }, []);

  const formatDate = (date) => {
    if (!date) return '';

    return new Date(date).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  return (
    <main className="blog-page">

      {/* HERO */}
      <section
        style={{
          background: '#0f172a',
          color: '#ffffff',
          padding: '5rem 0',
          textAlign: 'center'
        }}
      >
        <div className="container">

          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: '#dcfce7',
              color: '#15803d',
              padding: '0.5rem 1rem',
              borderRadius: '999px',
              fontWeight: 700,
              marginBottom: '1rem'
            }}
          >
            <BookOpen size={18} />
            Our Blog
          </div>

          <h1
            style={{
              fontSize: 'clamp(2.5rem, 5vw, 4rem)',
              fontWeight: 800,
              margin: '0 0 1rem'
            }}
          >
            Stories, Updates & News
          </h1>

          <p
            style={{
              maxWidth: '700px',
              margin: '0 auto',
              color: '#cbd5e1',
              fontSize: '1.1rem',
              lineHeight: 1.7
            }}
          >
            Stories from the communities we serve, updates from
            Piplad Welfare Foundation, and ideas that inspire
            positive change.
          </p>

        </div>
      </section>


      {/* BLOG LIST */}
      <section
        style={{
          background: '#f8fafc',
          padding: '5rem 0'
        }}
      >

        <div className="container">

          {/* Loading */}
          {loading && (
            <div
              style={{
                textAlign: 'center',
                padding: '4rem 1rem',
                color: '#64748b'
              }}
            >
              Loading blog posts...
            </div>
          )}


          {/* Error */}
          {!loading && error && (
            <div
              style={{
                maxWidth: '700px',
                margin: '0 auto',
                background: '#fef2f2',
                border: '1px solid #fecaca',
                color: '#991b1b',
                padding: '1.5rem',
                borderRadius: '12px',
                textAlign: 'center'
              }}
            >
              {error}
            </div>
          )}


          {/* Empty */}
          {!loading && !error && posts.length === 0 && (
            <div
              style={{
                textAlign: 'center',
                padding: '4rem 1rem'
              }}
            >
              <h2 style={{ color: '#0f172a' }}>
                No blog posts yet
              </h2>

              <p style={{ color: '#64748b' }}>
                New stories and updates will appear here soon.
              </p>
            </div>
          )}


          {/* Posts */}
          {!loading && !error && posts.length > 0 && (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns:
                  'repeat(auto-fit, minmax(300px, 1fr))',
                gap: '2rem'
              }}
            >

              {posts.map((post) => {

                const isHovered = hoveredPostId === post.id;

                return (
                  <article
                    key={post.id}
                    onMouseEnter={() => setHoveredPostId(post.id)}
                    onMouseLeave={() => setHoveredPostId(null)}
                    style={{
                      background: '#ffffff',
                      borderRadius: '18px',
                      overflow: 'hidden',

                      /*
                       * Hover effect:
                       * - Normal: standard shadow
                       * - Hover: card lifts 6px and shadow increases
                       */
                      boxShadow: isHovered
                        ? '0 18px 40px rgba(15, 23, 42, 0.15)'
                        : '0 8px 30px rgba(15, 23, 42, 0.08)',

                      border: '1px solid #e2e8f0',
                      display: 'flex',
                      flexDirection: 'column',

                      transform: isHovered
                        ? 'translateY(-6px)'
                        : 'translateY(0)',

                      transition:
                        'transform 0.25s ease, box-shadow 0.25s ease',

                      cursor: 'pointer'
                    }}
                  >

                    {/* Image */}
                    <div
                      style={{
                        height: '220px',
                        background: '#e2e8f0',
                        overflow: 'hidden'
                      }}
                    >

                      {post.image_url ? (
                        <img
                          src={post.image_url}
                          alt={post.title}
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',

                            /*
                             * Very subtle image zoom on hover.
                             * This keeps the effect elegant instead
                             * of making the card feel overly animated.
                             */
                            transform: isHovered
                              ? 'scale(1.03)'
                              : 'scale(1)',

                            transition: 'transform 0.35s ease'
                          }}
                        />
                      ) : (
                        <div
                          style={{
                            width: '100%',
                            height: '100%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: '#64748b',
                            fontWeight: 600
                          }}
                        >
                          Piplad Welfare Foundation
                        </div>
                      )}

                    </div>


                    {/* Content */}
                    <div
                      style={{
                        padding: '1.75rem',
                        display: 'flex',
                        flexDirection: 'column',
                        flex: 1
                      }}
                    >

                      {/* Date */}
                      {post.published_date && (
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            color: '#65a30d',
                            fontSize: '0.85rem',
                            fontWeight: 700,
                            marginBottom: '0.75rem'
                          }}
                        >
                          <Calendar size={16} />

                          {formatDate(post.published_date)}
                        </div>
                      )}


                      {/* Title */}
                      <h2
                        style={{
                          color: '#0f172a',
                          fontSize: '1.35rem',
                          lineHeight: 1.35,
                          margin: '0 0 0.75rem'
                        }}
                      >
                        {post.title}
                      </h2>


                      {/* Summary */}
                      <p
                        style={{
                          color: '#475569',
                          lineHeight: 1.7,
                          margin: '0 0 1.5rem'
                        }}
                      >
                        {post.summary ||
                          'Read the latest story from Piplad Welfare Foundation.'}
                      </p>


                      {/* Read More */}
                      <div
                        style={{
                          marginTop: 'auto'
                        }}
                      >

                        <Link
                          to={`/blog/${post.id}`}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            color: '#15803d',
                            fontWeight: 700,
                            textDecoration: 'none'
                          }}
                        >
                          Read More

                          <ArrowRight
                            size={18}
                            style={{
                              transform: isHovered
                                ? 'translateX(4px)'
                                : 'translateX(0)',
                              transition:
                                'transform 0.25s ease'
                            }}
                          />

                        </Link>

                      </div>

                    </div>

                  </article>
                );
              })}

            </div>
          )}

        </div>

      </section>

    </main>
  );
}