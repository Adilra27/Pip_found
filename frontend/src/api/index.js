export const API_BASE_URL = (
  import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
).replace(/\/$/, '');

export const API_ORIGIN = API_BASE_URL.replace(/\/api$/, '');

export function resolveMediaUrl(url) {
  if (!url) return '';

  if (/^https?:\/\//i.test(url)) {
    return url;
  }

  if (url.startsWith('/')) {
    return `${API_ORIGIN}${url}`;
  }

  return `${API_ORIGIN}/${url}`;
}


// ============================================================
// PUBLIC API
// ============================================================

export async function fetchCauses() {
  const res = await fetch(`${API_BASE_URL}/causes`);

  if (!res.ok) {
    throw new Error('Failed to fetch causes');
  }

  return res.json();
}

export async function fetchCauseById(id) {
  const res = await fetch(`${API_BASE_URL}/causes/${id}`);

  if (!res.ok) {
    throw new Error('Failed to fetch cause details');
  }

  return res.json();
}

export async function submitContact(data) {
  const res = await fetch(`${API_BASE_URL}/contact`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error('Failed to submit contact form');
  }

  return res.json();
}


// ============================================================
// DONATIONS / RAZORPAY
// ============================================================

export async function createRazorpayOrder(data) {
  const res = await fetch(`${API_BASE_URL}/donate/create-order`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error('Failed to create donation order');
  }

  return res.json();
}

export async function verifyPayment(data) {
  const res = await fetch(`${API_BASE_URL}/donate/verify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    throw new Error('Failed to verify payment');
  }

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
    JSON.stringify({
      username,
      password,
    })
  );
}

export function clearAdminCredentials() {
  sessionStorage.removeItem(ADMIN_STORAGE_KEY);
}


// ============================================================
// ADMIN FETCH HELPER
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
    `Basic ${btoa(
      `${credentials.username}:${credentials.password}`
    )}`
  );

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
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
      // Keep the generic error message.
    }

    throw new Error(message);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}


// ============================================================
// ADMIN DASHBOARD
// ============================================================

export async function fetchAdminStats() {
  return adminFetch('/admin/stats');
}


// ============================================================
// ADMIN PHOTO GALLERY
// ============================================================

export async function fetchAdminGallery() {
  return adminFetch('/admin/gallery');
}

export async function uploadAdminGalleryImage({
  title,
  description,
  file,
}) {
  const form = new FormData();

  form.append('title', title);

  if (description) {
    form.append('description', description);
  }

  form.append('file', file);

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
// ADMIN VIDEO GALLERY
// ============================================================

export async function fetchAdminVideos() {
  return adminFetch('/admin/videos');
}

export async function uploadAdminVideo({
  title,
  description,
  file,
}) {
  const form = new FormData();

  form.append('title', title);

  if (description) {
    form.append('description', description);
  }

  form.append('file', file);

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
// ADMIN UPCOMING PROJECTS
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

  form.append(
    'remove_image',
    String(Boolean(removeImage))
  );

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

export async function fetchUpcomingProjects() {
  const res = await fetch(
    `${API_BASE_URL}/projects?status=upcoming`
  );

  if (!res.ok) {
    throw new Error('Failed to fetch upcoming projects');
  }

  return res.json();
}


// ============================================================
// PUBLIC DONATIONS
// ============================================================

export async function fetchDonationsList() {
  const res = await fetch(`${API_BASE_URL}/donate`);

  if (!res.ok) {
    throw new Error('Failed to fetch donations');
  }

  return res.json();
}


// ============================================================
// PUBLIC CONTACT / INQUIRIES
// ============================================================

export async function fetchContactInquiries() {
  const res = await fetch(`${API_BASE_URL}/contact`);

  if (!res.ok) {
    throw new Error('Failed to fetch inquiries');
  }

  return res.json();
}


// ============================================================
// PUBLIC TEAM
// ============================================================

export async function fetchTeam() {
  const res = await fetch(`${API_BASE_URL}/team`);

  if (!res.ok) {
    throw new Error('Failed to fetch team');
  }

  return res.json();
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