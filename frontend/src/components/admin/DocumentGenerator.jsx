import React, { useCallback, useEffect, useState } from 'react';
import {
  Award, Download, Eye, FileImage, Loader2, Plus, RefreshCw,
  ShieldCheck, ShieldX, UserCheck, FileText, BadgeCheck,
} from 'lucide-react';
import {
  downloadAdminCertificate,
  downloadAdminVolunteerCard,
  fetchGeneratedCertificates,
  fetchGeneratedOptions,
  fetchGeneratedVolunteers,
  generateAdminCertificate,
  generateAdminVolunteerCard,
  revokeAdminCertificate,
  revokeAdminVolunteerCard,
  resolveMediaUrl,
} from '../../api';

const inputStyle = {
  width: '100%',
  boxSizing: 'border-box',
  padding: '0.75rem',
  border: '1px solid #cbd5e1',
  borderRadius: 8,
  background: '#fff',
};

const formGridStyle = {
  display: 'grid',
  gap: '.9rem',
  marginBottom: '2rem',
};

const primaryButton = { background: '#059669', color: '#fff', border: 0 };
const dangerButton = { background: '#fff', color: '#b91c1c', border: '1px solid #fecaca' };
const outlineButton = { background: '#fff', color: '#0f172a', border: '1px solid #cbd5e1' };
const tableStyle = { width: '100%', borderCollapse: 'collapse', textAlign: 'left' };
const th = { padding: '.7rem', background: '#f1f5f9', color: '#334155', fontSize: '.8rem' };
const td = { padding: '.7rem', borderBottom: '1px solid #e2e8f0', color: '#475569' };

const TYPE_FIELDS = {
  appreciation: [
    ['first_name', 'First Name', 'text', true],
    ['last_name', 'Last Name', 'text', false],
    ['recipient_email', 'Recipient Email', 'email', false],
    ['program_name', 'Program / Event', 'text', false],
    ['issue_date', 'Issue Date', 'date', false],
    ['certificate_number', 'Certificate Number (blank = auto)', 'text', false],
  ],
  internship: [
    ['first_name', 'First Name', 'text', true],
    ['last_name', 'Last Name', 'text', false],
    ['recipient_email', 'Recipient Email', 'email', false],
    ['program_name', 'Program / Internship', 'text', true],
    ['starting_date', 'Starting Date', 'date', true],
    ['end_date', 'End Date', 'date', true],
    ['issue_date', 'Issue Date', 'date', false],
    ['certificate_number', 'Certificate Number (blank = auto)', 'text', false],
  ],
  completion: [
    ['first_name', 'First Name', 'text', true],
    ['last_name', 'Last Name', 'text', false],
    ['recipient_email', 'Recipient Email', 'email', false],
    ['program_name', 'Program / Competition', 'text', true],
    ['organisation_name', 'Organisation Name', 'text', false],
    ['competition_date', 'Competition Date', 'date', false],
    ['competition_location', 'Competition Location', 'text', false],
    ['issue_date', 'Issue Date', 'date', false],
    ['certificate_number', 'Certificate Number (blank = auto)', 'text', false],
  ],
  participation: [
    ['first_name', 'First Name', 'text', true],
    ['last_name', 'Last Name', 'text', false],
    ['recipient_email', 'Recipient Email', 'email', false],
    ['program_name', 'Program / Event', 'text', true],
    ['competition_date', 'Competition Date', 'date', false],
    ['competition_location', 'Competition Location', 'text', false],
    ['issue_date', 'Issue Date', 'date', false],
    ['certificate_number', 'Certificate Number (blank = auto)', 'text', false],
  ],
};

const TYPE_LABELS = {
  appreciation: 'Certificate of Appreciation',
  completion: 'Certificate of Completion',
  internship: 'Certificate of Internship',
  participation: 'Certificate of Participation',
};

function SectionTitle({ icon: Icon, children }) {
  return (
    <h2
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '.5rem',
        marginBottom: '1rem',
      }}
    >
      <Icon size={20} />
      {children}
    </h2>
  );
}

function Empty({ children }) {
  return (
    <p style={{ color: '#94a3b8', textAlign: 'center', padding: '2rem 0' }}>
      {children}
    </p>
  );
}

function CertificateTab({ types }) {
  const [form, setForm] = useState({
    certificate_type: 'appreciation',
    first_name: '',
    last_name: '',
    recipient_email: '',
    program_name: '',
    starting_date: '',
    end_date: '',
    organisation_name: '',
    competition_date: '',
    competition_location: '',
    issue_date: '',
    certificate_number: '',
  });
  const [typeFilter, setTypeFilter] = useState('');
  const [search, setSearch] = useState('');
  const [list, setList] = useState({ items: [], total: 0, page: 1, page_size: 20 });
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchGeneratedCertificates({
        typeLabel: typeFilter,
        search,
        page: list.page,
        pageSize: 20,
      });
      setList(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [typeFilter, search, list.page]);

  useEffect(() => {
    load();
  }, [typeFilter, search, list.page, load]);

  function setField(key, value) {
    setForm({ ...form, [key]: value });
  }

  async function handleGenerate() {
    setError('');
    setInfo('');
    if (!form.first_name.trim()) {
      setError('First name is required.');
      return;
    }
    if (
      form.end_date &&
      form.starting_date &&
      form.end_date < form.starting_date
    ) {
      setError('Internship end date cannot be before the starting date.');
      return;
    }
    setGenerating(true);
    try {
      const cert = await generateAdminCertificate({
        certificate_type: form.certificate_type,
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim() || null,
        recipient_email: form.recipient_email.trim() || null,
        program_name: form.program_name.trim() || null,
        starting_date: form.starting_date || null,
        end_date: form.end_date || null,
        organisation_name: form.organisation_name.trim() || null,
        competition_date: form.competition_date || null,
        competition_location: form.competition_location.trim() || null,
        issue_date: form.issue_date || null,
        certificate_number: form.certificate_number.trim() || null,
      });
      setInfo(
        `Certificate ${cert.certificate_number} generated for ${cert.recipient_name}.`
      );
      setForm({ ...form, certificate_number: '' });
      setList({ ...list, page: 1 });
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  }

  async function handleRevoke(id) {
    if (!window.confirm('Revoke this certificate? It will no longer verify.')) return;
    try {
      await revokeAdminCertificate(id);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div style={{ display: 'grid', gap: '1.5rem' }}>
      <div className="card" style={{ padding: '1rem' }}>
        <SectionTitle icon={Award}>Generate Official Certificate</SectionTitle>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '.9rem', marginBottom: '1rem' }}>
          {(types || []).map((t) => (
            <label
              key={t.type}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '.5rem',
                border: form.certificate_type === t.type ? '1px solid #059669' : '1px solid #cbd5e1',
                borderRadius: 10,
                padding: '.6rem .8rem',
                cursor: 'pointer',
                color: form.certificate_type === t.type ? '#047857' : '#334155',
                background: form.certificate_type === t.type ? '#ecfdf5' : '#fff',
              }}
            >
              <input
                type="radio"
                name="cert-type"
                checked={form.certificate_type === t.type}
                onChange={() => setField('certificate_type', t.type)}
              />
              {TYPE_LABELS[t.type] || t.label}
              {!t.image_available && ' (missing template)'}
            </label>
          ))}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleGenerate();
          }}
          style={formGridStyle}
        >
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: '.75rem' }}>
            {(TYPE_FIELDS[form.certificate_type] || TYPE_FIELDS.appreciation).map(([key, label, kind]) => (
              <input
                key={key}
                type={kind}
                required={key === 'first_name' || (key === 'program_name' && ['internship', 'completion', 'participation'].includes(form.certificate_type))}
                placeholder={label}
                value={form[key]}
                onChange={(e) => setField(key, e.target.value)}
                style={inputStyle}
              />
            ))}
          </div>

          <div style={{ display: 'flex', gap: '.75rem', flexWrap: 'wrap' }}>
            <button type="submit" className="btn" disabled={generating} style={primaryButton}>
              {generating ? <Loader2 size={17} className="spin" /> : <Plus size={17} />}
              {generating ? 'Generating…' : 'Generate Certificate'}
            </button>
          </div>
          {error && <p style={{ color: '#b91c1c', margin: 0 }}>{error}</p>}
          {info && <p style={{ color: '#047857', margin: 0 }}>{info}</p>}
        </form>
      </div>

      <div className="card" style={{ overflowX: 'auto', padding: '1rem' }}>
        <div style={{ display: 'flex', gap: '.75rem', flexWrap: 'wrap', marginBottom: '1rem', alignItems: 'center' }}>
          <select
            value={typeFilter}
            onChange={(e) => { setTypeFilter(e.target.value); setList({ ...list, page: 1 }); }}
            style={inputStyle}
          >
            <option value="">All types</option>
            {(types || []).map((t) => (
              <option key={t.type} value={t.type}>
                {TYPE_LABELS[t.type] || t.label}
              </option>
            ))}
          </select>
          <input
            placeholder="Search name / number / email"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setList({ ...list, page: 1 }); }}
            style={{ ...inputStyle, flex: 1, minWidth: 220 }}
          />
          <button type="button" className="btn" onClick={load} style={outlineButton}>
            <RefreshCw size={16} />Refresh
          </button>
        </div>

        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={th}>Number</th>
              <th style={th}>Type</th>
              <th style={th}>Recipient</th>
              <th style={th}>Issue Date</th>
              <th style={th}>Status</th>
              <th style={th} />
            </tr>
          </thead>
          <tbody>
            {(list.items || []).map((cert) => (
              <tr key={cert.id}>
                <td style={td}>
                  <b>{cert.certificate_number || '—'}</b>
                </td>
                <td style={td}>{TYPE_LABELS[cert.certificate_type] || cert.certificate_type}</td>
                <td style={td}>{cert.recipient_name}</td>
                <td style={td}>{cert.issue_date || '—'}</td>
                <td style={td}>
                  {cert.revoked ? (
                    <span style={{ color: '#b91c1c' }}>Revoked</span>
                  ) : (
                    <span style={{ color: '#047857' }}>Valid</span>
                  )}
                </td>
                <td style={{ ...td, textAlign: 'right', whiteSpace: 'nowrap' }}>
                  {!cert.revoked && cert.rendered_url && (
                    <button type="button" className="btn" title="Preview" style={outlineButton} onClick={() => window.open(resolveMediaUrl(cert.rendered_url), '_blank')}>
                      <Eye size={15} />
                    </button>
                  )}
                  {cert.rendered_url && (
                    <button type="button" className="btn" title="Download JPG" style={outlineButton} onClick={() => downloadAdminCertificate(cert.id, 'jpg').catch((e) => setError(e.message))}>
                      <Download size={15} />
                    </button>
                  )}
                  {cert.rendered_url && (
                    <button type="button" className="btn" title="Download PDF" style={outlineButton} onClick={() => downloadAdminCertificate(cert.id, 'pdf').catch((e) => setError(e.message))}>
                      <FileText size={15} />
                    </button>
                  )}
                  {!cert.revoked && (
                    <button type="button" className="btn" title="Revoke" style={dangerButton} onClick={() => handleRevoke(cert.id)}>
                      <ShieldX size={15} />
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {list.items?.length === 0 && !loading && (
          <Empty>No certificates yet — generate the first one above.</Empty>
        )}
        {list.total > list.page_size && (
          <div style={{ display: 'flex', justifyContent: 'center', gap: '.5rem', marginTop: '1rem' }}>
            <button className="btn" style={outlineButton} disabled={list.page <= 1} onClick={() => setList({ ...list, page: list.page - 1 })}>
              Prev
            </button>
            <span style={{ padding: '.5rem .8rem', color: '#475569' }}>
              Page {list.page} of {Math.max(1, Math.ceil(list.total / list.page_size || 1))}
            </span>
            <button className="btn" style={outlineButton} disabled={list.page * list.page_size >= list.total} onClick={() => setList({ ...list, page: list.page + 1 })}>
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function VolunteerTab() {
  const [volunteers, setVolunteers] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const items = await fetchGeneratedVolunteers({ status: 'accepted', search });
      setVolunteers(items);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleGenerateCard(id) {
    setBusyId(id);
    setError('');
    try {
      await generateAdminVolunteerCard(id, {});
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId(null);
    }
  }

  async function handleRevoke(id) {
    if (!window.confirm('Revoke this Volunteer ID card? It will no longer verify.')) return;
    try {
      await revokeAdminVolunteerCard(id);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card" style={{ overflowX: 'auto', padding: '1rem' }}>
      <SectionTitle icon={BadgeCheck}>Volunteer ID Cards</SectionTitle>
      <div style={{ display: 'flex', gap: '.75rem', flexWrap: 'wrap', marginBottom: '1rem', alignItems: 'center' }}>
        <input
          placeholder="Search name / email / ID"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ ...inputStyle, flex: 1, minWidth: 220 }}
        />
        <button type="button" className="btn" onClick={load} style={outlineButton}>
          <RefreshCw size={16} />Refresh
        </button>
      </div>

      <table style={tableStyle}>
        <thead>
          <tr>
            <th style={th}>Volunteer</th>
            <th style={th}>ID</th>
            <th style={th}>Valid Till</th>
            <th style={th}>Official Card</th>
            <th style={th} />
          </tr>
        </thead>
        <tbody>
          {(volunteers || []).map((v) => (
            <tr key={v.id}>
              <td style={td}>
                <b>{v.full_name}</b>
                <div style={{ color: '#94a3b8', fontSize: '.8rem' }}>{v.email}</div>
              </td>
              <td style={td}>{v.volunteer_id || '—'}</td>
              <td style={td}>{v.valid_till || '—'}</td>
              <td style={td}>
                {v.card_revoked_at ? (
                  <span style={{ color: '#b91c1c' }}>Revoked</span>
                ) : v.card_file_path ? (
                  <span style={{ color: '#047857' }}>
                    <ShieldCheck size={15} style={{ verticalAlign: 'middle' }} /> Ready
                    <a
                      href={resolveMediaUrl(v.verified_url)}
                      target="_blank"
                      rel="noreferrer"
                      style={{ display: 'block', fontSize: '.78rem', color: '#047857' }}
                    >
                      View verification page
                    </a>
                  </span>
                ) : (
                  <span style={{ color: '#94a3b8' }}>Not generated</span>
                )}
              </td>
              <td style={{ ...td, textAlign: 'right', whiteSpace: 'nowrap' }}>
                <button
                  type="button"
                  className="btn"
                  disabled={busyId === v.id || !!v.card_revoked_at}
                  style={v.card_file_path && !v.card_revoked_at ? outlineButton : primaryButton}
                  onClick={() => handleGenerateCard(v.id)}
                >
                  {busyId === v.id ? <Loader2 size={15} className="spin" /> : <Plus size={15} />}
                  {v.card_file_path && !v.card_revoked_at ? 'Regenerate' : 'Generate Card'}
                </button>
                {v.card_file_path && !v.card_revoked_at && (
                  <>
                    <button type="button" className="btn" title="Download JPG" style={outlineButton} onClick={() => downloadAdminVolunteerCard(v.id, 'jpg').catch((e) => setError(e.message))}>
                      <Download size={15} />
                    </button>
                    <button type="button" className="btn" title="Download PDF" style={outlineButton} onClick={() => downloadAdminVolunteerCard(v.id, 'pdf').catch((e) => setError(e.message))}>
                      <FileText size={15} />
                    </button>
                    <button type="button" className="btn" title="Revoke" style={dangerButton} onClick={() => handleRevoke(v.id)}>
                      <ShieldX size={15} />
                    </button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {volunteers?.length === 0 && !loading && (
        <Empty>No accepted volunteers with this search.</Empty>
      )}
      {error && <p style={{ color: '#b91c1c', marginTop: '1rem' }}>{error}</p>}
    </div>
  );
}

export default function DocumentGenerator() {
  const [tab, setTab] = useState('certificates');
  const [types, setTypes] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchGeneratedOptions()
      .then((data) => setTypes(data.certificate_types || []))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div style={{ display: 'grid', gap: '1rem' }}>
      <div className="card" style={{ padding: '1rem' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '.5rem', marginBottom: '1rem' }}>
          <FileImage size={20} /> Official Documents
        </h2>
        <p style={{ color: '#64748b', marginTop: 0 }}>
          Generate official certificates and the Volunteer ID card from the
          registered templates. Every document carries a unique QR code that
          opens /verify pages to validate authenticity.
        </p>
        <div style={{ display: 'flex', gap: '.6rem', flexWrap: 'wrap' }}>
          {[
            ['certificates', 'Certificates', Award],
            ['volunteers', 'Volunteer ID Cards', UserCheck],
          ].map(([key, label, Icon]) => (
            <button
              key={key}
              type="button"
              className="btn"
              onClick={() => setTab(key)}
              style={tab === key ? primaryButton : outlineButton}
            >
              <Icon size={16} /> {label}
            </button>
          ))}
        </div>
      </div>

      {error && <p style={{ color: '#b91c1c' }}>{error}</p>}
      {types === null ? (
        <p style={{ color: '#94a3b8' }}>Loading document options…</p>
      ) : tab === 'certificates' ? (
        <CertificateTab types={types} />
      ) : (
        <VolunteerTab />
      )}
    </div>
  );
}