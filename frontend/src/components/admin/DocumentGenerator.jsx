import React, { useCallback, useEffect, useState } from 'react';
import {
  Award, Download, Eye, FileImage, FileText, Inbox, Loader2, Plus, RefreshCw,
  ShieldCheck, ShieldX, UserCheck, BadgeCheck,
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
import '../../styles/admin.css';

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
    <h2 className="adm-heading">
      <Icon size={20} />
      {children}
    </h2>
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

  const currentType = form.certificate_type;

  return (
    <div style={{ display: 'grid', gap: '1.5rem' }}>
      <div className="card adm-panel">
        <SectionTitle icon={Award}>Generate Official Certificate</SectionTitle>

        <div className="adm-type-grid">
          {(types || []).map((t) => {
            const active = currentType === t.type;
            return (
              <button
                key={t.type}
                type="button"
                className="adm-type-card"
                aria-pressed={active}
                onClick={() => setField('certificate_type', t.type)}
              >
                <span className="adm-type-icon">
                  <Award size={17} />
                </span>
                <span>
                  {TYPE_LABELS[t.type] || t.label}
                  {!t.image_available ? <span className="adm-sub"> (missing template)</span> : null}
                </span>
              </button>
            );
          })}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleGenerate();
          }}
        >
          {(TYPE_FIELDS[currentType] || TYPE_FIELDS.appreciation).map(([key, label, kind]) => (
            <div style={{ marginBottom: '.8rem' }} key={key}>
              <label className="adm-label" htmlFor={`dg-${key}`}>
                {label}
              </label>
              <input
                id={`dg-${key}`}
                className="adm-input"
                type={kind}
                required={key === 'first_name' || (key === 'program_name' && ['internship', 'completion', 'participation'].includes(currentType))}
                placeholder={label}
                value={form[key]}
                onChange={(e) => setField(key, e.target.value)}
              />
            </div>
          ))}

          <div style={{ display: 'flex', gap: '.75rem', flexWrap: 'wrap', marginTop: '.4rem' }}>
            <button type="submit" className="adm-btn adm-btn-primary" disabled={generating}>
              {generating ? <Loader2 size={17} className="spin" /> : <Plus size={17} />}
              {generating ? 'Generating…' : 'Generate Certificate'}
            </button>
          </div>
          {error && (
            <p style={{ color: '#b91c1c', margin: '1rem 0 0' }}>
              {error}
            </p>
          )}
          {info && (
            <p style={{ color: '#047857', margin: '1rem 0 0' }}>
              {info}
            </p>
          )}
        </form>
      </div>

      <div className="card adm-panel">
        <SectionTitle icon={FileText}>Registered Certificates</SectionTitle>

        <div className="adm-toolbar">
          <div className="adm-filter">
            <label className="adm-filter-label" htmlFor="dg-filter">
              Certificate Type
            </label>
            <select
              id="dg-filter"
              className="adm-input"
              value={typeFilter}
              onChange={(e) => {
                setTypeFilter(e.target.value);
                setList({ ...list, page: 1 });
              }}
            >
              <option value="">All types</option>
              {(types || []).map((t) => (
                <option key={t.type} value={t.type}>
                  {TYPE_LABELS[t.type] || t.label}
                </option>
              ))}
            </select>
          </div>
          <div className="adm-search">
            <label className="adm-filter-label" htmlFor="dg-search">
              Search
            </label>
            <input
              id="dg-search"
              className="adm-input"
              placeholder="Search name / number / email"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setList({ ...list, page: 1 });
              }}
            />
          </div>
          <div className="adm-filter">
            <span className="adm-filter-label">&nbsp;</span>
            <button type="button" className="adm-btn adm-btn-ghost" onClick={load}>
              <RefreshCw size={16} /> Refresh
            </button>
          </div>
        </div>

        {loading ? (
          <div className="adm-loading">
            <Loader2 size={18} className="spin" /> Loading certificates…
          </div>
        ) : (
          <div className="adm-table-wrap">
            <table className="adm-table">
              <thead>
                <tr>
                  <th>Number</th>
                  <th>Type</th>
                  <th>Recipient</th>
                  <th>Issue Date</th>
                  <th>Status</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {(list.items || []).map((cert) => (
                  <tr key={cert.id}>
                    <td className="adm-num">{cert.certificate_number || '—'}</td>
                    <td>{TYPE_LABELS[cert.certificate_type] || cert.certificate_type}</td>
                    <td>{cert.recipient_name}</td>
                    <td style={{ whiteSpace: 'nowrap' }}>{cert.issue_date || '—'}</td>
                    <td>
                      {cert.revoked ? (
                        <span className="adm-pill adm-pill-revoked">Revoked</span>
                      ) : (
                        <span className="adm-pill adm-pill-valid">Valid</span>
                      )}
                    </td>
                    <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                      <div className="adm-actions" style={{ justifyContent: 'flex-end' }}>
                        {!cert.revoked && cert.rendered_url && (
                          <button
                            type="button"
                            className="adm-action"
                            title="Preview"
                            onClick={() => window.open(resolveMediaUrl(cert.rendered_url), '_blank')}
                          >
                            <Eye size={15} /> Preview
                          </button>
                        )}
                        {cert.rendered_url && (
                          <button
                            type="button"
                            className="adm-action"
                            title="Download JPG"
                            onClick={() => downloadAdminCertificate(cert.id, 'jpg').catch((e) => setError(e.message))}
                          >
                            <Download size={15} /> JPG
                          </button>
                        )}
                        {cert.rendered_url && (
                          <button
                            type="button"
                            className="adm-action"
                            title="Download PDF"
                            onClick={() => downloadAdminCertificate(cert.id, 'pdf').catch((e) => setError(e.message))}
                          >
                            <FileText size={15} /> PDF
                          </button>
                        )}
                        {!cert.revoked && (
                          <button
                            type="button"
                            className="adm-action adm-action-danger"
                            title="Revoke"
                            onClick={() => handleRevoke(cert.id)}
                          >
                            <ShieldX size={15} /> Revoke
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {list.items?.length === 0 && !loading && (
              <div className="adm-empty">
                <span className="adm-empty-icon">
                  <Inbox size={22} />
                </span>
                <strong>No certificates yet</strong>
                <small>Generate the first one above — it will appear here.</small>
              </div>
            )}
          </div>
        )}

        {list.total > list.page_size && (
          <div className="adm-pagination" style={{ justifyContent: 'center' }}>
            <div className="adm-pager">
              <button
                className="adm-btn adm-btn-ghost"
                disabled={list.page <= 1}
                onClick={() => setList({ ...list, page: list.page - 1 })}
              >
                Prev
              </button>
              <span className="adm-pager-info">
                Page {list.page} of {Math.max(1, Math.ceil(list.total / list.page_size || 1))}
              </span>
              <button
                className="adm-btn adm-btn-ghost"
                disabled={list.page * list.page_size >= list.total}
                onClick={() => setList({ ...list, page: list.page + 1 })}
              >
                Next
              </button>
            </div>
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
    <div className="card adm-panel">
      <SectionTitle icon={BadgeCheck}>Volunteer ID Cards</SectionTitle>

      <div className="adm-toolbar">
        <div className="adm-search">
          <label className="adm-filter-label" htmlFor="vs-search">
            Search
          </label>
          <input
            id="vs-search"
            className="adm-input"
            placeholder="Search name / email / ID"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="adm-filter">
          <span className="adm-filter-label">&nbsp;</span>
          <button type="button" className="adm-btn adm-btn-ghost" onClick={load}>
            <RefreshCw size={16} /> Refresh
          </button>
        </div>
      </div>

      {loading ? (
        <div className="adm-loading">
          <Loader2 size={18} className="spin" /> Loading volunteers…
        </div>
      ) : (
        <div className="adm-table-wrap">
          <table className="adm-table">
            <thead>
              <tr>
                <th>Volunteer</th>
                <th>ID</th>
                <th>Valid Till</th>
                <th>Official Card</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {(volunteers || []).map((v) => (
                <tr key={v.id}>
                  <td>
                    <b className="adm-num" style={{ fontWeight: 700 }}>{v.full_name}</b>
                    <div className="adm-sub">{v.email}</div>
                  </td>
                  <td style={{ whiteSpace: 'nowrap' }}>{v.volunteer_id || '—'}</td>
                  <td style={{ whiteSpace: 'nowrap' }}>{v.valid_till || '—'}</td>
                  <td>
                    {v.card_revoked_at ? (
                      <span className="adm-pill adm-pill-revoked">Revoked</span>
                    ) : v.card_file_path ? (
                      <span className="adm-pill adm-pill-ready">
                        <ShieldCheck size={14} /> Ready
                      </span>
                    ) : (
                      <span className="adm-pill adm-pill-muted">Not generated</span>
                    )}
                    {v.card_file_path && !v.card_revoked_at ? (
                      <a
                        href={resolveMediaUrl(v.verified_url)}
                        target="_blank"
                        rel="noreferrer"
                        className="adm-sub"
                        style={{ color: '#047857', display: 'block' }}
                      >
                        View verification page
                      </a>
                    ) : null}
                  </td>
                  <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                    <div className="adm-actions" style={{ justifyContent: 'flex-end' }}>
                      <button
                        type="button"
                        className={v.card_file_path && !v.card_revoked_at ? 'adm-btn adm-btn-ghost' : 'adm-btn adm-btn-primary'}
                        disabled={busyId === v.id || !!v.card_revoked_at}
                        onClick={() => handleGenerateCard(v.id)}
                      >
                        {busyId === v.id ? <Loader2 size={15} className="spin" /> : <Plus size={15} />}
                        {v.card_file_path && !v.card_revoked_at ? 'Regenerate' : 'Generate Card'}
                      </button>
                      {v.card_file_path && !v.card_revoked_at ? (
                        <>
                          <button
                            type="button"
                            className="adm-action"
                            title="Download JPG"
                            onClick={() => downloadAdminVolunteerCard(v.id, 'jpg').catch((e) => setError(e.message))}
                          >
                            <Download size={15} /> JPG
                          </button>
                          <button
                            type="button"
                            className="adm-action"
                            title="Download PDF"
                            onClick={() => downloadAdminVolunteerCard(v.id, 'pdf').catch((e) => setError(e.message))}
                          >
                            <FileText size={15} /> PDF
                          </button>
                          <button
                            type="button"
                            className="adm-action adm-action-danger"
                            title="Revoke"
                            onClick={() => handleRevoke(v.id)}
                          >
                            <ShieldX size={15} /> Revoke
                          </button>
                        </>
                      ) : null}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {volunteers?.length === 0 && !loading && (
            <div className="adm-empty">
              <span className="adm-empty-icon">
                <Inbox size={22} />
              </span>
              <strong>No volunteers found</strong>
              <small>Try a different search or verify the accepted applications.</small>
            </div>
          )}
        </div>
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
    <div className="adm" style={{ display: 'grid', gap: '1rem' }}>
      <div className="card adm-panel">
        <h2 className="adm-heading">
          <FileImage size={20} /> Official Documents
        </h2>
        <p className="adm-hint" style={{ marginBottom: '.35rem' }}>
          Generate official certificates and the Volunteer ID card from the
          registered templates. Every document carries a unique QR code that
          opens /verify pages to validate authenticity.
        </p>
        <div className="adm-tabs">
          {[
            ['certificates', 'Certificates', Award],
            ['volunteers', 'Volunteer ID Cards', UserCheck],
          ].map(([key, label, Icon]) => (
            <button
              key={key}
              type="button"
              className={tab === key ? 'adm-btn adm-btn-primary' : 'adm-btn adm-btn-ghost'}
              onClick={() => setTab(key)}
            >
              <Icon size={16} /> {label}
            </button>
          ))}
        </div>
      </div>

      {error && <p style={{ color: '#b91c1c' }}>{error}</p>}
      {types === null ? (
        <div className="adm-loading">Loading document options…</div>
      ) : tab === 'certificates' ? (
        <CertificateTab types={types} />
      ) : (
        <VolunteerTab />
      )}
    </div>
  );
}