import React, { useState, useEffect } from 'react';
import mapboxgl from 'mapbox-gl';

mapboxgl.accessToken = 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4M29iazA2Z2gycXA4N2pmbDZmangifQ.-g_vE53SD2WrJ6tFX7QHmA';

const StanfordMap = () => {
    const [map, setMap] = useState(null);

    useEffect(() => {
        const initializeMap = () => {
            const map = new mapboxgl.Map({
                container: 'map',
                style: 'mapbox://styles/mapbox/streets-v11',
                center: [-122.1708, 37.4241],
                zoom: 13
            });

            // Add markers for local businesses
            const localBusinesses = [
                {
                    name: 'Stanford Coffee',
                    location: [-122.1679, 37.4276],
                    product: 'Latte',
                    price: '$4.50',
                    image: 'https://example.com/latte.jpg'
                },
                {
                    name: 'Hobee\'s',
                    location: [-122.1824, 37.4454],
                    product: 'Pancakes',
                    price: '$9.99',
                    image: 'https://example.com/pancakes.jpg'
                },
                // Add more local businesses here
            ];

            localBusinesses.forEach((business) => {
                const popupHtml = `
          <div>
            <h3>${business.name}</h3>
            <img src="${business.image}" alt="${business.product}" style="width: 100%; max-width: 300px;">
            <p><strong>Price:</strong> ${business.price}</p>
            <button>Buy now</button>
          </div>
        `;

                new mapboxgl.Marker()
                    .setLngLat(business.location)
                    .setPopup(new mapboxgl.Popup().setHTML(popupHtml))
                    .addTo(map);
            });

            setMap(map);
        };

        if (!map) {
            initializeMap();
        }
    }, [map]);

    return <div id="map" style={{ height: '500px' }} />;
};

export default StanfordMap;
