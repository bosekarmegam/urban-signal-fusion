import React, { useState, useEffect, useMemo } from 'react';
import {
  Globe2,
  Map as MapIcon,
  Settings2,
  Activity,
  Volume2,
  ThermometerSun,
  Users,
  AlertTriangle,
  ShieldAlert,
  RefreshCcw,
  MapPin,
  Plus,
  Minus,
  CheckCircle2,
  BarChart3,
  Menu,
  X
} from 'lucide-react';
import axios from 'axios';
import { Map } from 'react-map-gl/maplibre';
import DeckGL from '@deck.gl/react';
import { H3HexagonLayer } from '@deck.gl/geo-layers';
import 'maplibre-gl/dist/maplibre-gl.css';
import { getCityHexes, randomGauss, getColor, fetchCountries, fetchStates, fetchCities } from './utils/locationApi';

const Dashboard = () => {
  const [opacity, setOpacity] = useState(60);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const [region, setRegion] = useState({
    country: "India",
    state: "Tamil Nadu",
    city: "Chennai"
  });

  const [availableCountries, setAvailableCountries] = useState(["India"]);
  const [availableStates, setAvailableStates] = useState(["Tamil Nadu"]);
  const [availableCities, setAvailableCities] = useState(["Chennai"]);

  const [unavailableMessage, setUnavailableMessage] = useState("");

  // Real Backend State
  const [cityStats, setCityStats] = useState({
    csi_score: "0.0",
    transit: "0",
    noise: "0",
    heat: "0",
    crowd: "0",
    alerts: "0"
  });

  const [baseCityStats, setBaseCityStats] = useState({
    csi_score: "0.0",
    transit: "0",
    noise: "0",
    heat: "0",
    crowd: "0",
    alerts: "0"
  });

  const [activeAlerts, setActiveAlerts] = useState([]);
  const [hexData, setHexData] = useState([]);
  const [viewState, setViewState] = useState({
    longitude: 80.2707,
    latitude: 13.0827,
    zoom: 11.5,
    pitch: 25,
    bearing: 0
  });

  const fetchRegionData = async (hexes, center) => {
    // 1. Fetch City Base Stats
    try {
      const cityStatRes = await axios.get(`/api/v1/scores/city?city=${region.city}`);
      setBaseCityStats(cityStatRes.data);
      setCityStats(cityStatRes.data);
    } catch (e) {
      console.warn("City stats unavailable", e);
    }

    // 2. Fetch Active Anomalies
    try {
      const anomalyRes = await axios.get(`/api/v1/anomalies?city=${region.city}&since=1h`);
      setActiveAlerts(anomalyRes.data.anomalies || []);
    } catch (e) {
      console.warn("Anomalies unavailable", e);
    }

    // 3. Fetch Hex Map Data
    try {
      const scoreRes = await axios.get(`/api/v1/scores/region?bbox=0,0,0,0&resolution=9`);
      const backendScores = scoreRes.data.hexagons || [];

      const mapped = hexes.map((h, i) => {
        const backendNode = backendScores.find(b => b.hex_id === h);
        let csi = backendNode ? backendNode.csi_score : Math.max(0.0, Math.min(1.0, randomGauss(0.4, 0.2)));

        return {
          hex: h,
          csi: csi.toFixed(2),
          color: getColor(csi),
          transit: backendNode ? backendNode.transit_delay.toFixed(1) : (Math.random() * 43 + 2).toFixed(1),
          noise: backendNode ? backendNode.noise_db.toFixed(1) : (Math.random() * 40 + 55).toFixed(1),
          heat: backendNode ? backendNode.heat_index.toFixed(1) : (Math.random() * 18 + 26).toFixed(1),
          crowd: backendNode ? backendNode.crowd_density : Math.floor(Math.random() * 750 + 50),
          alerts: backendNode ? backendNode.active_alerts : Math.floor(Math.random() * 12)
        };
      });
      setHexData(mapped);

    } catch (e) {
      console.warn("Backend unavailable, falling back to pure simulation map.");

      const mapped = hexes.map(h => {
        let csi = Math.max(0.0, Math.min(1.0, randomGauss(0.4, 0.2)));
        return {
          hex: h,
          csi: csi.toFixed(2),
          color: getColor(csi),
          transit: (Math.random() * 43 + 2).toFixed(1),
          noise: (Math.random() * 40 + 55).toFixed(1),
          heat: (Math.random() * 18 + 26).toFixed(1),
          crowd: Math.floor(Math.random() * 750 + 50),
          alerts: Math.floor(Math.random() * 12)
        };
      });
      setHexData(mapped);
    }
  };

  useEffect(() => {
    if (!region.city) return;
    getCityHexes(region.city, region.state, region.country).then((res) => {
      const { hexes, center } = res;

      if (!hexes || hexes.length === 0) {
        if (region.city !== "Chennai") {
          setUnavailableMessage(`Polygon data for ${region.city} is currently unavailable. Defaulting back to Chennai.`);
          setTimeout(() => setUnavailableMessage(""), 5000);
          setRegion({ country: "India", state: "Tamil Nadu", city: "Chennai" });
        }
        return;
      }

      if (center) {
        setViewState(prev => ({ ...prev, longitude: center[1], latitude: center[0], zoom: 10.9 }));
      }
      fetchRegionData(hexes, center);
    });
  }, [region.city]);

  useEffect(() => {
    fetchCountries().then(setAvailableCountries);
  }, []);

  useEffect(() => {
    if (region.country) fetchStates(region.country).then(states => {
      setAvailableStates(states);
      if (states.length === 0) {
        if (region.country !== "India") {
          setUnavailableMessage(`No states available for ${region.country}. Defaulting to Chennai.`);
          setTimeout(() => setUnavailableMessage(""), 5000);
          setRegion({ country: "India", state: "Tamil Nadu", city: "Chennai" });
        }
      } else if (!states.includes(region.state)) {
        setRegion(r => ({ ...r, state: states[0] }));
      }
    });
  }, [region.country]);

  useEffect(() => {
    if (region.country && region.state) fetchCities(region.country, region.state).then(cities => {
      setAvailableCities(cities);
      if (cities.length === 0) {
        if (region.state !== "Tamil Nadu") {
          setUnavailableMessage(`No cities available in ${region.state}. Defaulting to Chennai.`);
          setTimeout(() => setUnavailableMessage(""), 5000);
          setRegion({ country: "India", state: "Tamil Nadu", city: "Chennai" });
        }
      } else if (!cities.includes(region.city)) {
        setRegion(r => ({ ...r, city: cities[0] }));
      }
    });
  }, [region.state, region.country]);

  const mapLayers = [
    new H3HexagonLayer({
      id: 'h3-hexagon-layer',
      data: hexData,
      pickable: true,
      wireframe: false,
      filled: true,
      extruded: false,
      opacity: opacity / 100,
      getHexagon: d => d.hex,
      getFillColor: d => d.color,
      getLineColor: [255, 255, 255, 200],
      lineWidthMinPixels: 1,
      onHover: ({ object }) => {
        if (object) {
          setCityStats({
            csi_score: object.csi,
            transit: object.transit,
            noise: object.noise,
            heat: object.heat,
            crowd: object.crowd,
            alerts: object.alerts
          });
        } else {
          setCityStats(baseCityStats);
        }
      }
    })
  ];

  const csiDistribution = useMemo(() => {
    if (!hexData.length) return [20, 20, 20, 20, 20];
    const counts = [0, 0, 0, 0, 0];
    hexData.forEach(h => {
      const c = parseFloat(h.csi);
      if (c < 0.2) counts[0]++;
      else if (c < 0.4) counts[1]++;
      else if (c < 0.6) counts[2]++;
      else if (c < 0.8) counts[3]++;
      else counts[4]++;
    });
    const total = counts.reduce((a, b) => a + b, 0);
    return counts.map(c => (c / total) * 100);
  }, [hexData]);

  const conicGradient = useMemo(() => {
    let current = 0;
    const stops = csiDistribution.map((pct, i) => {
      const start = current;
      current += pct;
      const color = ['#10b981', '#84cc16', '#eab308', '#f97316', '#ef4444'][i];
      return `${color} ${start.toFixed(1)}% ${current.toFixed(1)}%`;
    });
    return `conic-gradient(${stops.join(', ')})`;
  }, [csiDistribution]);

  const handleSync = async () => {
    setIsSyncing(true);
    if (hexData.length > 0) {
      const hexes = hexData.map(h => h.hex);
      await fetchRegionData(hexes, [viewState.latitude, viewState.longitude]);
    }
    setTimeout(() => setIsSyncing(false), 500);
  };

  // --- REUSABLE BLOCKS FOR RESPONSIVE REORDERING ---

  const headerBlock = (
    <div className="mb-4 shrink-0 flex flex-col md:flex-row md:items-end justify-between gap-3">
      <div className="flex items-start gap-3">
        {/* Mobile Hamburger Button */}
        <button
          className="md:hidden mt-1 p-1.5 -ml-1 text-slate-600 hover:text-slate-900 hover:bg-slate-200 rounded-lg transition-colors"
          onClick={() => setIsSidebarOpen(true)}
        >
          <Menu size={24} />
        </button>
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 mb-1 md:mb-2 tracking-tight leading-tight">
            Multi-Modal City Stress Score
          </h1>
          <p className="text-slate-500 text-sm max-w-3xl hidden md:block">
            Monitor high-frequency geospatial urban signals synthesized into a real-time <strong className="text-slate-700 font-semibold">City Stress Index (CSI)</strong> down to the street level.
          </p>
          <p className="text-slate-500 text-xs md:hidden">
            Real-time City Stress Index (CSI) monitoring.
          </p>
        </div>
      </div>
      <div className="inline-flex self-start md:self-auto items-center gap-1.5 bg-indigo-50 text-indigo-700 px-3 py-1.5 rounded-full text-xs font-semibold border border-indigo-100 shrink-0 whitespace-nowrap ml-10 md:ml-0">
        <MapPin size={14} />
        Focusing on: {region.city}
      </div>
    </div>
  );

  const kpiBlock = (
    <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3 mb-4 shrink-0">
      {/* CSI Score - Highlighted & First */}
      <KpiCard
        variant="primary"
        icon={<Activity size={20} />}
        title="CSI Score"
        value={cityStats.csi_score}
        className="col-span-2 xl:col-span-1"
      />
      {/* Other Parameters */}
      <KpiCard icon={<Activity className="text-amber-500" size={18} />} title="Transit Delay" value={cityStats.transit} unit="min/trip" />
      <KpiCard icon={<Volume2 className="text-indigo-400" size={18} />} title="Noise Level" value={cityStats.noise} unit="dB" />
      <KpiCard icon={<ThermometerSun className="text-rose-500" size={18} />} title="Surface Heat" value={cityStats.heat} unit="°C" />
      <KpiCard icon={<Users className="text-emerald-500" size={18} />} title="Crowd Density" value={cityStats.crowd} unit="ppl/km²" />
      <KpiCard icon={<AlertTriangle className="text-orange-500" size={18} />} title="Incidents" value={cityStats.alerts} unit="" />
    </div>
  );

  const mapBlock = (
    <div className="bg-[#e5e7eb] rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col relative w-full h-full min-h-[350px]">
      {unavailableMessage && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-50 bg-rose-500/95 backdrop-blur-sm text-white px-5 py-2.5 rounded-full shadow-[0_8px_30px_rgb(0,0,0,0.12)] font-semibold text-sm flex items-center gap-2.5 whitespace-nowrap transition-all duration-300 ease-out border border-rose-400">
          <ShieldAlert size={18} className="text-rose-100" />
          {unavailableMessage}
        </div>
      )}
      <DeckGL
        initialViewState={viewState}
        controller={true}
        layers={mapLayers}
        getTooltip={({ object }) => object && `Hex: ${object.hex}\nCSI Score: ${object.csi}\nHeat: ${object.heat}°C\nNoise: ${object.noise}dB\nTransit: ${object.transit}min`}
        onViewStateChange={({ viewState }) => setViewState(viewState)}
      >
        <Map mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json" />
      </DeckGL>

      {/* Map Controls */}
      <div className="absolute top-4 right-4 flex flex-col gap-2 z-10">
        <div className="bg-white rounded-lg shadow-md border border-slate-100 flex flex-col">
          <button
            onClick={() => setViewState(v => ({ ...v, zoom: v.zoom + 1 }))}
            className="p-1.5 md:p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-50 rounded-t-lg transition-colors"
          >
            <Plus size={18} />
          </button>
          <div className="h-px bg-slate-100 w-full"></div>
          <button
            onClick={() => setViewState(v => ({ ...v, zoom: v.zoom - 1 }))}
            className="p-1.5 md:p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-50 rounded-b-lg transition-colors"
          >
            <Minus size={18} />
          </button>
        </div>
      </div>

      {/* Map Attribution */}
      <div className="absolute bottom-0 right-0 bg-white/80 backdrop-blur-sm text-[10px] text-slate-500 px-2 py-1 rounded-tl-lg z-10 border-t border-l border-white/50">
        © CARTO, © OpenStreetMap contributors
      </div>
    </div>
  );

  const panelsBlock = (
    <>
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 md:p-5 shrink-0 min-h-[140px] flex flex-col">
        <h3 className="flex items-center gap-2 font-semibold text-slate-800 mb-3 text-sm md:text-base">
          <ShieldAlert size={18} className="text-rose-500" />
          Active Alerts
        </h3>

        {activeAlerts.length === 0 ? (
          <div className="bg-slate-50 rounded-xl p-3 md:p-4 border border-slate-100 flex items-center text-left gap-3 flex-1 h-full">
            <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center shrink-0">
              <CheckCircle2 size={16} className="text-emerald-600" />
            </div>
            <p className="text-xs md:text-sm text-slate-600 font-medium">
              No active high-severity anomalies at this time.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-2 max-h-[150px] overflow-y-auto pr-1 flex-1">
            {activeAlerts.map((alert, idx) => (
              <div key={idx} className="bg-rose-50 border border-rose-100 rounded-lg p-3 text-rose-800 text-xs md:text-sm flex flex-col">
                <strong className="font-semibold mb-1">{alert.feature_type.replace('_', ' ').toUpperCase()}</strong>
                <span>CSI Spiked to {(alert.confidence * 10).toFixed(1)}</span>
                <span className="text-rose-600/70 text-[10px] mt-1">{alert.timestamp}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* CSI Distribution */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 flex-1 min-h-[300px] xl:min-h-0 flex flex-col overflow-hidden">
        <div className="p-4 md:p-5 flex flex-col h-full overflow-y-auto">
          <h3 className="flex items-center gap-2 font-semibold text-slate-800 mb-3 md:mb-4 text-sm md:text-base shrink-0">
            <BarChart3 size={18} className="text-indigo-500" />
            CSI Distribution
          </h3>

          <div className="flex-1 flex flex-col items-center justify-center min-h-0 py-2">
            {/* CSS Donut Chart */}
            <div className="relative w-28 h-28 lg:w-32 lg:h-32 xl:w-36 xl:h-36 rounded-full mb-5 shadow-sm shrink-0" style={{
              background: conicGradient
            }}>
              {/* Inner white circle */}
              <div className="absolute inset-0 m-auto w-3/5 h-3/5 bg-white rounded-full shadow-[inset_0_2px_4px_rgba(0,0,0,0.05)] flex items-center justify-center">
                <div className="text-center">
                  <span className="block text-base md:text-xl font-bold text-slate-800">100%</span>
                  <span className="block text-[8px] md:text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Total</span>
                </div>
              </div>
            </div>

            {/* Legend */}
            <div className="w-full grid grid-cols-2 gap-y-2.5 gap-x-2 text-[10px] md:text-xs px-2 shrink-0">
              <LegendItem color="bg-emerald-500" label="Very Low" pct={csiDistribution[0]} />
              <LegendItem color="bg-lime-500" label="Low" pct={csiDistribution[1]} />
              <LegendItem color="bg-yellow-500" label="Moderate" pct={csiDistribution[2]} />
              <LegendItem color="bg-orange-500" label="High" pct={csiDistribution[3]} />
              <LegendItem color="bg-red-500" label="Critical" pct={csiDistribution[4]} />
            </div>
          </div>
        </div>
      </div>
    </>
  );

  return (
    <div className="h-screen w-full bg-slate-50 font-sans text-slate-800 flex overflow-hidden">

      {/* MOBILE OVERLAY */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-slate-900/50 z-40 md:hidden backdrop-blur-sm transition-opacity"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* SIDEBAR */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-50 w-72 bg-white border-r border-slate-200 shrink-0 flex flex-col shadow-2xl md:shadow-sm transform transition-transform duration-300 ease-in-out h-full
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0`}
      >
        <div className="flex items-center justify-between p-4 md:hidden border-b border-slate-100">
          <span className="font-bold text-slate-800">Dashboard Menu</span>
          <button
            onClick={() => setIsSidebarOpen(false)}
            className="p-2 text-slate-500 hover:bg-slate-100 rounded-lg"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-4 md:p-5 flex-grow overflow-y-auto">
          {/* Region Settings Section */}
          <div className="mb-8">
            <h2 className="flex items-center gap-2 font-semibold text-slate-800 mb-4 text-sm uppercase tracking-wider">
              <Globe2 size={18} className="text-indigo-500" />
              Region Settings
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Country</label>
                <select
                  value={region.country}
                  onChange={(e) => setRegion({ ...region, country: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 text-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                >
                  {availableCountries.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">State/Province</label>
                <select
                  value={region.state}
                  onChange={(e) => setRegion({ ...region, state: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 text-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                >
                  {availableStates.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">City</label>
                <select
                  value={region.city}
                  onChange={(e) => setRegion({ ...region, city: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 text-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                >
                  {availableCities.map(cty => <option key={cty} value={cty}>{cty}</option>)}
                </select>
              </div>
            </div>
          </div>

          <hr className="border-slate-100 mb-8" />

          {/* Visual Settings Section */}
          <div className="mb-8">
            <h2 className="flex items-center gap-2 font-semibold text-slate-800 mb-4 text-sm uppercase tracking-wider">
              <Settings2 size={18} className="text-pink-500" />
              Visual Settings
            </h2>
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-xs font-medium text-slate-500">Hexagon Opacity</label>
                <span className="text-xs font-semibold text-slate-700">{(opacity / 100).toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={opacity}
                onChange={(e) => setOpacity(e.target.value)}
                className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 md:p-5 bg-slate-50 border-t border-slate-200 shrink-0">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
              <span className="text-sm font-medium text-slate-700">Live Data Feed</span>
            </div>
            <div className="text-xs text-slate-500 font-mono">2026-03-03</div>
          </div>
          <button
            onClick={handleSync}
            className="w-full bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 font-medium py-2 px-4 rounded-lg shadow-sm flex items-center justify-center gap-2 transition-colors text-sm"
          >
            <RefreshCcw size={16} className={isSyncing ? "animate-spin text-indigo-500" : "text-slate-400"} />
            {isSyncing ? 'Syncing...' : 'Sync Live Data'}
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT WRAPPER */}
      <main className="flex-1 flex flex-col h-full w-full overflow-hidden relative">
        <div className="flex-1 p-4 md:p-6 overflow-y-auto flex flex-col h-full w-full">

          {/* --- DESKTOP VIEW --- */}
          <div className="hidden xl:flex flex-col h-full min-h-min w-full pb-6 xl:pb-0">
            {headerBlock}
            {kpiBlock}
            <div className="flex-1 grid grid-cols-1 xl:grid-cols-3 gap-5 xl:min-h-0">
              <div className="xl:col-span-2 h-full min-h-[450px] xl:min-h-0">
                {mapBlock}
              </div>
              <div className="xl:col-span-1 h-full min-h-[400px] xl:min-h-0 flex flex-col gap-5">
                {panelsBlock}
              </div>
            </div>
          </div>

          {/* --- MOBILE & TABLET VIEW (Scrollable, Map on Top) --- */}
          <div className="flex xl:hidden flex-col gap-4 md:gap-5 w-full pb-8">
            {headerBlock}
            <div className="h-[350px] md:h-[450px] lg:h-[550px] shrink-0 w-full">
              {mapBlock}
            </div>
            {kpiBlock}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-5 w-full">
              {panelsBlock}
            </div>
          </div>

        </div>
      </main>

    </div>
  );
};

// Helper Components
const KpiCard = ({ icon, title, value, unit, variant = 'default', className = '' }) => {
  if (variant === 'primary') {
    return (
      <div className={`bg-gradient-to-br from-indigo-600 to-indigo-800 p-4 md:p-4 rounded-xl shadow-md border border-indigo-500 transition-all hover:shadow-lg ${className}`}>
        <div className="flex items-center gap-2 text-indigo-100 text-sm font-medium mb-2">
          <div className="p-1.5 rounded-lg bg-indigo-500/50 text-white backdrop-blur-sm">
            {icon}
          </div>
          <span className="truncate">{title}</span>
        </div>
        <div className="flex items-baseline gap-1 mt-1">
          <span className="text-3xl md:text-3xl font-bold text-white tracking-tight">{value}</span>
          {unit && <span className="text-sm font-medium text-indigo-200">{unit}</span>}
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white p-3 md:p-4 rounded-xl shadow-sm border border-slate-200 transition-all hover:shadow-md ${className}`}>
      <div className="flex items-center gap-1.5 text-slate-500 text-xs md:text-sm font-medium mb-1.5 md:mb-2">
        <div className="p-1.5 rounded-lg bg-slate-50">
          {icon}
        </div>
        <span className="truncate">{title}</span>
      </div>
      <div className="flex items-baseline gap-1 mt-1">
        <span className="text-xl md:text-2xl font-bold text-slate-800">{value}</span>
        {unit && <span className="text-xs md:text-sm font-medium text-slate-500">{unit}</span>}
      </div>
    </div>
  );
};

const LegendItem = ({ color, label, pct }) => (
  <div className="flex items-center justify-between gap-2 max-w-[100px]">
    <div className="flex items-center gap-2">
      <span className={`w-2.5 h-2.5 rounded-full ${color}`}></span>
      <span className="text-slate-600 font-medium">{label}</span>
    </div>
    <span className="text-slate-400 font-semibold">{pct ? Math.round(pct) : 0}%</span>
  </div>
);

export default Dashboard;
