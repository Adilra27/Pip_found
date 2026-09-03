import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import DonateModal from './components/DonateModal';
import Home from './pages/Home';
import About from './pages/About';
import Causes from './pages/Causes';
import Donate from './pages/Donate';
import Gallery from './pages/Gallery';
import Contact from './pages/Contact';
import Terms from './pages/Terms';
import Blog from './pages/Blog';
import BlogPost from './pages/BlogPost';
import Team from './pages/Team';
import Certificates from './pages/Certificates';
import JoinUs from './pages/JoinUs';
import Admin from './pages/Admin';
import Partner from './pages/Partner';


import { fetchCauses } from './api';

function ScrollToTop() {
  const location = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname, location.search]);

  return null;
}

export default function App() {
  const [donateModalOpen, setDonateModalOpen] = useState(false);
  const [selectedCause, setSelectedCause] = useState(null);
  const [causes, setCauses] = useState([]);

  useEffect(() => {
    fetchCauses()
      .then((data) => setCauses(data))
      .catch((err) => console.error(err));
  }, []);

  const handleOpenDonate = (cause = null) => {
    setSelectedCause(cause);
    setDonateModalOpen(true);
  };

  const handleCloseDonate = () => {
    setDonateModalOpen(false);
    setSelectedCause(null);
  };

  return (
    <Router>
      <ScrollToTop />
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header onOpenDonate={() => handleOpenDonate()} />

        <main style={{ flexGrow: 1 }}>
          <Routes>
            <Route path="/" element={<Home onOpenDonate={() => handleOpenDonate()} onSelectCauseToDonate={(c) => handleOpenDonate(c)} />} />
            <Route path="/about" element={<About onOpenDonate={() => handleOpenDonate()} />} />
            <Route path="/causes" element={<Causes onSelectCauseToDonate={(c) => handleOpenDonate(c)} />} />
            <Route path="/donate" element={<Donate onOpenDonate={() => handleOpenDonate()} />} />
            <Route path="/gallery" element={<Gallery />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/terms" element={<Terms />} />
            <Route path="/blog" element={<Blog />} />
            <Route path="/blog/:id" element={<BlogPost />} />
            <Route path="/team" element={<Team />} />
            <Route path="/team/:teamName" element={<Team />} />
            <Route path="/certificates" element={<Certificates />} />
            <Route path="/join" element={<JoinUs />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/partners/:partnerSlug" element={<Partner />} />
          </Routes>
        </main>

        <Footer onOpenDonate={() => handleOpenDonate()} />

        <DonateModal
          isOpen={donateModalOpen}
          onClose={handleCloseDonate}
          selectedCause={selectedCause}
          causes={causes}
        />
      </div>
    </Router>
  );
}
