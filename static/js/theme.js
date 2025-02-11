const themes = {
    light: {
        '--main': '#2090f7',
        '--first': '#ffffff',
        '--second': '#121212',
        '--third': '#333333',
        '--fourth': '#ffffff',
        '--shadow': 'rgba(0, 0, 0, 0.1)',
        '--switch-icon': '🌞',
        '--map-color': 'mapbox://styles/mapbox/navigation-day-v1',
    },
    dark: {
        '--main': '#2090f7',
        '--first': '#121212',
        '--second': '#ffffff',
        '--third': '#333333',
        '--fourth': '#ffffff',
        '--shadow': 'rgba(255, 255, 255, 0.1)',
        '--switch-icon': '🌙',
        '--map-color': 'mapbox://styles/mapbox/navigation-night-v1',
    }
};

function applyTheme(themeName) {
    const theme = themes[themeName];
    if (!theme) return;

    Object.keys(theme).forEach(property => {
        document.documentElement.style.setProperty(property, theme[property]);
    });

    localStorage.setItem('theme', themeName);

    const slider = document.querySelector('.slider');
    if (slider) {
        slider.textContent = theme['--switch-icon'];
        slider.style.backgroundColor = theme['--second']; // Меняем фон
        slider.style.color = theme['--first']; // Меняем цвет текста
    }
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
}

function createThemeSwitch() {
    const switchContainer = document.getElementById('switch');
    if (!switchContainer) return;

    switchContainer.innerHTML = '';

    const slider = document.createElement('div');
    slider.classList.add('slider');
    slider.textContent = themes[localStorage.getItem('theme') || 'light']['--switch-icon'];
    slider.style.backgroundColor = getComputedStyle(document.documentElement).getPropertyValue('--second');
    slider.style.color = getComputedStyle(document.documentElement).getPropertyValue('--first');

    slider.addEventListener('click', () => {
        const newTheme = localStorage.getItem('theme') === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
    });

    switchContainer.appendChild(slider);

    // Добавляем стили динамически
    const style = document.createElement('style');
    style.textContent = `
        #switch {
            margin: 20px auto;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .slider {
            font-size: 18px;
            cursor: pointer;
            transition: background-color 0.3s, color 0.3s;
            padding: 10px;
            border-radius: 20px;
            text-align: center;
            user-select: none;
        }
    `;
    document.head.appendChild(style);
}
