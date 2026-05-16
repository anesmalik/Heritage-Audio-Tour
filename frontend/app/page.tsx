'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

const SITES = [
  {
    id: 'babylon',
    name: 'Babylon',
    arabic: 'بابل',
    period: 'Neo-Babylonian Empire · 626–539 BC',
    description: 'Walk through the legendary city of Nebuchadnezzar II — home to the Ishtar Gate, the Processional Way, and the mythic Hanging Gardens.',
    coordinates: '32°32\'N 44°25\'E',
    bg: 'linear-gradient(135deg, #78350f 0%, #92400e 40%, #b45309 100%)',
    emoji: '🏛',
  },
  {
    id: 'ur',
    name: 'Ur',
    arabic: 'أور',
    period: 'Third Dynasty of Ur · 2112–2004 BC',
    description: 'Explore one of the oldest cities in human history — birthplace of Abraham, home to the Great Ziggurat, and the Royal Cemetery of kings.',
    coordinates: '30°57\'N 46°06\'E',
    bg: 'linear-gradient(135deg, #1c4a3e 0%, #065f46 40%, #047857 100%)',
    emoji: '⛩',
  },
  {
    id: 'erbil_citadel',
    name: 'Erbil Citadel',
    arabic: 'قلعة أربيل',
    period: 'Continuously inhabited · 6000+ years',
    description: 'Ascend the ancient tell of Erbil — a UNESCO World Heritage Site where 6,000 years of human civilization are layered beneath your feet.',
    coordinates: '36°11\'N 44°00\'E',
    bg: 'linear-gradient(135deg, #1e3a5f 0%, #1e40af 40%, #2563eb 100%)',
    emoji: '🏰',
  },
];

const DURATIONS = [
  { mins: 30, label: '30 min', stops: '4 stops', description: 'A focused visit to the most iconic locations.' },
  { mins: 60, label: '60 min', stops: '6 stops', description: 'A balanced tour covering history, culture, and architecture.' },
  { mins: 90, label: '90 min', stops: '8 stops', description: 'The complete experience — every remarkable corner.' },
];

const FEATURES = [
  { icon: '🎧', title: 'AI Narration', description: 'Expert-quality audio narrated by AI, tailored to your chosen site and duration.' },
  { icon: '🗺', title: 'Walking Route', description: 'An optimised walking route with an interactive map guiding you stop to stop.' },
  { icon: '✅', title: 'Fact-Checked', description: 'Every claim verified against Wikipedia sources by a dedicated AI agent.' },
  { icon: '⚡', title: 'Instant Cache', description: 'Previously generated tours load instantly — no waiting, no repeat API calls.' },
];

export default function HomePage() {
  const router = useRouter();
  const [selectedSite, setSelectedSite] = useState<string | null>(null);
  const [selectedDuration, setSelectedDuration] = useState<number | null>(null);

  const canGenerate = selectedSite && selectedDuration;

  const handleGenerate = () => {
    if (!canGenerate) return;
    const params = new URLSearchParams({
      site_id: selectedSite,
      duration_mins: selectedDuration.toString(),
    });
    router.push(`/generating?${params.toString()}`);
  };

  return (
    <div className="min-h-screen bg-white" style={{ fontFamily: 'system-ui, sans-serif' }}>

      {/* ── Navbar ─────────────────────────────────────────────────── */}
      <nav style={{ borderBottom: '1px solid #f0ede8', background: '#fff', position: 'sticky', top: 0, zIndex: 50 }}>
        <div style={{ maxWidth: 1100, margin: '0 auto', padding: '0 24px', height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 22 }}>🏛</span>
            <span style={{ fontWeight: 700, fontSize: 18, color: '#1a1a1a', letterSpacing: '-0.3px' }}>
              Echoes of <span style={{ color: '#b45309' }}>Mesopotamia</span>
            </span>
          </div>
          <button
            onClick={() => document.getElementById('choose-site')?.scrollIntoView({ behavior: 'smooth' })}
            style={{ background: '#b45309', color: '#fff', border: 'none', borderRadius: 6, padding: '8px 18px', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}
          >
            Start Tour
          </button>
        </div>
      </nav>

      {/* ── Hero ───────────────────────────────────────────────────── */}
      <section style={{ height: 420, position: 'relative', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
        {/* Static CartoDB Light tiles centred on Babylon — 5 wide × 2 tall × 256px */}
        <div style={{ position: 'absolute', top: '-46px', left: '50%', transform: 'translateX(-50%)', width: 1280, height: 512, filter: 'grayscale(100%)', opacity: 0.75, zIndex: 0, pointerEvents: 'none' }}>
          {([1655, 1656] as number[]).flatMap((y, row) =>
            ([2551, 2552, 2553, 2554, 2555] as number[]).map((x, col) => (
              <img
                key={`${x}-${y}`}
                src={`https://a.basemaps.cartocdn.com/light_all/12/${x}/${y}.png`}
                alt=""
                style={{ position: 'absolute', top: row * 256, left: col * 256, width: 256, height: 256, display: 'block' }}
              />
            ))
          )}
        </div>
        {/* Dark overlay — let map show through */}
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', background: 'linear-gradient(135deg, rgba(28,20,10,0.52) 0%, rgba(45,31,14,0.48) 100%)', zIndex: 1 }} />
        <div style={{ position: 'relative', zIndex: 2, maxWidth: 700, margin: '0 auto', padding: '0 24px' }}>
          <div style={{ display: 'inline-block', background: 'rgba(180,83,9,0.25)', border: '1px solid rgba(180,83,9,0.4)', borderRadius: 20, padding: '4px 14px', marginBottom: 20 }}>
            <span style={{ color: '#fbbf24', fontSize: 12, fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', fontFamily: 'monospace' }}>AI-Powered Heritage Experience</span>
          </div>
          <h1 style={{ color: '#fff', fontSize: 52, fontWeight: 800, lineHeight: 1.15, margin: '0 0 16px', letterSpacing: '-1px' }}>
            Explore Iraq's<br />
            <span style={{ color: '#f59e0b' }}>Ancient Wonders</span>
          </h1>
          <p style={{ color: '#fff', fontSize: 18, lineHeight: 1.6, margin: '0 0 36px', textShadow: '0 1px 6px rgba(0,0,0,0.6)' }}>
            Select a site and duration. An AI guide crafts your personal audio tour —
            narrated, fact-checked, and ready to walk.
          </p>
          <button
            onClick={() => document.getElementById('choose-site')?.scrollIntoView({ behavior: 'smooth' })}
            style={{ background: '#b45309', color: '#fff', border: 'none', borderRadius: 8, padding: '14px 32px', fontSize: 16, fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 20px rgba(180,83,9,0.4)' }}
          >
            Build My Tour →
          </button>
        </div>
      </section>

      {/* ── Features ───────────────────────────────────────────────── */}
      <section style={{ background: '#fafaf8', padding: '56px 24px', borderBottom: '1px solid #f0ede8' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <h2 style={{ textAlign: 'center', fontSize: 13, fontWeight: 700, color: '#b45309', letterSpacing: '0.15em', textTransform: 'uppercase', fontFamily: 'monospace', marginBottom: 40 }}>
            Why Echoes of Mesopotamia
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 24 }}>
            {FEATURES.map((f) => (
              <div key={f.title} style={{ background: '#fff', border: '1px solid #f0ede8', borderRadius: 12, padding: '28px 24px', textAlign: 'center' }}>
                <div style={{ fontSize: 32, marginBottom: 14 }}>{f.icon}</div>
                <h3 style={{ fontSize: 15, fontWeight: 700, color: '#1a1a1a', margin: '0 0 8px' }}>{f.title}</h3>
                <p style={{ fontSize: 13, color: '#6b7280', lineHeight: 1.6, margin: 0 }}>{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Site selection ─────────────────────────────────────────── */}
      <section id="choose-site" style={{ padding: '64px 24px', maxWidth: 1100, margin: '0 auto' }}>
        <div style={{ marginBottom: 36 }}>
          <p style={{ fontSize: 13, fontWeight: 700, color: '#b45309', letterSpacing: '0.15em', textTransform: 'uppercase', fontFamily: 'monospace', margin: '0 0 8px' }}>Step 1</p>
          <h2 style={{ fontSize: 28, fontWeight: 800, color: '#1a1a1a', margin: 0, letterSpacing: '-0.5px' }}>Choose Your Site</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 20 }}>
          {SITES.map((site) => {
            const selected = selectedSite === site.id;
            return (
              <button
                key={site.id}
                onClick={() => setSelectedSite(site.id)}
                style={{
                  textAlign: 'left', padding: 0, border: 'none', borderRadius: 14,
                  overflow: 'hidden', cursor: 'pointer',
                  outline: selected ? '3px solid #b45309' : '3px solid transparent',
                  outlineOffset: 2,
                  boxShadow: selected ? '0 8px 30px rgba(180,83,9,0.25)' : '0 2px 12px rgba(0,0,0,0.08)',
                  transform: selected ? 'translateY(-2px)' : 'none',
                  transition: 'all 0.2s ease',
                  background: 'transparent',
                }}
              >
                {/* Card image area */}
                <div style={{ height: 140, background: site.bg, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '20px 24px', position: 'relative' }}>
                  <div>
                    <div style={{ color: 'rgba(255,255,255,0.6)', fontSize: 24, fontFamily: 'serif', marginBottom: 4 }}>{site.arabic}</div>
                    <div style={{ color: '#fff', fontSize: 26, fontWeight: 800, letterSpacing: '-0.5px' }}>{site.name}</div>
                  </div>
                  <div style={{ fontSize: 52, opacity: 0.4 }}>{site.emoji}</div>
                  {selected && (
                    <div style={{ position: 'absolute', top: 12, right: 12, width: 24, height: 24, background: '#b45309', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, color: '#fff' }}>✓</div>
                  )}
                </div>
                {/* Card body */}
                <div style={{ background: '#fff', padding: '18px 24px', borderTop: '1px solid #f0ede8' }}>
                  <p style={{ fontSize: 11, fontWeight: 700, color: '#b45309', textTransform: 'uppercase', letterSpacing: '0.08em', fontFamily: 'monospace', margin: '0 0 8px' }}>{site.period}</p>
                  <p style={{ fontSize: 13, color: '#4b5563', lineHeight: 1.55, margin: '0 0 12px' }}>{site.description}</p>
                  <p style={{ fontSize: 11, color: '#fff', fontFamily: 'monospace', margin: 0, background: '#6b7280', display: 'inline-block', padding: '2px 8px', borderRadius: 4 }}>{site.coordinates}</p>
                </div>
              </button>
            );
          })}
        </div>
      </section>

      {/* ── Duration selection ─────────────────────────────────────── */}
      <section style={{ padding: '0 24px 64px', maxWidth: 1100, margin: '0 auto' }}>
        <div style={{ marginBottom: 36 }}>
          <p style={{ fontSize: 13, fontWeight: 700, color: '#b45309', letterSpacing: '0.15em', textTransform: 'uppercase', fontFamily: 'monospace', margin: '0 0 8px' }}>Step 2</p>
          <h2 style={{ fontSize: 28, fontWeight: 800, color: '#1a1a1a', margin: 0, letterSpacing: '-0.5px' }}>Choose Your Duration</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16 }}>
          {DURATIONS.map((d) => {
            const selected = selectedDuration === d.mins;
            return (
              <button
                key={d.mins}
                onClick={() => setSelectedDuration(d.mins)}
                style={{
                  textAlign: 'left', padding: '24px', borderRadius: 12, cursor: 'pointer',
                  border: selected ? '2px solid #b45309' : '2px solid #e5e7eb',
                  background: selected ? '#fef3c7' : '#fff',
                  transition: 'all 0.15s ease',
                  boxShadow: selected ? '0 4px 16px rgba(180,83,9,0.15)' : 'none',
                }}
              >
                <div style={{ fontSize: 36, fontWeight: 800, color: selected ? '#b45309' : '#1a1a1a', letterSpacing: '-1px', marginBottom: 4 }}>{d.label}</div>
                <div style={{ fontSize: 12, fontWeight: 700, color: selected ? '#92400e' : '#6b7280', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 10 }}>{d.stops}</div>
                <div style={{ fontSize: 13, color: '#6b7280', lineHeight: 1.5 }}>{d.description}</div>
              </button>
            );
          })}
        </div>
      </section>

      {/* ── Generate CTA ───────────────────────────────────────────── */}
      <section style={{ background: '#fafaf8', borderTop: '1px solid #f0ede8', padding: '48px 24px', textAlign: 'center' }}>
        <button
          onClick={handleGenerate}
          disabled={!canGenerate}
          style={{
            background: canGenerate ? '#b45309' : '#e5e7eb',
            color: canGenerate ? '#fff' : '#9ca3af',
            border: 'none', borderRadius: 10,
            padding: '18px 48px', fontSize: 17, fontWeight: 700,
            cursor: canGenerate ? 'pointer' : 'not-allowed',
            boxShadow: canGenerate ? '0 6px 24px rgba(180,83,9,0.35)' : 'none',
            transition: 'all 0.2s ease',
            letterSpacing: '-0.2px',
          }}
        >
          {canGenerate ? 'Generate My Audio Tour →' : 'Select a site and duration to continue'}
        </button>
        {canGenerate && (
          <p style={{ marginTop: 12, fontSize: 13, color: '#9ca3af' }}>
            Generating takes ~2 minutes · Cached tours load instantly
          </p>
        )}
      </section>

      {/* ── Footer ─────────────────────────────────────────────────── */}
      <footer style={{ background: '#1a1a1a', padding: '40px 24px', textAlign: 'center' }}>
        <div style={{ fontSize: 22, marginBottom: 10 }}>🏛</div>
        <p style={{ color: '#6b7280', fontSize: 12, margin: 0, lineHeight: 1.7 }}>
          Audio narration is AI-generated · All facts sourced from Wikipedia · Not a substitute for professional guides
        </p>
        <p style={{ color: '#374151', fontSize: 11, marginTop: 16 }}>© 2025 Echoes of Mesopotamia</p>
      </footer>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap');
        * { box-sizing: border-box; }
        button:hover { opacity: 0.92; }
      `}</style>
    </div>
  );
}
