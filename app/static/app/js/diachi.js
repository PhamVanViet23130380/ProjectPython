// Address Page Script - With Vietnam Provinces and Leaflet Map
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const citySelect = document.getElementById('citySelect');
    const districtSelect = document.getElementById('districtSelect');
    const streetInput = document.getElementById('streetInput');
    const nextBtn = document.getElementById('nextBtn');
    const findOnMapBtn = document.getElementById('findOnMap');
    const addressPreview = document.getElementById('addressPreview');
    const fullAddressText = document.getElementById('fullAddressText');
    const mapLoading = document.getElementById('mapLoading');
    const latitudeInput = document.getElementById('latitudeInput');
    const longitudeInput = document.getElementById('longitudeInput');

    // Map variables
    let map = null;
    let marker = null;
    let mapInitialized = false;

    // ============ POPULATE PROVINCES ============
    function populateProvinces() {
        // Clear existing options
        citySelect.innerHTML = '<option value="">-- Chọn Tỉnh/Thành phố --</option>';
        
        // Add provinces sorted alphabetically
        sortedProvinces.forEach(province => {
            const option = document.createElement('option');
            option.value = province;
            option.textContent = province;
            citySelect.appendChild(option);
        });
    }

    // ============ POPULATE DISTRICTS ============
    function populateDistricts(province) {
        // Clear existing options
        districtSelect.innerHTML = '<option value="">-- Chọn Quận/Huyện --</option>';
        
        if (!province || !vietnamProvinces[province]) {
            districtSelect.disabled = true;
            return;
        }

        // Enable and populate districts
        districtSelect.disabled = false;
        const districts = vietnamProvinces[province].sort((a, b) => a.localeCompare(b, 'vi'));
        
        districts.forEach(district => {
            const option = document.createElement('option');
            option.value = district;
            option.textContent = district;
            districtSelect.appendChild(option);
        });
    }

    // ============ INITIALIZE MAP ============
    function initMap() {
        if (mapInitialized) return;
        
        // Default center: Ho Chi Minh City
        const defaultLat = 10.8231;
        const defaultLng = 106.6297;
        
        map = L.map('map').setView([defaultLat, defaultLng], 13);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        // Custom marker icon
        const customIcon = L.divIcon({
            className: 'custom-marker',
            html: '<i class="fa-solid fa-location-dot" style="font-size: 32px; color: #8B4513;"></i>',
            iconSize: [32, 32],
            iconAnchor: [16, 32]
        });

        // Add draggable marker
        marker = L.marker([defaultLat, defaultLng], {
            draggable: true,
            icon: customIcon
        }).addTo(map);

        // Update coordinates when marker is dragged
        marker.on('dragend', function(e) {
            const pos = marker.getLatLng();
            updateCoordinates(pos.lat, pos.lng);
            reverseGeocode(pos.lat, pos.lng);
        });

        // Click on map to move marker
        map.on('click', function(e) {
            marker.setLatLng(e.latlng);
            updateCoordinates(e.latlng.lat, e.latlng.lng);
            reverseGeocode(e.latlng.lat, e.latlng.lng);
        });

        mapInitialized = true;
    }

    // ============ UPDATE COORDINATES ============
    function updateCoordinates(lat, lng) {
        latitudeInput.value = lat.toFixed(6);
        longitudeInput.value = lng.toFixed(6);
        validateForm();
    }

    // ============ GEOCODE ADDRESS ============
    async function geocodeAddress(address) {
        try {
            mapLoading.style.display = 'flex';
            
            const response = await fetch(
                `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&countrycodes=vn&limit=1`
            );
            const data = await response.json();
            
            if (data && data.length > 0) {
                const result = data[0];
                const lat = parseFloat(result.lat);
                const lng = parseFloat(result.lon);
                
                // Update map
                if (map && marker) {
                    map.setView([lat, lng], 16);
                    marker.setLatLng([lat, lng]);
                }
                
                updateCoordinates(lat, lng);
                return { lat, lng };
            } else {
                // If not found, try with just district and city
                const simpleAddress = `${districtSelect.value}, ${citySelect.value}, Vietnam`;
                const simpleResponse = await fetch(
                    `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(simpleAddress)}&countrycodes=vn&limit=1`
                );
                const simpleData = await simpleResponse.json();
                
                if (simpleData && simpleData.length > 0) {
                    const result = simpleData[0];
                    const lat = parseFloat(result.lat);
                    const lng = parseFloat(result.lon);
                    
                    if (map && marker) {
                        map.setView([lat, lng], 14);
                        marker.setLatLng([lat, lng]);
                    }
                    
                    updateCoordinates(lat, lng);
                    return { lat, lng };
                }
            }
            
            return null;
        } catch (error) {
            console.error('Geocoding error:', error);
            return null;
        } finally {
            mapLoading.style.display = 'none';
        }
    }

    // ============ REVERSE GEOCODE ============
    async function reverseGeocode(lat, lng) {
        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`
            );
            const data = await response.json();
            
            if (data && data.address) {
                // Update preview with reverse geocoded address
                const addr = data.address;
                const displayAddress = data.display_name || 'Địa chỉ không xác định';
                
                if (fullAddressText && addressPreview) {
                    addressPreview.style.display = 'block';
                    fullAddressText.innerHTML = `
                        <i class="fa-solid fa-map-marker-alt"></i> ${displayAddress}
                        <br><small style="color: #666;">Tọa độ: ${lat.toFixed(6)}, ${lng.toFixed(6)}</small>
                    `;
                }
            }
        } catch (error) {
            console.error('Reverse geocoding error:', error);
        }
    }

    // ============ UPDATE ADDRESS PREVIEW ============
    function updateAddressPreview() {
        const city = citySelect.value;
        const district = districtSelect.value;
        const street = streetInput.value.trim();
        
        if (city && district && street) {
            const fullAddress = `${street}, ${district}, ${city}`;
            addressPreview.style.display = 'block';
            fullAddressText.innerHTML = `<i class="fa-solid fa-map-marker-alt"></i> ${fullAddress}`;
        } else {
            addressPreview.style.display = 'none';
        }
    }

    // ============ VALIDATE FORM ============
    function validateForm() {
        const hasCity = citySelect.value !== '';
        const hasDistrict = districtSelect.value !== '';
        const hasStreet = streetInput.value.trim() !== '';
        const hasCoords = latitudeInput.value !== '' && longitudeInput.value !== '';
        
        const isValid = hasCity && hasDistrict && hasStreet;
        nextBtn.disabled = !isValid;
        
        return isValid;
    }

    // ============ EVENT LISTENERS ============
    
    // City select change
    citySelect.addEventListener('change', function() {
        populateDistricts(this.value);
        districtSelect.value = '';
        updateAddressPreview();
        validateForm();
    });

    // District select change
    districtSelect.addEventListener('change', function() {
        updateAddressPreview();
        validateForm();
    });

    // Street input change
    streetInput.addEventListener('input', function() {
        updateAddressPreview();
        validateForm();
    });

    // Find on map button
    findOnMapBtn.addEventListener('click', async function() {
        if (!mapInitialized) {
            initMap();
        }
        
        const city = citySelect.value;
        const district = districtSelect.value;
        const street = streetInput.value.trim();
        
        if (!city || !district) {
            alert('Vui lòng chọn Tỉnh/Thành phố và Quận/Huyện trước');
            return;
        }
        
        // Build full address
        let fullAddress = '';
        if (street) {
            fullAddress = `${street}, ${district}, ${city}, Vietnam`;
        } else {
            fullAddress = `${district}, ${city}, Vietnam`;
        }
        
        const result = await geocodeAddress(fullAddress);
        
        if (!result) {
            alert('Không tìm thấy địa chỉ trên bản đồ. Vui lòng kéo thả marker để xác định vị trí.');
        }
    });

    // Form submit
    document.getElementById('addressForm').addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            alert('Vui lòng điền đầy đủ thông tin địa chỉ');
            return false;
        }
        
        // Store in sessionStorage for multi-step form
        sessionStorage.setItem('listing_city', citySelect.value);
        sessionStorage.setItem('listing_district', districtSelect.value);
        sessionStorage.setItem('listing_street', streetInput.value);
        sessionStorage.setItem('listing_latitude', latitudeInput.value);
        sessionStorage.setItem('listing_longitude', longitudeInput.value);
    });

    // Help button
    document.querySelector('.btnThacMac')?.addEventListener('click', function() {
        alert('Liên hệ support: support@homenest.com');
    });

    // Exit button
    document.querySelector('.btnLuuThoat')?.addEventListener('click', function() {
        if (confirm('Bạn chắc chắn muốn thoát? Dữ liệu chưa lưu sẽ bị mất.')) {
            window.location.href = '/';
        }
    });

    // ============ INITIALIZATION ============
    populateProvinces();
    
    // Restore from sessionStorage if exists
    const savedCity = sessionStorage.getItem('listing_city');
    const savedDistrict = sessionStorage.getItem('listing_district');
    const savedStreet = sessionStorage.getItem('listing_street');
    const savedLat = sessionStorage.getItem('listing_latitude');
    const savedLng = sessionStorage.getItem('listing_longitude');
    
    if (savedCity) {
        citySelect.value = savedCity;
        populateDistricts(savedCity);
        
        if (savedDistrict) {
            districtSelect.value = savedDistrict;
        }
    }
    
    if (savedStreet) {
        streetInput.value = savedStreet;
    }
    
    if (savedLat && savedLng) {
        latitudeInput.value = savedLat;
        longitudeInput.value = savedLng;
    }
    
    updateAddressPreview();
    validateForm();
    
    // Initialize map after a short delay
    setTimeout(() => {
        initMap();
        
        // If we have saved coordinates, show them on map
        if (savedLat && savedLng) {
            const lat = parseFloat(savedLat);
            const lng = parseFloat(savedLng);
            if (map && marker) {
                map.setView([lat, lng], 16);
                marker.setLatLng([lat, lng]);
            }
        }
    }, 500);
});
