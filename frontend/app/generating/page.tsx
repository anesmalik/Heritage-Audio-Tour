'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

interface ProgressEvent {
  type: 'progress' | 'success' | 'error' | 'cached';
  message: string;
  data?: {
    cache_key?: string;
    manifest?: object;
  };
}

function GeneratingContent() {
  const router = useRouter();
  const params = useSearchParams();
  const siteId = params.get('site_id');
  const durationMins = params.get('duration_mins');

  const [events, setEvents] = useState<string[]>([]);
  const [status, setStatus] = useState<'connecting' | 'streaming' | 'done' | 'error'>('connecting');
  const [dots, setDots] = useState('');

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(d => d.length >= 3 ? '' : d + '.');
    }, 500);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!siteId || !durationMins) return;
    setStatus('streaming');

    const controller = new AbortController();

    fetch('http://localhost:8000/tour/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ site_id: siteId, duration_mins: parseInt(durationMins) }),
      signal: controller.signal,
    }).then(async (response) => {
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        for (const line of chunk.split('\n')) {
          if (!line.startsWith('data: ')) continue;
          const jsonStr = line.slice(6).trim();
          if (!jsonStr) continue;
          try {
            const event: ProgressEvent = JSON.parse(jsonStr);
            if (event.type === 'progress') {
              setEvents(prev => [...prev, event.message]);
            }
            if (event.type === 'cached') {
              setEvents(prev => [...prev, '⚡ Tour found in cache — loading instantly...']);
              setStatus('done');
              const cacheKey = event.data?.cache_key;
              if (cacheKey) setTimeout(() => router.push(`/tour/${cacheKey}`), 1000);
            }
            if (event.type === 'success') {
              setEvents(prev => [...prev, '✓ Your audio tour is ready!']);
              setStatus('done');
              const cacheKey = event.data?.cache_key;
              if (cacheKey) setTimeout(() => router.push(`/tour/${cacheKey}`), 1500);
            }
            if (event.type === 'error') {
              setEvents(prev => [...prev, `✗ Error: ${event.message}`]);
              setStatus('error');
            }
          } catch { /* skip malformed lines */ }
        }
      }
    }).catch((err) => {
      if (err.name !== 'AbortError') {
        setEvents(prev => [...prev, `✗ Connection failed: ${err.message}`]);
        setStatus('error');
      }
    });

    return () => controller.abort();
  }, [siteId, durationMins, router]);

  const siteName = siteId?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

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

      {/* Content */}
      <div style={{ maxWidth: 600, margin: '0 auto', padding: '64px 24px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

        {/* Spinner */}
        <div style={{
          width: 64, height: 64, borderRadius: '50%',
          border: '4px solid #f0ede8',
          borderTop: status === 'error' ? '4px solid #ef4444' : status === 'done' ? '4px solid #b45309' : '4px solid #b45309',
          animation: status === 'streaming' || status === 'connecting' ? 'spin 1s linear infinite' : 'none',
          marginBottom: 28,
          fontSize: status === 'done' ? 28 : status === 'error' ? 28 : 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          {status === 'done' && <span style={{ fontSize: 24 }}>✓</span>}
          {status === 'error' && <span style={{ fontSize: 24 }}>✗</span>}
        </div>

        {/* Title */}
        <p style={{ fontSize: 12, fontWeight: 700, color: '#b45309', letterSpacing: '0.15em', textTransform: 'uppercase', fontFamily: 'monospace', margin: '0 0 8px' }}>
          Crafting Your Tour
        </p>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: '#1a1a1a', margin: '0 0 8px', letterSpacing: '-0.5px', textAlign: 'center' }}>
          {siteName}
        </h1>
        <p style={{ fontSize: 14, color: '#9ca3af', fontFamily: 'monospace', margin: '0 0 40px', textAlign: 'center' }}>
          {durationMins} minute tour · AI agents at work{status === 'streaming' ? dots : ''}
        </p>

        {/* Progress log */}
        <div style={{
          width: '100%', background: '#fff', border: '1px solid #f0ede8',
          borderRadius: 12, padding: '24px', minHeight: 200,
          boxShadow: '0 2px 12px rgba(0,0,0,0.05)',
        }}>
          {events.length === 0 && (
            <p style={{ color: '#d1d5db', fontSize: 13, fontFamily: 'monospace', margin: 0 }}>
              Initializing pipeline{dots}
            </p>
          )}
          {events.map((event, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, marginBottom: 12 }}>
              <span style={{
                fontSize: 13,
                color: event.startsWith('✗') ? '#ef4444' : event.startsWith('✓') || event.startsWith('⚡') ? '#b45309' : '#9ca3af',
                flexShrink: 0, marginTop: 1,
              }}>
                {event.startsWith('✗') ? '✗' : event.startsWith('✓') ? '✓' : event.startsWith('⚡') ? '⚡' : '·'}
              </span>
              <p style={{
                fontSize: 13, fontFamily: 'monospace', margin: 0,
                color: event.startsWith('✗') ? '#ef4444' : event.startsWith('✓') || event.startsWith('⚡') ? '#1a1a1a' : '#6b7280',
              }}>
                {event.replace(/^[✗✓⚡]\s*/, '')}
              </p>
            </div>
          ))}
          {status === 'streaming' && events.length > 0 && (
            <p style={{ color: '#d1d5db', fontSize: 13, fontFamily: 'monospace', margin: '4px 0 0' }}>
              Working{dots}
            </p>
          )}
          {status === 'done' && (
            <p style={{ color: '#b45309', fontSize: 13, fontFamily: 'monospace', margin: '8px 0 0', fontWeight: 600 }}>
              Redirecting to your tour{dots}
            </p>
          )}
        </div>

        {/* Status pill */}
        <div style={{ marginTop: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 8, height: 8, borderRadius: '50%',
            background: status === 'error' ? '#ef4444' : status === 'done' ? '#b45309' : '#b45309',
            opacity: status === 'streaming' || status === 'connecting' ? undefined : 1,
            animation: status === 'streaming' || status === 'connecting' ? 'pulse 1.5s ease-in-out infinite' : 'none',
          }} />
          <span style={{ fontSize: 12, color: '#9ca3af', fontFamily: 'monospace' }}>
            {status === 'connecting' && 'Connecting...'}
            {status === 'streaming' && 'Pipeline running'}
            {status === 'done' && 'Complete'}
            {status === 'error' && 'Failed'}
          </span>
        </div>

        {status === 'error' && (
          <button
            onClick={() => router.back()}
            style={{ marginTop: 24, background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8, padding: '10px 24px', fontSize: 14, color: '#6b7280', cursor: 'pointer' }}
          >
            ← Go Back
          </button>
        )}
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
        * { box-sizing: border-box; }
      `}</style>
    </div>
  );
}

export default function GeneratingPage() {
  return (
    <Suspense>
      <GeneratingContent />
    </Suspense>
  );
}
