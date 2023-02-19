import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import mapboxgl from 'mapbox-gl';

mapboxgl.accessToken = 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4M29iazA2Z2gycXA4N2pmbDZmangifQ.-g_vE53SD2WrJ6tFX7QHmA';

const StanfordMap = () => {
    const [map, setMap] = useState(null);
    const [markers, setMarkers] = useState([]);

    const handleClick = () => {
        handlePayment();
        // btn.removeEventListener("click", handleClick)
    }

    const handlePayment = (business) => {
        const settings = {
            async: true,
            crossDomain: true,
            url: 'http://localhost:8010/v3/check/digital',
            method: 'POST',
            headers: {
                accept: 'application/json',
                'content-type': 'application/json',
                Authorization: '0d5fa59be2a7785a5ac5a4f6605b27e5:2aa10eb20520941bca2c4687e53b0bfd'
            },
            processData: false,
            data: `{"recipient":"akotha12@gmail.com","name":"${business.name}","amount":${+(business.price.split('$')
            [1])},"description":"${business.product}"}`
        };

        $.ajax(settings).done(function (response) {
            console.log(response);
        });
    }

    useEffect(() => {
        const initializeMap = () => {
            const map = new mapboxgl.Map({
                container: 'map',
                style: 'mapbox://styles/mapbox/streets-v11',
                center: [-122.1708, 37.4391],
                zoom: 12.5,
            });

            // Add markers for local businesses
            const localBusinesses = [
                {
                    name: 'Stanford Coffee',
                    location: [-122.1679, 37.4276],
                    product: 'Coffee',
                    price: '$3.50',
                },
                {
                    name: "Hobee's",
                    location: [-122.1824, 37.4454],
                    product: 'Blueberry Coffee Cake',
                    price: '$4.95',
                },
                {
                    name: 'The Prolific Oven',
                    location: [-122.1664, 37.4449],
                    product: 'Chocolate Croissant',
                    price: '$3.95',
                },
                {
                    name: 'Coupa Cafe',
                    location: [-122.1708, 37.4276],
                    product: 'Chai Latte',
                    price: '$4.25',
                },
                {
                    name: 'The Cheese House',
                    location: [-122.1768, 37.4457],
                    product: 'Gourmet Cheese Plate',
                    price: '$15.99',
                },
                {
                    name: "Ike's Love & Sandwiches",
                    location: [-122.1765, 37.4485],
                    product: "The Famous Ike's Sandwich",
                    price: '$10.95',
                },
                {
                    name: "Scotty's Corner Pub",
                    location: [-122.1833, 37.4438],
                    product: 'Fish and Chips',
                    price: '$15.95',
                },
                {
                    name: 'Channing House',
                    location: [-122.1632, 37.4482],
                    product: 'Salmon Filet',
                    price: '$21.99',
                },
            ];


            localBusinesses.forEach((business) => {
                const div = document.createElement("div");
                console.log({ div })
                ReactDOM.render((
                    <div className="popup-content">
                        <h3>{business.name}</h3>
                        <p><strong>Price:</strong> {business.price}</p>
                        <button id="buy-now" onClick={e =>
                            handlePayment(business)
                            // alert("you bought { }")
                        }>Buy now</button>
                    </div >
                ), div)

                const marker = new mapboxgl.Marker()
                    .setLngLat(business.location)
                    .setPopup(new mapboxgl.Popup().setDOMContent(div))
                    .addTo(map);
                // Add event listener to each marker
                marker.getElement().addEventListener('click', () => {
                    marker.togglePopup();
                });
            });

            setMap(map);
        };

        if (!map) {
            initializeMap();
        }

        const btn = document.getElementsByClassName('btn')[0];
        // if (btn) {
        //     btn.addEventListener('click', () => {
        //         console.log('hi')
        //         handlePayment()
        //     })
        // }


    }, [map]);

    return <div id="map" style={{ height: '500px' }} />;
};

export default StanfordMap;