import axios from 'axios';

// Configure Axios Defaults for Production (Vercel) -> Backend (Render)
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || '';

// Pseudo-random gaussian for simulated nodes in case backend metrics are sparse
export const randomGauss = (mean, stdev) => {
    let u = 1 - Math.random();
    let v = Math.random();
    let z = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
    return z * stdev + mean;
};

export const getColor = (csi) => {
    if (csi < 0.5) {
        const r = Math.floor((csi / 0.5) * 255);
        const g = Math.floor(255 - (csi / 0.5) * 60);
        return [r, g, 60];
    } else {
        const r = 255;
        const g = Math.floor((1.0 - ((csi - 0.5) / 0.5)) * 200);
        return [r, g, 60];
    }
};

/**
 * Fetch Native H3 Cell arrays and Geometric Center directly from the Python Backend instance.
 * Completely offloads the heavy `h3-js` polyfill math from the client.
 */
export const getCityHexes = async (cityName, stateName, countryName, resolution = 8) => {
    try {
        const url = `/api/v1/locations/hexes?city=${encodeURIComponent(cityName)}&state=${encodeURIComponent(stateName)}&country=${encodeURIComponent(countryName)}&resolution=${resolution}`;
        const response = await axios.get(url);
        return response.data; // { hexes: ['89...', ...], center: [lat, lng] }
    } catch (e) {
        console.error("Backend Geometry Engine unavailable, crashing gracefully.", e);
        return { hexes: [], center: null };
    }
};

// Exposing API Fetchers
export const fetchCountries = async () => {
    const res = await axios.get('/api/v1/locations/countries');
    return res.data;
};

export const fetchStates = async (country) => {
    const res = await axios.get(`/api/v1/locations/states?country=${encodeURIComponent(country)}`);
    return res.data;
};

export const fetchCities = async (country, state) => {
    const res = await axios.get(`/api/v1/locations/cities?country=${encodeURIComponent(country)}&state=${encodeURIComponent(state)}`);
    return res.data;
};
