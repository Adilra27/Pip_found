import React, { useEffect, useState } from 'react';

import {
  CalendarDays,
  Image as ImageIcon,
  LogIn,
  LogOut,
  MessageSquare,
  RefreshCw,
  ShieldCheck,
  Trash2,
  Upload,
  Video,
  DollarSign,
  Users,
  Heart,
  Check,
  X,
  Award,
  Edit3,
  Mail,
  MailX,
  BarChart3,
  Eye,
  EyeOff,
  Send,
} from 'lucide-react';

import {
  clearAdminCredentials,
  createAdminCertificate,
  createAdminProject,
  createAdminTeamMember,
  deleteAdminCertificate,
  deleteAdminGalleryImage,
  deleteAdminProject,
  deleteAdminTeamMember,
  deleteAdminVideo,
  deleteContactInquiry,
  fetchAdminCertificates,
  fetchAdminGallery,
  fetchAdminProjects,
  fetchAdminStats,
  fetchAdminTeam,
  fetchAdminVideos,
  fetchAdminVolunteers,
  fetchAdminGalleryCategories,
  fetchAdminVideoCategories,
  fetchContactInquiries,
  fetchDonationsList,
  getAdminCredentials,
  resolveMediaUrl,
  setAdminCredentials,
  updateAdminCertificate,
  updateAdminProject,
  updateAdminVolunteerStatus,
  uploadAdminGalleryImage,
  uploadAdminVideo,
  deleteAdminVolunteer,
  resendAdminVolunteerCard,
  resendAdminVolunteerRejection,
  fetchAdminDonations,
  resendAdminDonationReceipt,
  fetchAdminImpact,
  updateAdminImpact,
  API_ORIGIN,
} from '../api';


// ============================================================
// EMPTY FORMS
// ============================================================

const emptyPhotoForm = {
  title: '',
  description: '',
  category: 'Photo Gallery',
  files: [],
};

const emptyVideoForm = {
  title: '',
  description: '',
  category: 'Video Gallery',
  files: [],
};

const emptyProjectForm = {
  title: '',
  description: '',
  expectedDate: '',
  file: null,
};

const emptyCertificateForm = {
  title: '',
  description: '',
  file: null,
};


// ============================================================
// SHARED COMPONENTS
// ============================================================

function ErrorMessage({ message }) {
  if (!message) {
    return null;
  }

  return (
    <div
      style={{
        padding: '0.85rem 1rem',
        marginBottom: '1rem',
        borderRadius: 8,
        background: '#fee2e2',
        color: '#991b1b',
      }}
    >
      {message}
    </div>
  );
}


function ManagerSection({
  title,
  icon,
  children,
}) {
  return (
    <section
      className="card"
      style={{
        padding: '1.5rem',
        marginBottom: '2rem',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '.6rem',
          marginBottom: '1.25rem',
        }}
      >
        {icon}
        <h2 style={{ margin: 0 }}>
          {title}
        </h2>
      </div>

      {children}
    </section>
  );
}


// ============================================================
// CATEGORY PICKER
// ============================================================

function CategoryPicker({
  value,
  onChange,
  options,
}) {
  const [isNew, setIsNew] = useState(false);
  const [newValue, setNewValue] = useState('');

  const selectStyle = {
    ...inputStyle,
    appearance: 'auto',
  };

  return (
    <div
      style={{
        display: 'grid',
        gap: '.5rem',
      }}
    >
      {!isNew ? (
        <select
          value={options.includes(value) ? value : ''}
          onChange={(e) => {
            if (e.target.value === '__new__') {
              setIsNew(true);
              setNewValue('');
              onChange('');
              return;
            }

            onChange(e.target.value);
          }}
          style={selectStyle}
        >
          <option value="" disabled>
            Select a category
          </option>

          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}

          <option value="__new__">
            + Add New / Other...
          </option>
        </select>
      ) : (
        <div style={{ display: 'grid', gap: '.5rem' }}>
          <input
            placeholder="Type a new category name"
            value={newValue}
            onChange={(e) => {
              setNewValue(e.target.value);
              onChange(e.target.value);
            }}
            style={inputStyle}
            autoFocus
          />
          <button
            type="button"
            className="btn"
            onClick={() => {
              setIsNew(false);
              setNewValue('');
              onChange(options[0] || '');
            }}
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}


// ============================================================
// ADMIN LOGIN
// ============================================================

function AdminLogin({ onLogin }) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();

    setError('');
    setLoading(true);

    try {
      setAdminCredentials(
        username,
        password
      );

      await fetchAdminStats();

      onLogin();
    } catch (err) {
      clearAdminCredentials();

      setError(
        err.code === 'ADMIN_AUTH_REQUIRED'
          ? 'Invalid admin username or password.'
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section
      className="section-padding"
      style={{
        background: '#f8fafc',
        minHeight: '70vh',
      }}
    >
      <div
        className="container"
        style={{ maxWidth: 460 }}
      >
        <div
          className="card"
          style={{ padding: '2rem' }}
        >
          <div
            style={{
              textAlign: 'center',
              marginBottom: '1.5rem',
            }}
          >
            <ShieldCheck
              size={42}
              color="#059669"
            />

            <h1
              style={{
                margin:
                  '0.75rem 0 0.4rem',
              }}
            >
              Admin Login
            </h1>

            <p
              style={{
                color: '#64748b',
                margin: 0,
              }}
            >
              Sign in to manage Piplad.
            </p>
          </div>

          <ErrorMessage
            message={error}
          />

          <form onSubmit={submit}>
            <label
              style={{
                display: 'block',
                fontWeight: 600,
                marginBottom: 6,
              }}
            >
              Username
            </label>

            <input
              value={username}
              onChange={(e) =>
                setUsername(e.target.value)
              }
              required
              style={inputStyle}
            />

            <label
              style={{
                display: 'block',
                fontWeight: 600,
                margin:
                  '1rem 0 6px',
              }}
            >
              Password
            </label>

            <input
              type="password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              required
              style={inputStyle}
            />

            <button
              className="btn"
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                marginTop: '1.25rem',
                background: '#059669',
                color: '#fff',
                border: 0,
              }}
            >
              <LogIn size={17} />

              {loading
                ? 'Signing in...'
                : 'Sign in'}
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}


// ============================================================
// PHOTO GALLERY
// ============================================================

function GalleryManager({ refreshAll }) {
  const [items, setItems] =
    useState([]);

  const [selectedIds, setSelectedIds] =
    useState([]);

  const [form, setForm] =
    useState(emptyPhotoForm);

  const [categories, setCategories] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState('');

  async function load() {
    setLoading(true);

    try {
      const [photoData, categoryData] =
        await Promise.all([
          fetchAdminGallery(),
          fetchAdminGalleryCategories(),
        ]);

      setItems(photoData);
      setSelectedIds([]);
      setCategories(categoryData);
      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(e) {
    e.preventDefault();

    setError('');

    if (form.files.length === 0) {
      setError(
        'Please select at least one image.'
      );
      return;
    }

    setSaving(true);

    try {
      await uploadAdminGalleryImage(
        form
      );

      setForm(emptyPhotoForm);

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  async function remove(id) {
    if (
      !window.confirm(
        'Delete this photograph?'
      )
    ) {
      return;
    }

    try {
      await deleteAdminGalleryImage(id);

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    }
  }

  function toggleSelected(id) {
    setSelectedIds((current) =>
      current.includes(id)
        ? current.filter((selectedId) => selectedId !== id)
        : [...current, id]
    );
  }

  function toggleAll() {
    setSelectedIds((current) =>
      current.length === items.length
        ? []
        : items.map((item) => item.id)
    );
  }

  async function removeSelected() {
    if (selectedIds.length === 0) return;

    if (
      !window.confirm(
        `Delete ${selectedIds.length} selected ${selectedIds.length === 1 ? 'photo' : 'photos'}?`
      )
    ) {
      return;
    }

    try {
      await Promise.all(
        selectedIds.map((id) => deleteAdminGalleryImage(id))
      );

      await load();
      refreshAll();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <ManagerSection
      title="Photo Gallery"
      icon={
        <ImageIcon size={22} />
      }
    >
      <ErrorMessage
        message={error}
      />

      {items.length > 0 && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '.75rem',
            flexWrap: 'wrap',
            marginBottom: '1rem',
          }}
        >
          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '.5rem',
              color: '#334155',
              fontWeight: 600,
            }}
          >
            <input
              type="checkbox"
              checked={selectedIds.length === items.length}
              onChange={toggleAll}
            />
            Select all photos
          </label>

          {selectedIds.length > 0 && (
            <button
              type="button"
              className="btn"
              onClick={removeSelected}
              style={dangerButton}
            >
              <Trash2 size={15} />
              Delete selected ({selectedIds.length})
            </button>
          )}
        </div>
      )}

      <form
        onSubmit={submit}
        style={formGridStyle}
      >
        <input
          placeholder="Event / album title"
          value={form.title}
          onChange={(e) =>
            setForm({
              ...form,
              title: e.target.value,
            })
          }
          required
          style={inputStyle}
        />

        <CategoryPicker
          value={form.category}
          options={categories}
          onChange={(category) =>
            setForm({
              ...form,
              category,
            })
          }
        />

        <input
          type="file"
          multiple
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={(e) =>
            setForm({
              ...form,
              files:
                Array.from(
                  e.target.files || []
                ),
            })
          }
          required
          style={inputStyle}
        />

        {form.files.length > 0 && (
          <p
            style={{
              color: '#475569',
              fontSize: '.9rem',
              margin: 0,
            }}
          >
            {form.files.length}
            {' '}
            {form.files.length === 1
              ? 'file'
              : 'files'}
            {' '}
            selected
          </p>
        )}

        <textarea
          placeholder="Description / caption (optional)"
          value={form.description}
          onChange={(e) =>
            setForm({
              ...form,
              description:
                e.target.value,
            })
          }
          style={textareaStyle}
        />

        <button
          className="btn"
          disabled={saving}
          style={primaryButton}
        >
          <Upload size={17} />

          {saving
            ? 'Uploading...'
            : 'Upload Photos'}
        </button>
      </form>

      <div style={managerGrid}>
        {loading ? (
          <p>Loading...</p>
        ) : items.length === 0 ? (
          <p
            style={{
              color: '#64748b',
            }}
          >
            No photos uploaded yet.
          </p>
        ) : (
          items.map((item) => (
            <article
              key={item.id}
              className="card"
              style={{
                overflow: 'hidden',
              }}
            >
              <label
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '.5rem',
                  padding: '.75rem 1rem 0',
                  color: '#334155',
                  fontWeight: 600,
                  fontSize: '.9rem',
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedIds.includes(item.id)}
                  onChange={() => toggleSelected(item.id)}
                />
                Select photo
              </label>

              <img
                src={resolveMediaUrl(
                  item.image_url
                )}
                alt={item.title}
                style={{
                  width: '100%',
                  height: 180,
                  objectFit: 'cover',
                }}
              />

              <div
                style={{
                  padding: '1rem',
                }}
              >
                {item.category && (
                  <span
                    style={{
                      display:
                        'inline-block',
                      background:
                        '#ecfdf5',
                      color: '#047857',
                      fontSize: '.75rem',
                      fontWeight: 700,
                      padding:
                        '.25rem .6rem',
                      borderRadius: 999,
                      marginBottom:
                        '.6rem',
                    }}
                  >
                    {item.category}
                  </span>
                )}

                <h3
                  style={{
                    margin: '0 0 .4rem',
                  }}
                >
                  {item.title}
                </h3>

                {item.description && (
                  <p
                    style={{
                      color: '#64748b',
                    }}
                  >
                    {item.description}
                  </p>
                )}

                <button
                  onClick={() =>
                    remove(item.id)
                  }
                  className="btn"
                  style={dangerButton}
                >
                  <Trash2 size={15} />
                  Delete
                </button>
              </div>
            </article>
          ))
        )}
      </div>
    </ManagerSection>
  );
}


// ============================================================
// VIDEO MANAGER
// ============================================================

function VideoManager({ refreshAll }) {
  const [items, setItems] =
    useState([]);

  const [form, setForm] =
    useState(emptyVideoForm);

  const [categories, setCategories] =
    useState([]);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState('');

  const [loading, setLoading] =
    useState(true);

  async function load() {
    setLoading(true);

    try {
      const [videoData, categoryData] =
        await Promise.all([
          fetchAdminVideos(),
          fetchAdminVideoCategories(),
        ]);

      setItems(videoData);
      setCategories(categoryData);
      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(e) {
    e.preventDefault();

    setError('');

    if (form.files.length === 0) {
      setError(
        'Please select at least one video.'
      );
      return;
    }

    setSaving(true);

    try {
      await uploadAdminVideo(
        form
      );

      setForm(emptyVideoForm);

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  async function remove(id) {
    if (
      !window.confirm(
        'Delete this video?'
      )
    ) {
      return;
    }

    try {
      await deleteAdminVideo(id);

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <ManagerSection
      title="Video Gallery"
      icon={<Video size={22} />}
    >
      <ErrorMessage
        message={error}
      />

      <form
        onSubmit={submit}
        style={formGridStyle}
      >
        <input
          placeholder="Video title"
          value={form.title}
          onChange={(e) =>
            setForm({
              ...form,
              title: e.target.value,
            })
          }
          required
          style={inputStyle}
        />

        <CategoryPicker
          value={form.category}
          options={categories}
          onChange={(category) =>
            setForm({
              ...form,
              category,
            })
          }
        />

        <input
          type="file"
          multiple
          accept="video/mp4,video/webm,video/quicktime,video/x-m4v"
          onChange={(e) =>
            setForm({
              ...form,
              files:
                Array.from(
                  e.target.files || []
                ),
            })
          }
          required
          style={inputStyle}
        />

        {form.files.length > 0 && (
          <p
            style={{
              color: '#475569',
              fontSize: '.9rem',
              margin: 0,
            }}
          >
            {form.files.length}
            {' '}
            {form.files.length === 1
              ? 'file'
              : 'files'}
            {' '}
            selected
          </p>
        )}

        <textarea
          placeholder="Description (optional)"
          value={form.description}
          onChange={(e) =>
            setForm({
              ...form,
              description:
                e.target.value,
            })
          }
          style={textareaStyle}
        />

        <button
          className="btn"
          disabled={saving}
          style={primaryButton}
        >
          <Upload size={17} />

          {saving
            ? 'Uploading...'
            : 'Upload Videos'}
        </button>
      </form>

      <p
        style={{
          color: '#64748b',
          fontSize: '.9rem',
        }}
      >
        Maximum video size: 100 MB.
        MP4 is recommended for browser
        compatibility.
      </p>

      <div style={managerGrid}>
        {loading ? (
          <p>Loading...</p>
        ) : items.length === 0 ? (
          <p
            style={{
              color: '#64748b',
            }}
          >
            No videos uploaded yet.
          </p>
        ) : (
          items.map((item) => (
            <article
              key={item.id}
              className="card"
              style={{
                overflow: 'hidden',
              }}
            >
              <video
                controls
                preload="metadata"
                src={resolveMediaUrl(
                  item.video_url
                )}
                style={{
                  width: '100%',
                  height: 180,
                  objectFit: 'cover',
                }}
              />

              <div
                style={{
                  padding: '1rem',
                }}
              >
                {item.category && (
                  <span
                    style={{
                      display:
                        'inline-block',
                      background:
                        '#ecfdf5',
                      color: '#047857',
                      fontSize: '.75rem',
                      fontWeight: 700,
                      padding:
                        '.25rem .6rem',
                      borderRadius: 999,
                      marginBottom:
                        '.6rem',
                    }}
                  >
                    {item.category}
                  </span>
                )}

                <h3
                  style={{
                    margin: '0 0 .4rem',
                  }}
                >
                  {item.title}
                </h3>

                {item.description && (
                  <p
                    style={{
                      color: '#64748b',
                    }}
                  >
                    {item.description}
                  </p>
                )}

                <button
                  onClick={() =>
                    remove(item.id)
                  }
                  className="btn"
                  style={dangerButton}
                >
                  <Trash2 size={15} />
                  Delete
                </button>
              </div>
            </article>
          ))
        )}
      </div>
    </ManagerSection>
  );
}


// ============================================================
// VOLUNTEER MANAGER
// ============================================================

function VolunteerManager() {
  const [items, setItems] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState('');

  async function load() {
    setLoading(true);

    try {
      setItems(
        await fetchAdminVolunteers()
      );

      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function setStatus(
    id,
    status
  ) {
    try {
      const updated =
        await updateAdminVolunteerStatus(
          id,
          status
        );

      setItems((current) =>
        current.map((item) =>
          item.id === id
            ? updated
            : item
        )
      );

      if (
        status === 'accepted' &&
        updated &&
        updated.volunteer_id &&
        updated.card_emailed === false &&
        !updated.card_sent_at
      ) {
        setError(
          'Volunteer accepted. The welcome card could not be emailed yet - use "Send card" to retry.'
        );
      } else {
        setError('');
      }
    } catch (e) {
      setError(e.message);
    }
  }

  async function resendCard(id) {
    try {
      const updated =
        await resendAdminVolunteerCard(id);

      setItems((current) =>
        current.map((item) =>
          item.id === id
            ? updated
            : item
        )
      );

      if (updated && updated.card_sent_at) {
        setError('');
      }
    } catch (e) {
      setError(e.message);
    }
  }

  async function resendRejection(id) {
    try {
      const updated =
        await resendAdminVolunteerRejection(id);

      setItems((current) =>
        current.map((item) =>
          item.id === id
            ? updated
            : item
        )
      );

      if (updated && updated.rejection_email_sent_at) {
        setError('');
      }
    } catch (e) {
      setError(e.message);
    }
  }

  async function remove(id) {
    if (
      !window.confirm(
        'Remove this volunteer application?'
      )
    ) {
      return;
    }

    try {
      await deleteAdminVolunteer(
        id
      );

      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <ManagerSection
      title="Volunteer Applications"
      icon={<Users size={22} />}
    >
      <ErrorMessage
        message={error}
      />

      {loading ? (
        <p>Loading...</p>
      ) : items.length === 0 ? (
        <p
          style={{
            color: '#64748b',
          }}
        >
          No volunteer applications yet.
        </p>
      ) : (
        <div
          style={{
            display: 'grid',
            gap: '1rem',
          }}
        >
          {items.map((item) => (
            <article
              key={item.id}
              className="card"
              style={{
                padding: '1rem',
                borderLeft:
                  `4px solid ${
                    item.status ===
                    'accepted'
                      ? '#059669'
                      : item.status ===
                        'rejected'
                      ? '#dc2626'
                      : '#d97706'
                  }`,
              }}
            >
              <div
                style={{
                  display: 'flex',
                  justifyContent:
                    'space-between',
                  gap: '1rem',
                  flexWrap: 'wrap',
                }}
              >
                <div>
                  <h3
                    style={{
                      margin: 0,
                    }}
                  >
                    {item.full_name}
                  </h3>

                  <p
                    style={{
                      color: '#475569',
                      margin:
                        '.35rem 0',
                    }}
                  >
                    {item.email}
                    {' · '}
                    {item.phone}
                  </p>

                  <p
                    style={{
                      color: '#64748b',
                      margin: 0,
                    }}
                  >
                    Interest:{' '}
                    {item.interest_area}
                  </p>

                  {item.about_yourself && (
                    <p
                      style={{
                        color: '#475569',
                        lineHeight: 1.5,
                      }}
                    >
                      {
                        item.about_yourself
                      }
                    </p>
                  )}

                  {item.volunteer_id && (
                    <p
                      style={{
                        color: '#059669',
                        marginTop: '.35rem',
                        fontWeight: 700,
                      }}
                    >
                      Volunteer ID:{' '}
                      {item.volunteer_id}
                    </p>
                  )}
                </div>

                <span
                  className="badge"
                  style={{
                    background:
                      item.status ===
                      'accepted'
                        ? '#d1fae5'
                        : item.status ===
                          'rejected'
                        ? '#fee2e2'
                        : '#fef3c7',
                    color:
                      item.status ===
                      'accepted'
                        ? '#065f46'
                        : item.status ===
                          'rejected'
                        ? '#991b1b'
                        : '#92400e',
                  }}
                >
                  {item.status}
                </span>

                {item.status ===
                  'accepted' && (
                  <span
                    className="badge"
                    style={{
                      display:
                        'inline-flex',
                      alignItems: 'center',
                      gap: '.3rem',
                      background: item.card_sent_at
                        ? '#d1fae5'
                        : '#fef3c7',
                      color: item.card_sent_at
                        ? '#065f46'
                        : '#92400e',
                    }}
                    title={
                      item.card_sent_at
                        ? `Welcome card sent on ${new Date(
                            item.card_sent_at
                          ).toLocaleString()}`
                        : 'Welcome card not emailed yet'
                    }
                  >
                    {item.card_sent_at ? (
                      <Mail size={13} />
                    ) : (
                      <MailX size={13} />
                    )}
                    {item.card_sent_at
                      ? 'Card emailed'
                      : 'Card not sent'}
                  </span>
                )}

                {item.status ===
                  'rejected' && (
                  <span
                    className="badge"
                    style={{
                      display:
                        'inline-flex',
                      alignItems: 'center',
                      gap: '.3rem',
                      background: item.rejection_email_sent_at
                        ? '#d1fae5'
                        : '#fef3c7',
                      color: item.rejection_email_sent_at
                        ? '#065f46'
                        : '#92400e',
                    }}
                    title={
                      item.rejection_email_sent_at
                        ? `Rejection email sent on ${new Date(
                            item.rejection_email_sent_at
                          ).toLocaleString()}`
                        : 'Rejection email not sent yet'
                    }
                  >
                    {item.rejection_email_sent_at ? (
                      <Mail size={13} />
                    ) : (
                      <MailX size={13} />
                    )}
                    {item.rejection_email_sent_at
                      ? 'Rejection emailed'
                      : 'Rejection not sent'}
                  </span>
                )}
              </div>

              <div
                style={{
                  display: 'flex',
                  gap: '.5rem',
                  flexWrap: 'wrap',
                  marginTop: '1rem',
                }}
              >
                <button
                  className="btn"
                  onClick={() =>
                    setStatus(
                      item.id,
                      'accepted'
                    )
                  }
                  style={primaryButton}
                >
                  <Check size={15} />
                  Accept
                </button>

                <button
                  className="btn"
                  onClick={() =>
                    setStatus(
                      item.id,
                      'rejected'
                    )
                  }
                  style={dangerButton}
                >
                  <X size={15} />
                  Reject
                </button>

                {item.status ===
                  'accepted' && (
                  <button
                    className="btn"
                    onClick={() =>
                      resendCard(item.id)
                    }
                    style={{
                      ...outlineButton,
                    }}
                  >
                    <Mail size={15} />
                    {item.card_sent_at
                      ? 'Resend card'
                      : 'Send card'}
                  </button>
                )}

                {item.status ===
                  'rejected' && (
                  <button
                    className="btn"
                    onClick={() =>
                      resendRejection(item.id)
                    }
                    style={{
                      ...outlineButton,
                    }}
                  >
                    <Mail size={15} />
                    {item.rejection_email_sent_at
                      ? 'Resend rejection email'
                      : 'Send rejection email'}
                  </button>
                )}

                <button
                  className="btn"
                  onClick={() =>
                    remove(item.id)
                  }
                  style={dangerButton}
                >
                  <Trash2 size={15} />
                  Remove
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </ManagerSection>
  );
}


// ============================================================
// DONATION MANAGER
// ============================================================

function DonationManager() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function load() {
    setLoading(true);
    try {
      setItems(await fetchAdminDonations());
      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function resendReceipt(id) {
    try {
      const updated = await resendAdminDonationReceipt(id);
      setItems((current) =>
        current.map((item) =>
          item.id === id ? updated : item
        )
      );
      setError('');
    } catch (e) {
      setError(e.message);
    }
  }

  const panelStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '1rem',
    flexWrap: 'wrap',
    marginBottom: '1rem',
  };

  const badgeStyle = (status) => {
    const completed = status === 'completed';
    return {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '.3rem',
      borderRadius: '9999px',
      padding: '.25rem .75rem',
      fontSize: '0.78rem',
      fontWeight: 700,
      background: completed ? '#d1fae5' : '#fef3c7',
      color: completed ? '#065f46' : '#92400e',
    };
  };

  return (
    <ManagerSection
      title="Donations"
      icon={<DollarSign size={22} />}
    >
      <ErrorMessage message={error} />

      {loading ? (
        <p>Loading...</p>
      ) : items.length === 0 ? (
        <p style={{ color: '#64748b' }}>
          No donation records yet.
        </p>
      ) : (
        <div style={{ display: 'grid', gap: '1rem' }}>
          {items.map((item) => (
            <article
              key={item.id}
              className="card"
              style={{ padding: '1rem' }}
            >
              <div style={panelStyle}>
                <div>
                  <h3 style={{ margin: 0 }}>
                    {item.donor_name}
                  </h3>
                  <p style={{ color: '#475569', margin: '.35rem 0' }}>
                    {item.donor_email}
                    {item.donor_phone ? ` · ${item.donor_phone}` : ''}
                  </p>
                  <p style={{ color: '#64748b', margin: 0 }}>
                    {item.razorpay_order_id || '—'} ·{' '}
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>

                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '.75rem',
                    flexWrap: 'wrap',
                  }}
                >
                  <span style={{ fontSize: '1.15rem', fontWeight: 800, color: '#059669' }}>
                    ₹{Number(item.amount).toLocaleString('en-IN')}
                  </span>

                  <span style={badgeStyle(item.status)}>
                    {item.status}
                  </span>

                  {item.status === 'completed' && (
                    <span
                      style={badgeStyle('completed')}
                      title={
                        item.receipt_sent_at
                          ? `Documents emailed on ${new Date(item.receipt_sent_at).toLocaleString()}`
                          : 'Certificates not emailed yet'
                      }
                    >
                      {item.receipt_sent_at ? (
                        <Mail size={13} />
                      ) : (
                        <MailX size={13} />
                      )}
                      {item.receipt_sent_at
                        ? 'Emailed'
                        : 'Not sent'}
                    </span>
                  )}
                </div>
              </div>

              {item.status === 'completed' && (
                <div style={{ display: 'flex', gap: '.5rem', flexWrap: 'wrap', marginTop: '.75rem' }}>
                  <button
                    className="btn"
                    onClick={() => resendReceipt(item.id)}
                    style={{ ...outlineButton }}
                  >
                    <Send size={15} />
                    {item.receipt_sent_at
                      ? 'Resend certificate & receipt'
                      : 'Send certificate & receipt'}
                  </button>
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </ManagerSection>
  );
}


// ============================================================
// PROJECT MANAGER
// ============================================================

function ProjectManager({
  refreshAll,
}) {
  const [items, setItems] =
    useState([]);

  const [form, setForm] =
    useState(emptyProjectForm);

  const [editingId, setEditingId] =
    useState(null);

  const [removeImage, setRemoveImage] =
    useState(false);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState('');

  const [loading, setLoading] =
    useState(true);

  async function load() {
    setLoading(true);

    try {
      setItems(
        await fetchAdminProjects()
      );
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function reset() {
    setForm(emptyProjectForm);
    setEditingId(null);
    setRemoveImage(false);
  }

  function edit(item) {
    setEditingId(item.id);

    setRemoveImage(false);

    setForm({
      title: item.title,
      description:
        item.description || '',
      expectedDate:
        item.expected_date || '',
      file: null,
    });

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }

  async function submit(e) {
    e.preventDefault();

    setError('');
    setSaving(true);

    try {
      if (editingId) {
        await updateAdminProject(
          editingId,
          {
            ...form,
            removeImage,
          }
        );
      } else {
        await createAdminProject(
          form
        );
      }

      reset();

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  async function remove(id) {
    if (
      !window.confirm(
        'Delete this upcoming project?'
      )
    ) {
      return;
    }

    try {
      await deleteAdminProject(id);

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <ManagerSection
      title="Upcoming Projects"
      icon={
        <CalendarDays size={22} />
      }
    >
      <ErrorMessage
        message={error}
      />

      <form
        onSubmit={submit}
        style={formGridStyle}
      >
        <input
          placeholder="Project title"
          value={form.title}
          onChange={(e) =>
            setForm({
              ...form,
              title: e.target.value,
            })
          }
          required
          style={inputStyle}
        />

        <input
          type="date"
          value={form.expectedDate}
          onChange={(e) =>
            setForm({
              ...form,
              expectedDate:
                e.target.value,
            })
          }
          style={inputStyle}
        />

        <textarea
          placeholder="Project description"
          value={form.description}
          onChange={(e) =>
            setForm({
              ...form,
              description:
                e.target.value,
            })
          }
          style={textareaStyle}
        />

        <input
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={(e) =>
            setForm({
              ...form,
              file:
                e.target.files?.[0] ||
                null,
            })
          }
          style={inputStyle}
        />

        {editingId && (
          <label
            style={{
              display: 'flex',
              gap: '.5rem',
              alignItems: 'center',
            }}
          >
            <input
              type="checkbox"
              checked={removeImage}
              onChange={(e) =>
                setRemoveImage(
                  e.target.checked
                )
              }
            />

            Remove current image
          </label>
        )}

        <div
          style={{
            display: 'flex',
            gap: '.75rem',
            flexWrap: 'wrap',
          }}
        >
          <button
            className="btn"
            disabled={saving}
            style={primaryButton}
          >
            {saving
              ? 'Saving...'
              : editingId
              ? 'Update Project'
              : 'Add Upcoming Project'}
          </button>

          {editingId && (
            <button
              type="button"
              className="btn"
              onClick={reset}
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      <div style={managerGrid}>
        {loading ? (
          <p>Loading...</p>
        ) : items.length === 0 ? (
          <p
            style={{
              color: '#64748b',
            }}
          >
            No upcoming projects yet.
          </p>
        ) : (
          items.map((item) => (
            <article
              key={item.id}
              className="card"
              style={{
                overflow: 'hidden',
              }}
            >
              {item.image_url && (
                <img
                  src={resolveMediaUrl(
                    item.image_url
                  )}
                  alt={item.title}
                  style={{
                    width: '100%',
                    height: 180,
                    objectFit: 'cover',
                  }}
                />
              )}

              <div
                style={{
                  padding: '1rem',
                }}
              >
                <span className="badge badge-green">
                  Upcoming
                </span>

                <h3
                  style={{
                    margin:
                      '.5rem 0',
                  }}
                >
                  {item.title}
                </h3>

                {item.description && (
                  <p
                    style={{
                      color: '#64748b',
                    }}
                  >
                    {item.description}
                  </p>
                )}

                <p
                  style={{
                    color: '#475569',
                  }}
                >
                  {item.expected_date
                    ? new Date(
                        `${item.expected_date}T00:00:00`
                      ).toLocaleDateString(
                        'en-IN'
                      )
                    : 'Date not set'}
                </p>

                <div
                  style={{
                    display: 'flex',
                    gap: '.5rem',
                  }}
                >
                  <button
                    className="btn"
                    onClick={() =>
                      edit(item)
                    }
                  >
                    Edit
                  </button>

                  <button
                    onClick={() =>
                      remove(item.id)
                    }
                    className="btn"
                    style={dangerButton}
                  >
                    <Trash2 size={15} />
                    Delete
                  </button>
                </div>
              </div>
            </article>
          ))
        )}
      </div>
    </ManagerSection>
  );
}


// ============================================================
// TEAM MANAGER
// ============================================================

function TeamManager({
  refreshAll,
}) {
  const [items, setItems] =
    useState([]);

  const [form, setForm] =
    useState({
      name: '',
      role: '',
      team:
        'Education & Skill Development',
      bio: '',
      file: null,
    });

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState('');

  const teamOptions = [
    'Education & Skill Development',
    'Healthcare',
    'Finance & Legal',
    'Environment & Modern Agriculture',
    'Social Welfare',
    'Culture & Tourism',
    'Sports & Yoga',
    'IT & Social Media',
    'General',
  ];

  async function load() {
    setLoading(true);

    try {
      setItems(
        await fetchAdminTeam()
      );

      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function resetForm() {
    setForm({
      name: '',
      role: '',
      team:
        'Education & Skill Development',
      bio: '',
      file: null,
    });
  }

  async function submit(e) {
    e.preventDefault();

    setError('');

    if (!form.name.trim()) {
      setError(
        'Please enter the team member name.'
      );
      return;
    }

    if (!form.team.trim()) {
      setError(
        'Please select a team.'
      );
      return;
    }

    setSaving(true);

    try {
      await createAdminTeamMember(
        form
      );

      resetForm();

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  async function remove(id) {
    if (
      !window.confirm(
        'Are you sure you want to remove this team member?'
      )
    ) {
      return;
    }

    try {
      await deleteAdminTeamMember(
        id
      );

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    }
  }

  const groupedItems =
    items.reduce(
      (groups, item) => {
        const team =
          item.team || 'General';

        if (!groups[team]) {
          groups[team] = [];
        }

        groups[team].push(item);

        return groups;
      },
      {}
    );

  return (
    <ManagerSection
      title="Team Management"
      icon={<Users size={22} />}
    >
      <ErrorMessage
        message={error}
      />

      <div
        style={{
          padding: '1rem',
          marginBottom: '1.5rem',
          borderRadius: 12,
          background: '#f0fdf4',
          border:
            '1px solid #bbf7d0',
          color: '#166534',
          lineHeight: 1.6,
        }}
      >
        Add and remove people who
        should appear on the public
        Our Team page. A profile photo
        is optional.
      </div>

      <form
        onSubmit={submit}
        style={formGridStyle}
      >
        <input
          placeholder="Team member name"
          value={form.name}
          onChange={(e) =>
            setForm({
              ...form,
              name: e.target.value,
            })
          }
          required
          style={inputStyle}
        />

        <input
          placeholder="Role / designation"
          value={form.role}
          onChange={(e) =>
            setForm({
              ...form,
              role: e.target.value,
            })
          }
          style={inputStyle}
        />

        <select
          value={form.team}
          onChange={(e) =>
            setForm({
              ...form,
              team: e.target.value,
            })
          }
          required
          style={inputStyle}
        >
          {teamOptions.map(
            (team) => (
              <option
                key={team}
                value={team}
              >
                {team}
              </option>
            )
          )}
        </select>

        <textarea
          placeholder="Short bio (optional)"
          value={form.bio}
          onChange={(e) =>
            setForm({
              ...form,
              bio: e.target.value,
            })
          }
          style={textareaStyle}
        />

        <input
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={(e) =>
            setForm({
              ...form,
              file:
                e.target.files?.[0] ||
                null,
            })
          }
          style={inputStyle}
        />

        <button
          className="btn"
          type="submit"
          disabled={saving}
          style={primaryButton}
        >
          <Users size={17} />

          {saving
            ? 'Adding Member...'
            : 'Add Team Member'}
        </button>
      </form>

      {loading ? (
        <p>
          Loading team members...
        </p>
      ) : items.length === 0 ? (
        <div
          style={{
            padding: '2rem',
            textAlign: 'center',
            border:
              '1px dashed #cbd5e1',
            borderRadius: 12,
            color: '#64748b',
          }}
        >
          No team members have
          been added yet.
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gap: '2rem',
          }}
        >
          {Object.entries(
            groupedItems
          ).map(
            ([team, teamMembers]) => (
              <div key={team}>
                <div
                  style={{
                    display: 'flex',
                    justifyContent:
                      'space-between',
                    alignItems: 'center',
                    marginBottom: '1rem',
                    paddingBottom: '.6rem',
                    borderBottom:
                      '1px solid #e2e8f0',
                  }}
                >
                  <h3
                    style={{
                      margin: 0,
                      color: '#0f172a',
                    }}
                  >
                    {team}
                  </h3>

                  <span className="badge badge-green">
                    {teamMembers.length}{' '}
                    {teamMembers.length ===
                    1
                      ? 'Member'
                      : 'Members'}
                  </span>
                </div>

                <div
                  style={managerGrid}
                >
                  {teamMembers.map(
                    (member) => (
                      <article
                        key={member.id}
                        className="card"
                        style={{
                          overflow:
                            'hidden',
                        }}
                      >
                        <div
                          style={{
                            display: 'flex',
                            justifyContent:
                              'center',
                            alignItems:
                              'center',
                            height: 190,
                            background:
                              'linear-gradient(135deg, #f0fdf4, #ecfccb)',
                            padding: '1rem',
                          }}
                        >
                          <img
                            src={
                              member.photo_url
                                ? resolveMediaUrl(
                                    member.photo_url
                                  )
                                : '/piplad-logo.jpg'
                            }
                            alt={
                              member.name
                            }
                            style={{
                              width: 140,
                              height: 140,
                              borderRadius:
                                '50%',
                              objectFit:
                                'cover',
                              border:
                                '4px solid #fff',
                              boxShadow:
                                '0 8px 20px rgba(0,0,0,.12)',
                            }}
                          />
                        </div>

                        <div
                          style={{
                            padding: '1rem',
                          }}
                        >
                          <h3
                            style={{
                              margin:
                                '0 0 .35rem',
                            }}
                          >
                            {member.name}
                          </h3>

                          {member.role && (
                            <p
                              style={{
                                margin:
                                  '0 0 .6rem',
                                color:
                                  '#059669',
                                fontWeight:
                                  600,
                                fontSize:
                                  '.9rem',
                              }}
                            >
                              {member.role}
                            </p>
                          )}

                          {member.bio && (
                            <p
                              style={{
                                color:
                                  '#64748b',
                                fontSize:
                                  '.85rem',
                                lineHeight:
                                  1.6,
                              }}
                            >
                              {member.bio}
                            </p>
                          )}

                          <button
                            type="button"
                            onClick={() =>
                              remove(
                                member.id
                              )
                            }
                            className="btn"
                            style={{
                              ...dangerButton,
                              marginTop:
                                '.5rem',
                            }}
                          >
                            <Trash2
                              size={15}
                            />
                            Remove Member
                          </button>
                        </div>
                      </article>
                    )
                  )}
                </div>
              </div>
            )
          )}
        </div>
      )}
    </ManagerSection>
  );
}


// ============================================================
// CERTIFICATE MANAGER
// ============================================================

function CertificateManager({ refreshAll }) {
  const [items, setItems] = useState([]);

  const [form, setForm] = useState(emptyCertificateForm);

  const [editingId, setEditingId] = useState(null);

  const [removeImage, setRemoveImage] = useState(false);

  const [saving, setSaving] = useState(false);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState('');

  async function load() {
    setLoading(true);

    try {
      setItems(
        await fetchAdminCertificates()
      );

      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function reset() {
    setForm(emptyCertificateForm);
    setEditingId(null);
    setRemoveImage(false);
  }

  function edit(item) {
    setEditingId(item.id);

    setRemoveImage(false);

    setForm({
      title: item.title,
      description: item.description || '',
      file: null,
    });

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }

  async function submit(e) {
    e.preventDefault();

    setError('');

    if (!form.title.trim()) {
      setError('Please enter a certificate title.');
      return;
    }

    setSaving(true);

    try {
      if (editingId) {
        await updateAdminCertificate(
          editingId,
          {
            ...form,
            removeImage,
          }
        );
      } else {
        await createAdminCertificate(form);
      }

      reset();

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  async function remove(id) {
    if (
      !window.confirm(
        'Delete this certificate?'
      )
    ) {
      return;
    }

    try {
      await deleteAdminCertificate(id);

      await load();

      refreshAll();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <ManagerSection
      title="Certificates"
      icon={<Award size={22} />}
    >
      <ErrorMessage
        message={error}
      />

      <form
        onSubmit={submit}
        style={formGridStyle}
      >
        <input
          placeholder="Certificate title"
          value={form.title}
          onChange={(e) =>
            setForm({
              ...form,
              title: e.target.value,
            })
          }
          required
          style={inputStyle}
        />

        <textarea
          placeholder="Description (optional)"
          value={form.description}
          onChange={(e) =>
            setForm({
              ...form,
              description: e.target.value,
            })
          }
          style={textareaStyle}
        />

        <input
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={(e) =>
            setForm({
              ...form,
              file: e.target.files?.[0] || null,
            })
          }
          style={inputStyle}
        />

        {editingId && (
          <label
            style={{
              display: 'flex',
              gap: '.5rem',
              alignItems: 'center',
            }}
          >
            <input
              type="checkbox"
              checked={removeImage}
              onChange={(e) =>
                setRemoveImage(e.target.checked)
              }
            />

            Remove current image
          </label>
        )}

        <div
          style={{
            display: 'flex',
            gap: '.75rem',
            flexWrap: 'wrap',
          }}
        >
          <button
            className="btn"
            disabled={saving}
            style={primaryButton}
          >
            <Upload size={17} />

            {saving
              ? 'Saving...'
              : editingId
              ? 'Update Certificate'
              : 'Add Certificate'}
          </button>

          {editingId && (
            <button
              type="button"
              className="btn"
              onClick={reset}
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      <div style={managerGrid}>
        {loading ? (
          <p>Loading...</p>
        ) : items.length === 0 ? (
          <p style={{ color: '#64748b' }}>
            No certificates added yet.
          </p>
        ) : (
          items.map((item) => (
            <article
              key={item.id}
              className="card"
              style={{ overflow: 'hidden' }}
            >
              {item.image_url ? (
                <img
                  src={resolveMediaUrl(item.image_url)}
                  alt={item.title}
                  style={{
                    width: '100%',
                    height: 180,
                    objectFit: 'cover',
                  }}
                />
              ) : (
                <div
                  style={{
                    height: 180,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: '#f1f5f9',
                  }}
                >
                  <Award size={40} color="#94a3b8" />
                </div>
              )}

              <div style={{ padding: '1rem' }}>
                <h3 style={{ margin: '0 0 .4rem' }}>
                  {item.title}
                </h3>

                {item.description && (
                  <p style={{ color: '#64748b' }}>
                    {item.description}
                  </p>
                )}

                <div
                  style={{
                    display: 'flex',
                    gap: '.5rem',
                    marginTop: '.75rem',
                  }}
                >
                  <button
                    className="btn"
                    onClick={() => edit(item)}
                  >
                    <Edit3 size={15} />
                    Edit
                  </button>

                  <button
                    onClick={() => remove(item.id)}
                    className="btn"
                    style={dangerButton}
                  >
                    <Trash2 size={15} />
                    Delete
                  </button>
                </div>
              </div>
            </article>
          ))
        )}
      </div>
    </ManagerSection>
  );
}


// ============================================================
// IMPACT METRICS MANAGER
// ============================================================

const categoryLabels = {
  people: 'People Impact',
  environmental: 'Environmental Impact',
  carbon: 'Verified Carbon Credits',
};

function ImpactManager() {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  async function load() {
    setLoading(true);

    try {
      setMetrics(await fetchAdminImpact());
      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function updateMetric(index, patch) {
    setMetrics((current) =>
      current.map((metric, i) =>
        i === index ? { ...metric, ...patch } : metric
      )
    );
  }

  async function save(e) {
    e.preventDefault();

    setError('');
    setSaving(true);

    try {
      const payload = metrics.map((metric) => ({
        value: Number(metric.value) || 0,
        is_published: Boolean(metric.is_published),
      }));

      setMetrics(await updateAdminImpact(payload));
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  const grouped = metrics.reduce((acc, metric) => {
    const key = metric.category || 'people';
    acc[key] = acc[key] || [];
    acc[key].push(metric);
    return acc;
  }, {});

  return (
    <ManagerSection
      title="Impact Metrics"
      icon={<BarChart3 size={22} />}
    >
      <ErrorMessage message={error} />

      <p style={{ color: '#64748b', lineHeight: 1.7, marginTop: 0 }}>
        These figures appear on the public Impact page and the
        "Impact at a Glance" section of the homepage. Change a value
        and save — the website updates automatically. Carbon credits
        should stay at 0 until formally verified.
      </p>

      {loading ? (
        <p>Loading impact metrics…</p>
      ) : metrics.length === 0 ? (
        <p style={{ color: '#64748b' }}>
          No impact metrics found.
        </p>
      ) : (
        <form onSubmit={save}>
          {Object.entries(grouped).map(([category, items]) => (
            <div
              key={category}
              style={{
                marginBottom: '1.5rem',
                padding: '1.25rem',
                border: '1px solid #e2e8f0',
                borderRadius: 12,
                background: '#f8fafc',
              }}
            >
              <h3
                style={{
                  margin: '0 0 1rem',
                  fontSize: '1rem',
                  color: '#0f172a',
                }}
              >
                {categoryLabels[category] || category}
              </h3>

              <div
                style={{
                  display: 'grid',
                  gap: '1rem',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                }}
              >
                {items.map((metric) => {
                  const idx = metrics.indexOf(metric);

                  return (
                    <div
                      key={metric.id}
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '.5rem',
                        padding: '1rem',
                        background: '#fff',
                        border: '1px solid #e2e8f0',
                        borderRadius: 10,
                      }}
                    >
                      <label style={{ fontWeight: 700, fontSize: '.88rem' }}>
                        {metric.metric_name}
                      </label>

                      {metric.description && (
                        <small style={{ color: '#64748b', lineHeight: 1.5 }}>
                          {metric.description}
                        </small>
                      )}

                      <div style={{ display: 'flex', gap: '.5rem', alignItems: 'center' }}>
                        <input
                          type="number"
                          min="0"
                          step="any"
                          value={metric.value}
                          onChange={(e) =>
                            updateMetric(idx, {
                              value: e.target.value,
                            })
                          }
                          style={{ ...inputStyle, flex: 1 }}
                        />
                        {metric.unit && (
                          <span
                            style={{
                              color: '#64748b',
                              fontSize: '.82rem',
                              fontWeight: 700,
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {metric.unit}
                          </span>
                        )}
                      </div>

                      <label
                        style={{
                          display: 'inline-flex',
                          gap: '.5rem',
                          alignItems: 'center',
                          fontSize: '.85rem',
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={Boolean(metric.is_published)}
                          onChange={(e) =>
                            updateMetric(idx, {
                              is_published: e.target.checked,
                            })
                          }
                        />
                        {metric.is_published
                          ? <><Eye size={15} /> Published</>
                          : <><EyeOff size={15} /> Hidden</>}
                      </label>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}

          <div
            style={{
              display: 'flex',
              gap: '.75rem',
              alignItems: 'center',
              flexWrap: 'wrap',
            }}
          >
            <button
              className="btn"
              disabled={saving}
              style={primaryButton}
            >
              <Upload size={17} />
              {saving ? 'Saving…' : 'Save Changes'}
            </button>

            {metrics.length > 0 && (
              <span style={{ color: '#64748b', fontSize: '.85rem' }}>
                Last updated:{' '}
                {metrics
                  .map((m) => m.last_updated)
                  .filter(Boolean)
                  .sort()
                  .slice(-1)[0]
                  ? new Date(
                      metrics
                        .map((m) => m.last_updated)
                        .filter(Boolean)
                        .sort()
                        .slice(-1)[0]
                    ).toLocaleDateString('en-IN', {
                      day: 'numeric',
                      month: 'short',
                      year: 'numeric',
                    })
                  : 'Never'}
              </span>
            )}
          </div>
        </form>
      )}
    </ManagerSection>
  );
}


// ============================================================
// MAIN ADMIN PAGE
// ============================================================

export default function Admin() {
  const [
    authenticated,
    setAuthenticated,
  ] = useState(
    Boolean(
      getAdminCredentials()
    )
  );

  const [tab, setTab] =
    useState('dashboard');

  const [stats, setStats] =
    useState(null);

  const [donations, setDonations] =
    useState([]);

  const [inquiries, setInquiries] =
    useState([]);

  const [error, setError] =
    useState('');

  async function loadDashboard() {
    try {
      const [
        s,
        d,
        i,
      ] = await Promise.all([
        fetchAdminStats(),
        fetchDonationsList(),
        fetchContactInquiries(),
      ]);

      setStats(s);
      setDonations(d);
      setInquiries(i);
      setError('');
    } catch (e) {
      if (
        e.code ===
        'ADMIN_AUTH_REQUIRED'
      ) {
        setAuthenticated(false);
        return;
      }

      setError(e.message);
    }
  }

  useEffect(() => {
    if (authenticated) {
      loadDashboard();
    }
  }, [authenticated]);

  async function deleteInquiry(id) {
    if (
      !window.confirm(
        'Delete this contact inquiry?'
      )
    ) {
      return;
    }

    try {
      await deleteContactInquiry(id);

      setInquiries((current) =>
        current.filter((item) => item.id !== id)
      );
    } catch (e) {
      setError(e.message);
    }
  }

  if (!authenticated) {
    return (
      <AdminLogin
        onLogin={() =>
          setAuthenticated(true)
        }
      />
    );
  }

  function logout() {
    clearAdminCredentials();
    setAuthenticated(false);
  }

  const tabs = [
    [
      'dashboard',
      'Dashboard',
    ],
    [
      'donations',
      'Donations',
    ],
    [
      'volunteers',
      'Volunteers',
    ],
    [
      'gallery',
      'Photos',
    ],
    [
      'videos',
      'Videos',
    ],
    [
      'projects',
      'Upcoming Projects',
    ],
    [
      'team',
      'Team Members',
    ],
    [
      'certificates',
      'Certificates',
    ],
    [
      'impact',
      'Impact Metrics',
    ],
  ];

  return (
    <div>
      {/* =====================================================
          HEADER
          ===================================================== */}

      <section
        style={{
          background: '#0f172a',
          color: '#fff',
          padding:
            '3rem 0 2rem',
        }}
      >
        <div
          className="container"
          style={{
            display: 'flex',
            justifyContent:
              'space-between',
            gap: '1rem',
            alignItems:
              'center',
            flexWrap: 'wrap',
          }}
        >
          <div>
            <span className="badge badge-green">
              <ShieldCheck
                size={16}
              />
              Admin
            </span>

            <h1
              style={{
                color: '#fff',
                margin:
                  '.6rem 0 0',
              }}
            >
              Piplad Management
            </h1>
          </div>

          <div className="admin-actions">
            <button
              className="btn admin-action-btn admin-refresh-btn"
              onClick={
                loadDashboard
              }
            >
              <RefreshCw
                size={16}
              />
              Refresh
            </button>

            <button
              className="btn admin-action-btn admin-logout-btn"
              onClick={logout}
            >
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </div>
      </section>

      {/* =====================================================
          CONTENT
          ===================================================== */}

      <section
        className="section-padding"
        style={{
          background: '#f8fafc',
        }}
      >
        <div className="container">

          {/* TABS */}

          <div
            style={{
              display: 'flex',
              gap: '.5rem',
              flexWrap: 'wrap',
              marginBottom: '2rem',
            }}
          >
            {tabs.map(
              ([id, label]) => (
                <button
                  key={id}
                  className="btn"
                  onClick={() =>
                    setTab(id)
                  }
                  style={
                    tab === id
                      ? primaryButton
                      : {}
                  }
                >
                  {label}
                </button>
              )
            )}

            <a
              href={`${API_ORIGIN}/admin`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn"
              style={{
                textDecoration:
                  'none',
                marginLeft: 'auto',
              }}
            >
              <ShieldCheck
                size={16}
              />
              SQL Admin
            </a>
          </div>

          <ErrorMessage
            message={error}
          />

          {/* =================================================
              DASHBOARD
              ================================================= */}

          {tab ===
            'dashboard' && (
            <>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns:
                    'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '1rem',
                  marginBottom:
                    '2rem',
                }}
              >
                <Stat
                  icon={
                    <DollarSign />
                  }
                  label="Total Raised"
                  value={`₹${Number(
                    stats?.total_donations ||
                      0
                  ).toLocaleString(
                    'en-IN'
                  )}`}
                />

                <Stat
                  icon={
                    <Users />
                  }
                  label="Total Donors"
                  value={
                    stats?.total_donors ||
                    0
                  }
                />

                <Stat
                  icon={
                    <Heart />
                  }
                  label="Active Causes"
                  value={
                    stats?.active_causes ||
                    0
                  }
                />

                <Stat
                  icon={
                    <MessageSquare />
                  }
                  label="Contact Inquiries"
                  value={
                    stats?.inquiries_count ||
                    0
                  }
                />
              </div>

              <div
                className="card"
                style={{
                  padding: '1.5rem',
                }}
              >
                <h2>
                  Content Management
                </h2>

                <p
                  style={{
                    color: '#64748b',
                    lineHeight: 1.7,
                  }}
                >
                  Use Photos, Videos,
                  Upcoming Projects,
                  Team Members and
                  Volunteers to manage
                  the corresponding
                  sections of the
                  website.
                </p>
              </div>
            </>
          )}

          {/* =================================================
              MANAGERS
              ================================================= */}

          {tab === 'gallery' && (
            <GalleryManager
              refreshAll={
                loadDashboard
              }
            />
          )}

          {tab === 'volunteers' && (
            <VolunteerManager />
          )}

          {tab === 'donations' && (
            <DonationManager />
          )}

          {tab === 'videos' && (
            <VideoManager
              refreshAll={
                loadDashboard
              }
            />
          )}

          {tab === 'projects' && (
            <ProjectManager
              refreshAll={
                loadDashboard
              }
            />
          )}

          {tab === 'team' && (
            <TeamManager
              refreshAll={
                loadDashboard
              }
            />
          )}

          {tab === 'certificates' && (
            <CertificateManager
              refreshAll={
                loadDashboard
              }
            />
          )}

          {tab === 'impact' && (
            <ImpactManager />
          )}

          {/* =================================================
              RECENT DONATIONS / INQUIRIES
              ================================================= */}

          {tab ===
            'dashboard' && (
            <div
              style={{
                marginTop: '2rem',
              }}
            >
              <div
                className="card"
                style={{
                  overflowX:
                    'auto',
                  marginBottom:
                    '2rem',
                }}
              >
                <h2
                  style={{
                    padding:
                      '0 1rem',
                  }}
                >
                  Recent Donations
                </h2>

                <table
                  style={
                    tableStyle
                  }
                >
                  <thead>
                    <tr>
                      <th
                        style={th}
                      >
                        Donor
                      </th>

                      <th
                        style={th}
                      >
                        Amount
                      </th>

                      <th
                        style={th}
                      >
                        Status
                      </th>

                      <th
                        style={th}
                      >
                        Date
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {donations
                      .slice(0, 10)
                      .map(
                        (d) => (
                          <tr
                            key={
                              d.id
                            }
                          >
                            <td
                              style={
                                td
                              }
                            >
                              {
                                d.donor_name
                              }
                            </td>

                            <td
                              style={
                                td
                              }
                            >
                              ₹
                              {Number(
                                d.amount
                              ).toLocaleString(
                                'en-IN'
                              )}
                            </td>

                            <td
                              style={
                                td
                              }
                            >
                              {
                                d.status
                              }
                            </td>

                            <td
                              style={
                                td
                              }
                            >
                              {new Date(
                                d.created_at
                              ).toLocaleDateString()}
                            </td>
                          </tr>
                        )
                      )}

                    {donations.length ===
                      0 && (
                      <tr>
                        <td
                          colSpan="4"
                          style={
                            td
                          }
                        >
                          No donation
                          records.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              <div
                className="card"
                style={{
                  overflowX:
                    'auto',
                }}
              >
                <h2
                  style={{
                    padding:
                      '0 1rem',
                  }}
                >
                  Recent Inquiries
                </h2>

                <table
                  style={
                    tableStyle
                  }
                >
                  <thead>
                    <tr>
                      <th
                        style={th}
                      >
                        Name
                      </th>

                      <th
                        style={th}
                      >
                        Email
                      </th>

                      <th
                        style={th}
                      >
                        Phone
                      </th>

                      <th
                        style={th}
                      >
                        Subject
                      </th>

                      <th
                        style={th}
                      >
                        Message
                      </th>

                      <th
                        style={th}
                      >
                        Date
                      </th>

                      <th
                        style={th}
                      >
                        Actions
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {inquiries
                      .slice(0, 20)
                      .map(
                        (i) => (
                          <tr
                            key={
                              i.id
                            }
                          >
                            <td
                              style={
                                td
                              }
                            >
                              {i.name}
                            </td>

                            <td
                              style={
                                td
                              }
                            >
                              {i.email}
                            </td>

                            <td
                              style={
                                td
                              }
                            >
                              {i.phone ||
                                '—'}
                            </td>

                            <td
                              style={
                                td
                              }
                            >
                              {i.subject ||
                                'General'}
                            </td>

                            <td
                              style={{
                                ...td,
                                minWidth: 220,
                              }}
                            >
                              {i.message}
                            </td>

                            <td
                              style={
                                td
                              }
                            >
                              {new Date(
                                i.created_at
                              ).toLocaleString()}
                            </td>

                            <td
                              style={td}
                            >
                              <button
                                onClick={() =>
                                  deleteInquiry(
                                    i.id
                                  )
                                }
                                className="btn"
                                style={dangerButton}
                              >
                                <Trash2
                                  size={15}
                                />
                                Delete
                              </button>
                            </td>
                          </tr>
                        )
                      )}

                    {inquiries.length ===
                      0 && (
                      <tr>
                        <td
                          colSpan="7"
                          style={
                            td
                          }
                        >
                          No inquiries.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}


// ============================================================
// STATS
// ============================================================

function Stat({
  icon,
  label,
  value,
}) {
  return (
    <div
      className="card"
      style={{
        padding: '1.25rem',
        display: 'flex',
        gap: '.8rem',
        alignItems: 'center',
      }}
    >
      {React.cloneElement(
        icon,
        {
          size: 22,
          color: '#059669',
        }
      )}

      <div>
        <div
          style={{
            color: '#64748b',
            fontSize: '.85rem',
          }}
        >
          {label}
        </div>

        <strong
          style={{
            fontSize: '1.35rem',
            color: '#0f172a',
          }}
        >
          {value}
        </strong>
      </div>
    </div>
  );
}


// ============================================================
// STYLES
// ============================================================

const inputStyle = {
  width: '100%',
  boxSizing: 'border-box',
  padding: '0.75rem',
  border:
    '1px solid #cbd5e1',
  borderRadius: 8,
  background: '#fff',
};

const textareaStyle = {
  ...inputStyle,
  minHeight: 100,
  resize: 'vertical',
};

const formGridStyle = {
  display: 'grid',
  gap: '.9rem',
  marginBottom: '2rem',
};

const managerGrid = {
  display: 'grid',
  gridTemplateColumns:
    'repeat(auto-fit, minmax(260px, 1fr))',
  gap: '1.25rem',
};

const primaryButton = {
  background: '#059669',
  color: '#fff',
  border: 0,
};

const dangerButton = {
  background: '#fff',
  color: '#b91c1c',
  border:
    '1px solid #fecaca',
};

const outlineButton = {
  background: '#fff',
  color: '#0f172a',
  border:
    '1px solid #cbd5e1',
};

const tableStyle = {
  width: '100%',
  borderCollapse:
    'collapse',
  textAlign: 'left',
};

const th = {
  padding: '1rem',
  background: '#f1f5f9',
  color: '#334155',
};

const td = {
  padding: '1rem',
  borderBottom:
    '1px solid #e2e8f0',
  color: '#475569',
};
