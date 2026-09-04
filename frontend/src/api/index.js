export const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api').replace(/\/$/, '');

export const API_ORIGIN = API_BASE_URL.replace(/\/api$/, '');

export function resolveMediaUrl(url) {
  if (!url) return '';
  if (/^https?:\/\//i.test(url)) return url;
  if (url.startsWith('/')) return `${API_ORIGIN}${url}`;
  return `${API_ORIGIN}/${url}`;
}

export async function fetchCauses() {
  const res = await fetch(`${API_BASE_URL}/causes`);
  if (!res.ok) throw new Error('Failed to fetch causes');
  return res.json();
}

export async function fetchCauseById(id) {
  const res = await fetch(`${API_BASE_URL}/causes/${id}`);
  if (!res.ok) throw new Error('Failed to fetch cause details');
  return res.json();
}

export async function submitContact(data) {
  const res = await fetch(`${API_BASE_URL}/contact`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!res.ok) throw new Error('Failed to submit contact form');
  return res.json();
}

export async function submitVolunteerApplication(data) {
  const form = new FormData();

  form.append('full_name', data.full_name || '');
  form.append('email', data.email || '');
  form.append('phone', data.phone || '');
  form.append('interest_area', data.interest_area || '');

  if (data.about_yourself) {
    form.append('about_yourself', data.about_yourself);
  }

  if (data.profile_pic) {
    form.append('profile_pic', data.profile_pic);
  }

  const res = await fetch(`${API_BASE_URL}/volunteers`, {
    method: 'POST',
    body: form,
  });

  if (!res.ok) {
    const response = await res.json().catch(() => ({}));
    throw new Error(response.detail || 'Failed to submit volunteer application');
  }

  return res.json();
}

export async function createRazorpayOrder(data) {
  const res = await fetch(`${API_BASE_URL}/donate/create-order`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!res.ok) throw new Error('Failed to create donation order');
  return res.json();
}

export async function verifyPayment(data) {
  const res = await fetch(`${API_BASE_URL}/donate/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!res.ok) throw new Error('Failed to verify payment');
  return res.json();
}


// ============================================================
// ADMIN AUTHENTICATION
// ============================================================

const ADMIN_STORAGE_KEY = 'pwf_admin_basic_auth';

export function getAdminCredentials() {
  try {
    const raw = sessionStorage.getItem(ADMIN_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setAdminCredentials(username, password) {
  sessionStorage.setItem(
    ADMIN_STORAGE_KEY,
    JSON.stringify({ username, password })
  );
}

export function clearAdminCredentials() {
  sessionStorage.removeItem(ADMIN_STORAGE_KEY);
}


// ============================================================
// ADMIN REQUEST HELPER
// ============================================================

async function adminFetch(path, options = {}) {
  const credentials = getAdminCredentials();

  if (!credentials) {
    const error = new Error('ADMIN_AUTH_REQUIRED');
    error.code = 'ADMIN_AUTH_REQUIRED';
    throw error;
  }

  const headers = new Headers(options.headers || {});

  headers.set(
    'Authorization',
    `Basic ${btoa(`${credentials.username}:${credentials.password}`)}`
  );

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    cache: 'no-store',
    headers,
  });

  if (response.status === 401) {
    clearAdminCredentials();

    const error = new Error('ADMIN_AUTH_REQUIRED');
    error.code = 'ADMIN_AUTH_REQUIRED';
    throw error;
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`;

    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // Keep the generic message.
    }

    throw new Error(message);
  }

  if (response.status === 204) return null;

  return response.json();
}


// ============================================================
// ADMIN DASHBOARD
// ============================================================

export async function fetchAdminStats() {
  return adminFetch('/admin/stats');
}

export async function fetchAdminVolunteers() {
  return adminFetch('/admin/volunteers');
}

export async function updateAdminVolunteerStatus(id, status) {
  return adminFetch(`/admin/volunteers/${id}/status?status_value=${encodeURIComponent(status)}`, {
    method: 'PATCH',
  });
}

export async function deleteAdminVolunteer(id) {
  return adminFetch(`/admin/volunteers/${id}`, { method: 'DELETE' });
}

export async function resendAdminVolunteerCard(id) {
  return adminFetch(`/admin/volunteers/${id}/resend-card`, {
    method: 'POST',
  });
}


// ============================================================
// ADMIN GALLERY
// ============================================================

export async function fetchAdminGallery() {
  return adminFetch('/admin/gallery');
}

export async function fetchAdminGalleryCategories() {
  return adminFetch('/admin/gallery/categories');
}

export async function uploadAdminGalleryImage({
  title,
  description,
  category,
  files,
}) {
  const form = new FormData();

  form.append('title', title);

  if (category) {
    form.append('category', category);
  }

  if (description) {
    form.append('description', description);
  }

  for (const file of files) {
    form.append('files', file);
  }

  return adminFetch('/admin/gallery/upload', {
    method: 'POST',
    body: form,
  });
}

export async function deleteAdminGalleryImage(id) {
  return adminFetch(`/admin/gallery/${id}`, {
    method: 'DELETE',
  });
}


// ============================================================
// ADMIN VIDEOS
// ============================================================

export async function fetchAdminVideos() {
  return adminFetch('/admin/videos');
}

export async function fetchAdminVideoCategories() {
  return adminFetch('/admin/videos/categories');
}

export async function uploadAdminVideo({
  title,
  description,
  category,
  files,
}) {
  const form = new FormData();

  form.append('title', title);

  if (category) {
    form.append('category', category);
  }

  if (description) {
    form.append('description', description);
  }

  for (const file of files) {
    form.append('files', file);
  }

  return adminFetch('/admin/videos/upload', {
    method: 'POST',
    body: form,
  });
}

export async function deleteAdminVideo(id) {
  return adminFetch(`/admin/videos/${id}`, {
    method: 'DELETE',
  });
}


// ============================================================
// ADMIN PROJECTS
// ============================================================

export async function fetchAdminProjects() {
  return adminFetch('/admin/projects');
}

export async function createAdminProject({
  title,
  description,
  expectedDate,
  file,
}) {
  const form = new FormData();

  form.append('title', title);

  if (description) {
    form.append('description', description);
  }

  if (expectedDate) {
    form.append('expected_date', expectedDate);
  }

  if (file) {
    form.append('file', file);
  }

  return adminFetch('/admin/projects', {
    method: 'POST',
    body: form,
  });
}

export async function updateAdminProject(
  id,
  {
    title,
    description,
    expectedDate,
    file,
    removeImage,
  }
) {
  const form = new FormData();

  form.append('title', title);

  if (description) {
    form.append('description', description);
  }

  if (expectedDate) {
    form.append('expected_date', expectedDate);
  }

  form.append('remove_image', String(Boolean(removeImage)));

  if (file) {
    form.append('file', file);
  }

  return adminFetch(`/admin/projects/${id}`, {
    method: 'PUT',
    body: form,
  });
}

export async function deleteAdminProject(id) {
  return adminFetch(`/admin/projects/${id}`, {
    method: 'DELETE',
  });
}


// ============================================================
// PUBLIC GALLERY
// ============================================================

export async function fetchGalleryItems() {
  const res = await fetch(`${API_BASE_URL}/gallery`);

  if (!res.ok) {
    throw new Error('Failed to fetch gallery items');
  }

  return res.json();
}


// ============================================================
// PUBLIC VIDEOS
// ============================================================

export async function fetchVideos() {
  const res = await fetch(`${API_BASE_URL}/videos`);

  if (!res.ok) {
    throw new Error('Failed to fetch videos');
  }

  return res.json();
}


// ============================================================
// PUBLIC UPCOMING PROJECTS
// ============================================================

export async function fetchCertificates() {
  const res = await fetch(`${API_BASE_URL}/certificates`);
  if (!res.ok) throw new Error('Failed to fetch certificates');
  return res.json();
}

export async function fetchUpcomingProjects() {
  const res = await fetch(`${API_BASE_URL}/projects?status=upcoming`);

  if (!res.ok) {
    throw new Error('Failed to fetch upcoming projects');
  }

  return res.json();
}


// ============================================================
// DONATIONS
// ============================================================

export async function fetchDonationsList() {
  const res = await fetch(`${API_BASE_URL}/donate`);

  if (!res.ok) {
    throw new Error('Failed to fetch donations');
  }

  return res.json();
}


// ============================================================
// CONTACT
// ============================================================

export async function fetchContactInquiries() {
  return adminFetch('/contact');
}

// ============================================================
// TEAM
// ============================================================

export async function fetchTeam() {
  const res = await fetch(`${API_BASE_URL}/team`);

  if (!res.ok) {
    throw new Error('Failed to fetch team');
  }

  return res.json();
}


// ============================================================
// ADMIN TEAM
// ============================================================

export async function fetchAdminTeam() {
  return adminFetch('/admin/team');
}
export async function createAdminTeamMember({
  name,
  role,
  team,
  bio,
  file,
}) {
  const form = new FormData();

  form.append('name', name);

  if (role) {
    form.append('role', role);
  }

  form.append(
    'team',
    team || 'General'
  );

  if (bio) {
    form.append('bio', bio);
  }

  // Photo is optional.
  if (file) {
    form.append('file', file);
  }

  return adminFetch('/admin/team', {
    method: 'POST',
    body: form,
  });
}


export async function deleteAdminTeamMember(id) {
  return adminFetch(`/admin/team/${id}`, {
    method: 'DELETE',
  });
}

// ============================================================
// ADMIN CERTIFICATES
// ============================================================

export async function fetchAdminCertificates() {
  return adminFetch('/admin/certificates');
}

export async function createAdminCertificate({
  title,
  description,
  file,
}) {
  const form = new FormData();

  form.append('title', title);

  if (description) {
    form.append('description', description);
  }

  if (file) {
    form.append('file', file);
  }

  return adminFetch('/admin/certificates', {
    method: 'POST',
    body: form,
  });
}

export async function updateAdminCertificate(
  id,
  {
    title,
    description,
    file,
    removeImage,
  }
) {
  const form = new FormData();

  form.append('title', title);

  if (description) {
    form.append('description', description);
  }

  form.append('remove_image', String(Boolean(removeImage)));

  if (file) {
    form.append('file', file);
  }

  return adminFetch(`/admin/certificates/${id}`, {
    method: 'PUT',
    body: form,
  });
}

export async function deleteAdminCertificate(id) {
  return adminFetch(`/admin/certificates/${id}`, {
    method: 'DELETE',
  });
}

// ============================================================
// CONTACT INQUIRIES
// ============================================================

export async function deleteContactInquiry(id) {
  return adminFetch(`/contact/${id}`, {
    method: 'DELETE',
  });
}

// ============================================================
// PUBLIC BLOG
// ============================================================

export async function fetchBlogPosts() {
  const res = await fetch(`${API_BASE_URL}/blog`);

  if (!res.ok) {
    throw new Error('Failed to fetch blog posts');
  }

  return res.json();
}

export async function fetchBlogPost(id) {
  const res = await fetch(`${API_BASE_URL}/blog/${id}`);

  if (!res.ok) {
    if (res.status === 404) {
      throw new Error('Blog post not found');
    }

    throw new Error('Failed to fetch blog post');
  }

  return res.json();
}
