'use client';

import { useEffect, useRef, useState } from 'react';
import 'leaflet/dist/leaflet.css';

interface TourMapProps {
  geojson: object;
}

export default function TourMap({ geojson }: TourMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<unknown>(null);
  const [downloading, setDownloading] = useState(false);

  const downloadImage = async () => {
    if (!mapRef.current) return;
    setDownloading(true);
    const { toPng } = await import('html-to-image');
    const dataUrl = await toPng(mapRef.current, { cacheBust: true });
    const link = document.createElement('a');
    link.download = 'tour-map.png';
    link.href = dataUrl;
    link.click();
    setDownloading(false);
  };

  useEffect(() => {
    if (!mapRef.current) return;

    let cancelled = false;

    // Dynamically import Leaflet (client-side only)
    import('leaflet').then((L) => {
      if (cancelled || !mapRef.current || mapInstanceRef.current) return;
      // Fix default marker icons
      delete (L.Icon.Default.prototype as { _getIconUrl?: unknown })._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      });

      // Initialize map — fallback center on Iraq until fitBounds runs
      const map = L.map(mapRef.current!, {
        zoomControl: true,
        scrollWheelZoom: true,
        center: [33.0, 44.0],
        zoom: 7,
      });

      // Satellite imagery (ESRI World Imagery — no API key required)
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, USGS, AeroGRID, IGN & GIS Community',
        maxZoom: 19,
      }).addTo(map);

      // Custom amber marker icon
      const amberIcon = L.divIcon({
        className: '',
        html: `<div style="
          width: 28px; height: 28px;
          background: #b45309;
          border: 2px solid #fbbf24;
          border-radius: 50% 50% 50% 0;
          transform: rotate(-45deg);
          box-shadow: 0 2px 8px rgba(0,0,0,0.5);
        "></div>`,
        iconSize: [28, 28],
        iconAnchor: [14, 28],
        popupAnchor: [0, -30],
      });

      // Add GeoJSON layer
      const geoLayer = L.geoJSON(geojson as GeoJSON.GeoJsonObject, {
        style: (feature) => {
          if (feature?.geometry.type === 'LineString') {
            return {
              color: '#b45309',
              weight: 2,
              opacity: 0.7,
              dashArray: '6, 4',
            };
          }
          return {};
        },
        pointToLayer: (_feature, latlng) => {
          return L.marker(latlng, { icon: amberIcon });
        },
        onEachFeature: (feature, layer) => {
          if (feature.geometry.type === 'Point') {
            const props = feature.properties;
            layer.bindTooltip(
              `<div style="font-family: monospace; font-size: 11px; color: #fbbf24; background: #1c1917; border: 1px solid #b45309; padding: 3px 7px; white-space: nowrap;">
                <span style="color: #b45309; margin-right: 4px;">${String(props.stop_number).padStart(2, '0')}</span>${props.name}
              </div>`,
              { permanent: true, direction: 'right', offset: [12, 0], className: 'tour-label' }
            );
          }
        },
      }).addTo(map);

      // Fit map to show all stops, with extra right padding for tooltip labels
      const bounds = geoLayer.getBounds();
      if (bounds.isValid()) {
        map.fitBounds(bounds, {
          paddingTopLeft: [20, 40],
          paddingBottomRight: [200, 40],
          maxZoom: 16,
        });
      }

      mapInstanceRef.current = map;
    });

    return () => {
      cancelled = true;
      if (mapInstanceRef.current) {
        (mapInstanceRef.current as { remove: () => void }).remove();
        mapInstanceRef.current = null;
      }
    };
  }, [geojson]);

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <style>{`
        .tour-label { background: transparent !important; border: none !important; box-shadow: none !important; }
        .tour-label::before { display: none !important; }
      `}</style>
      <div ref={mapRef} style={{ width: '100%', height: '100%' }} />
      <button
        onClick={downloadImage}
        disabled={downloading}
        style={{
          position: 'absolute',
          bottom: '10px',
          left: '10px',
          zIndex: 1000,
        }}
        className="bg-stone-900/90 border border-stone-700 text-amber-500 hover:text-amber-400 text-xs font-mono px-3 py-1.5 transition-colors disabled:opacity-50"
      >
        {downloading ? 'Saving...' : '↓ Save as Image'}
      </button>
    </div>
  );
}
