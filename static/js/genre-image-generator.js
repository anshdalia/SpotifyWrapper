const GENRE_GRADIENTS = {
    // Music Genres
    'pop': {
        gradient: ['#FF6B6B', '#4ECDC4'],
        textColor: '#ffffff',
        icon: 'microphone'
    },
    'rock': {
        gradient: ['#FF4E50', '#FC913A'],
        textColor: '#ffffff',
        icon: 'guitar'
    },
    'hip hop': {
        gradient: ['#000000', '#434343'],
        textColor: '#ffffff',
        icon: 'headphones'
    },
    'electronic': {
        gradient: ['#5E2595', '#A74FD1'],
        textColor: '#ffffff',
        icon: 'wave-sine'
    },
    'indie': {
        gradient: ['#8A2BE2', '#4B0082'],
        textColor: '#ffffff',
        icon: 'music'
    },
    'alternative': {
        gradient: ['#2C3E50', '#3498DB'],
        textColor: '#ffffff',
        icon: 'guitar-pick'
    },
    'r&b': {
        gradient: ['#833AB4', '#FE5858'],
        textColor: '#ffffff',
        icon: 'mic'
    },
    'classical': {
        gradient: ['#BDBDBD', '#757F9A'],
        textColor: '#ffffff',
        icon: 'violin'
    },
    'jazz': {
        gradient: ['#4ECDC4', '#556270'],
        textColor: '#ffffff',
        icon: 'saxophone'
    },
    'metal': {
        gradient: ['#232526', '#414345'],
        textColor: '#ffffff',
        icon: 'flame'
    },
    'folk': {
        gradient: ['#2C3E50', '#4CA1AF'],
        textColor: '#ffffff',
        icon: 'tree'
    },
    'country': {
        gradient: ['#FF7E5F', '#FEB47B'],
        textColor: '#ffffff',
        icon: 'boot'
    },
    'reggae': {
        gradient: ['#00B4DB', '#00F260'],
        textColor: '#ffffff',
        icon: 'peace'
    },
    'punk': {
        gradient: ['#CB356B', '#BD3F32'],
        textColor: '#ffffff',
        icon: 'skull'
    },
    // Fallback for unknown genres
    'default': {
        gradient: ['#00B4DB', '#0083B0'],
        textColor: '#ffffff',
        icon: 'music-note'
    }
};

function sanitizeGenre(genre) {
    // Convert to lowercase and handle common variations
    return genre.toLowerCase()
        .replace(/&/g, 'and')
        .replace(/[^a-z\s]/g, '')
        .trim();
}

function capitalizeGenre(genre) {
    // Split the genre into words and capitalize each word
    return genre.split(/\s+/)
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function findBestGenreMatch(genre) {
    const sanitizedGenre = sanitizeGenre(genre);

    // Exact match
    if (GENRE_GRADIENTS[sanitizedGenre]) {
        return sanitizedGenre;
    }

    // Partial match
    for (let key in GENRE_GRADIENTS) {
        if (sanitizedGenre.includes(key)) {
            return key;
        }
    }

    // If no match found, return default
    return 'default';
}

function generateGenreImage(genre, uniqueId) {
    // Capitalize the genre text
    const capitalizedGenre = capitalizeGenre(genre);

    // Find the best matching genre configuration
    const genreKey = findBestGenreMatch(genre);
    const genreConfig = GENRE_GRADIENTS[genreKey];

    // Create SVG dynamically
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 200 200");
    svg.setAttribute("width", "200");
    svg.setAttribute("height", "200");
    svg.classList.add("genre-image", "animate__animated", "animate__zoomIn");

    // Gradient definition with a unique ID
    const gradientId = `genreGradient-${uniqueId}`;
    const gradientEl = document.createElementNS("http://www.w3.org/2000/svg", "linearGradient");
    gradientEl.setAttribute("id", gradientId);
    gradientEl.innerHTML = `
        <stop offset="0%" stop-color="${genreConfig.gradient[0]}"/>
        <stop offset="100%" stop-color="${genreConfig.gradient[1]}"/>
    `;
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    defs.appendChild(gradientEl);
    svg.appendChild(defs);

    // Background rectangle using the unique gradient ID
    const bgRect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    bgRect.setAttribute("width", "200");
    bgRect.setAttribute("height", "200");
    bgRect.setAttribute("fill", `url(#${gradientId})`);
    svg.appendChild(bgRect);

    // Decorative circles
    const circles = [
        { cx: 50, cy: 50, r: 20 },
        { cx: 150, cy: 150, r: 15 }
    ];
    circles.forEach(circle => {
        const circleEl = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circleEl.setAttribute("cx", circle.cx);
        circleEl.setAttribute("cy", circle.cy);
        circleEl.setAttribute("r", circle.r);
        circleEl.setAttribute("fill", "rgba(255,255,255,0.2)");
        svg.appendChild(circleEl);
    });

    // Genre text
    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", "100");
    text.setAttribute("y", "100");
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("alignment-baseline", "middle");
    text.setAttribute("font-family", "Arial, sans-serif");
    text.setAttribute("font-weight", "bold");
    text.setAttribute("fill", genreConfig.textColor);
    text.setAttribute("font-size", capitalizedGenre.length > 12 ? "20" : "32");
    text.textContent = capitalizedGenre;
    svg.appendChild(text);

    return svg;
}

// Function to replace the genre image placeholder
function replaceGenreImage(genre) {
    const placeholder = document.querySelector('.genre-image');
    if (placeholder) {
        const newSvg = generateGenreImage(genre);
        placeholder.parentNode.replaceChild(newSvg, placeholder);
    }
}
