'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams } from 'next/navigation';
import dynamic from 'next/dynamic';

const TourMap = dynamic(() => import('../../components/TourMap'), { ssr: false });

interface AudioFile {
  stop_number: number;
  stop_id: string;
  stop_name: string;
  filename: string;
  size_kb: number;
}

interface Manifest {
  site_id: string;
  site_name: string;
  duration_mins: number;
  cache_key: string;
  stop_count: number;
  audio_files: AudioFile[];
  geojson_file: string;
  ai_disclosure: string;
}

function AudioPlayer({ src }: { src: string }) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (playing) { audioRef.current.pause(); } else { audioRef.current.play(); }
    setPlaying(!playing);
  };

  const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    setProgress((audioRef.current.currentTime / audioRef.current.duration) * 100);
  };

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!audioRef.current) return;
    const rect = e.currentTarget.getBoundingClientRect();
    audioRef.current.currentTime = ((e.clientX - rect.left) / rect.width) * audioRef.current.duration;
  };

  const fmt = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;

  return (
    <div style={{ marginTop: 14, background: '#fafaf8', border: '1px solid #f0ede8', borderRadius: 8, padding: '14px 16px' }}>
      <audio ref={audioRef} src={src}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={() => audioRef.current && setDuration(audioRef.current.duration)}
        onEnded={() => setPlaying(false)}
      />
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <button
          onClick={togglePlay}
          style={{ width: 40, height: 40, borderRadius: '50%', background: '#b45309', border: 'none', color: '#fff', fontSize: 14, cursor: 'pointer', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        >
          {playing ? '⏸' : '▶'}
        </button>
        <div style={{ flex: 1 }}>
          <div style={{ height: 4, background: '#e5e7eb', borderRadius: 2, cursor: 'pointer', position: 'relative' }} onClick={handleSeek}>
            <div style={{ height: '100%', background: '#b45309', borderRadius: 2, width: `${progress}%`, transition: 'width 0.1s' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 5 }}>
            <span style={{ fontSize: 11, color: '#9ca3af', fontFamily: 'monospace' }}>
              {audioRef.current ? fmt(audioRef.current.currentTime) : '0:00'}
            </span>
            <span style={{ fontSize: 11, color: '#9ca3af', fontFamily: 'monospace' }}>
              {duration ? fmt(duration) : '--:--'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function TourPage() {
  const params = useParams();
  const cacheKey = params.cache_key as string;

  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [geojson, setGeojson] = useState<object | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeStop, setActiveStop] = useState<number>(1);

  const API = 'http://localhost:8000';

  useEffect(() => {
    if (!cacheKey) return;
    fetch(`${API}/tour/${cacheKey}`).then(r => r.json()).then(data => { setManifest(data); setLoading(false); });
    fetch(`${API}/tour/${cacheKey}/files/route.geojson`).then(r => r.json()).then(setGeojson);
  }, [cacheKey]);

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: '#fafaf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'system-ui, sans-serif' }}>
        <p style={{ color: '#9ca3af', fontSize: 14 }}>Loading tour...</p>
      </div>
    );
  }

  if (!manifest) {
    return (
      <div style={{ minHeight: '100vh', background: '#fafaf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'system-ui, sans-serif' }}>
        <p style={{ color: '#ef4444', fontSize: 14 }}>Tour not found.</p>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: '#fafaf8', fontFamily: 'system-ui, sans-serif' }}>

      {/* Navbar */}
      <nav style={{ borderBottom: '1px solid #f0ede8', background: '#fff', position: 'sticky', top: 0, zIndex: 50 }}>
        <div style={{ maxWidth: 1100, margin: '0 auto', padding: '0 24px', height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <a href="/" style={{ display: 'flex', alignItems: 'center', gap: 8, textDecoration: 'none' }}>
            <span style={{ fontSize: 22 }}>🏛</span>
            <span style={{ fontWeight: 700, fontSize: 18, color: '#1a1a1a', letterSpacing: '-0.3px' }}>
              Echoes of <span style={{ color: '#b45309' }}>Mesopotamia</span>
            </span>
          </a>
          <a href="/" style={{ color: '#6b7280', fontSize: 13, textDecoration: 'none', border: '1px solid #e5e7eb', borderRadius: 6, padding: '6px 14px' }}>
            ← Home
          </a>
        </div>
      </nav>

      {/* Page header */}
      <div style={{ background: '#fff', borderBottom: '1px solid #f0ede8', padding: '32px 24px' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <p style={{ fontSize: 12, fontWeight: 700, color: '#b45309', letterSpacing: '0.15em', textTransform: 'uppercase', fontFamily: 'monospace', margin: '0 0 6px' }}>
            Your Audio Tour
          </p>
          <h1 style={{ fontSize: 36, fontWeight: 800, color: '#1a1a1a', margin: '0 0 8px', letterSpacing: '-0.5px' }}>
            {manifest.site_name}
          </h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span style={{ fontSize: 13, color: '#6b7280' }}>{manifest.duration_mins} minutes</span>
            <span style={{ color: '#e5e7eb' }}>·</span>
            <span style={{ fontSize: 13, color: '#6b7280' }}>{manifest.stop_count} stops</span>
            <span style={{ color: '#e5e7eb' }}>·</span>
            <span style={{ fontSize: 12, background: '#fef3c7', color: '#92400e', padding: '2px 10px', borderRadius: 20, fontWeight: 600 }}>
              AI Generated
            </span>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '32px 24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>

          {/* Left — Stop list */}
          <section>
            <h2 style={{ fontSize: 12, fontWeight: 700, color: '#b45309', letterSpacing: '0.15em', textTransform: 'uppercase', fontFamily: 'monospace', margin: '0 0 16px' }}>
              Your Stops
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {manifest.audio_files.map((file) => {
                const active = activeStop === file.stop_number;
                return (
                  <div
                    key={file.stop_number}
                    onClick={() => setActiveStop(file.stop_number)}
                    style={{
                      background: '#fff', borderRadius: 10, padding: '16px 18px',
                      border: active ? '2px solid #b45309' : '2px solid #f0ede8',
                      cursor: 'pointer', transition: 'all 0.15s ease',
                      boxShadow: active ? '0 4px 16px rgba(180,83,9,0.12)' : '0 1px 4px rgba(0,0,0,0.04)',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
                        background: active ? '#b45309' : '#f0ede8',
                        color: active ? '#fff' : '#9ca3af',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 12, fontWeight: 700, fontFamily: 'monospace',
                      }}>
                        {String(file.stop_number).padStart(2, '0')}
                      </div>
                      <div style={{ flex: 1 }}>
                        <h3 style={{ fontSize: 15, fontWeight: 700, color: '#1a1a1a', margin: '0 0 4px' }}>
                          {file.stop_name}
                        </h3>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                          <span style={{ fontSize: 12, color: '#9ca3af', fontFamily: 'monospace' }}>
                            {file.size_kb} KB · MP3
                          </span>
                          <a
                            href={`${API}/tour/${cacheKey}/files/${file.filename}`}
                            download={file.filename}
                            onClick={e => e.stopPropagation()}
                            style={{ fontSize: 12, color: '#b45309', textDecoration: 'none', fontWeight: 600 }}
                          >
                            ↓ Download
                          </a>
                        </div>
                        {active && (
                          <AudioPlayer src={`${API}/tour/${cacheKey}/files/${file.filename}`} />
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          {/* Right — Map */}
          <section>
            <h2 style={{ fontSize: 12, fontWeight: 700, color: '#b45309', letterSpacing: '0.15em', textTransform: 'uppercase', fontFamily: 'monospace', margin: '0 0 16px' }}>
              Walking Route
            </h2>
            <div style={{ borderRadius: 12, overflow: 'hidden', border: '1px solid #f0ede8', height: 500, boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
              {geojson ? (
                <TourMap geojson={geojson} />
              ) : (
                <div style={{ height: '100%', background: '#fafaf8', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <p style={{ color: '#d1d5db', fontSize: 13, fontFamily: 'monospace' }}>Loading map...</p>
                </div>
              )}
            </div>

            {/* AI Disclosure */}
            <div style={{ marginTop: 12, background: '#fffbeb', border: '1px solid #fde68a', borderRadius: 8, padding: '12px 16px' }}>
              <p style={{ fontSize: 12, color: '#92400e', margin: 0, lineHeight: 1.6 }}>
                ⚠ {manifest.ai_disclosure}
              </p>
            </div>
          </section>

        </div>
      </div>

      <style>{`* { box-sizing: border-box; }`}</style>
    </div>
  );
}
