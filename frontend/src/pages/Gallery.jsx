import React, { useEffect, useState } from 'react';
import { Award, CalendarDays, Image as ImageIcon, Video } from 'lucide-react';
import { fetchGalleryItems, fetchUpcomingProjects, fetchVideos, resolveMediaUrl } from '../api';

function formatDate(value) {
  if (!value) return 'Date to be announced';
  return new Date(`${value}T00:00:00`).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'long', year: 'numeric'
  });
}

export default function Gallery() {
  const [photos, setPhotos] = useState([]);
  const [videos, setVideos] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([fetchGalleryItems(), fetchVideos(), fetchUpcomingProjects()])
      .then(([photoData, videoData, projectData]) => {
        setPhotos(photoData);
        setVideos(videoData);
        setProjects(projectData);
      })
      .catch((err) => setError(err.message || 'Unable to load Media & Awards.'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <section style={{ background: '#0f172a', color: '#fff', padding: '4rem 0 3rem', textAlign: 'center' }}>
        <div className="container">
          <span className="badge badge-amber" style={{ marginBottom: '0.75rem' }}>
            <Award size={16} /> Media & Recognition
          </span>
          <h1 className="heading-xl" style={{ color: '#fff', marginBottom: '0.75rem' }}>Media & Awards</h1>
          <p className="subheading" style={{ color: '#94a3b8', margin: '0 auto' }}>
            Explore our latest photographs, videos and upcoming community projects.
          </p>
        </div>
      </section>

      <section className="section-padding" style={{ background: '#f8fafc' }}>
        <div className="container">
          {loading && <div style={{ textAlign: 'center', padding: '4rem', color: '#64748b' }}>Loading Media & Awards...</div>}
          {error && !loading && <div className="card" style={{ padding: '1.5rem', color: '#b91c1c' }}>{error}</div>}

          {!loading && !error && (
            <>
              <section style={{ marginBottom: '4rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.5rem' }}>
                  <ImageIcon size={24} color="#059669" />
                  <h2 style={{ margin: 0 }}>Photo Gallery</h2>
                </div>
                {photos.length === 0 ? (
                  <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>No photographs have been published yet.</div>
                ) : (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem' }}>
                    {photos.map((item) => (
                      <article key={item.id} className="card" style={{ overflow: 'hidden' }}>
                        <div style={{ height: '230px', overflow: 'hidden' }}>
                          <img src={resolveMediaUrl(item.image_url)} alt={item.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        </div>
                        <div style={{ padding: '1.25rem' }}>
                          <h3 style={{ margin: '0 0 0.5rem', color: '#0f172a' }}>{item.title}</h3>
                          {item.description && <p style={{ margin: 0, color: '#64748b', lineHeight: 1.6 }}>{item.description}</p>}
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </section>

              <section style={{ marginBottom: '4rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.5rem' }}>
                  <Video size={24} color="#059669" />
                  <h2 style={{ margin: 0 }}>Video Gallery</h2>
                </div>
                {videos.length === 0 ? (
                  <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>No videos have been published yet.</div>
                ) : (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem' }}>
                    {videos.map((item) => (
                      <article key={item.id} className="card" style={{ overflow: 'hidden' }}>
                        <video controls preload="metadata" style={{ width: '100%', display: 'block' }} src={resolveMediaUrl(item.video_url)} />
                        <div style={{ padding: '1.25rem' }}>
                          <h3 style={{ margin: '0 0 0.5rem', color: '#0f172a' }}>{item.title}</h3>
                          {item.description && <p style={{ margin: 0, color: '#64748b', lineHeight: 1.6 }}>{item.description}</p>}
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </section>

              <section>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.5rem' }}>
                  <CalendarDays size={24} color="#059669" />
                  <h2 style={{ margin: 0 }}>Upcoming Projects</h2>
                </div>
                {projects.length === 0 ? (
                  <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>Upcoming projects will be announced soon.</div>
                ) : (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
                    {projects.map((project) => (
                      <article key={project.id} className="card" style={{ overflow: 'hidden' }}>
                        {project.image_url && <img src={resolveMediaUrl(project.image_url)} alt={project.title} style={{ width: '100%', height: '220px', objectFit: 'cover' }} />}
                        <div style={{ padding: '1.4rem' }}>
                          <span className="badge badge-green" style={{ marginBottom: '0.75rem' }}>Upcoming</span>
                          <h3 style={{ margin: '0 0 0.6rem', color: '#0f172a' }}>{project.title}</h3>
                          {project.description && <p style={{ color: '#64748b', lineHeight: 1.6 }}>{project.description}</p>}
                          <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center', color: '#475569', fontWeight: 600 }}>
                            <CalendarDays size={16} /> {formatDate(project.expected_date)}
                          </div>
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </section>
            </>
          )}
        </div>
      </section>
    </div>
  );
}
