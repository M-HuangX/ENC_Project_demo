class ModelViewer {
    constructor() {
        // State
        this.models = [];
        this.files = [];
        this.currentIndex = 0;
        this.cache = new Map();

        // DOM Elements
        this.elements = {
            model1Select: document.getElementById('model1Select'),
            model2Select: document.getElementById('model2Select'),
            fileSelect: document.getElementById('fileSelect'),
            prevBtn: document.getElementById('prevBtn'),
            nextBtn: document.getElementById('nextBtn'),
            imageDisplay: document.getElementById('imageDisplay'),
            keywordsDisplay: document.getElementById('keywordsDisplay'),
            model1Display: document.getElementById('model1Display'),
            model2Display: document.getElementById('model2Display'),
            model1Header: document.getElementById('model1Header'),
            model2Header: document.getElementById('model2Header')
        };

        // Bind event listeners
        this.bindEvents();
    }

    bindEvents() {
        this.elements.fileSelect.addEventListener('change', () => this.loadContent());
        this.elements.model1Select.addEventListener('change', () => this.updateContent());
        this.elements.model2Select.addEventListener('change', () => this.updateContent());
        this.elements.prevBtn.addEventListener('click', () => this.navigate('prev'));
        this.elements.nextBtn.addEventListener('click', () => this.navigate('next'));
    }

    async initialize() {
        try {
            // Load models and files lists
            await Promise.all([
                this.loadModels(),
                this.loadFiles()
            ]);

            // Load initial content
            if (this.files.length > 0) {
                this.loadContent();
            }
        } catch (error) {
            console.error('Initialization error:', error);
            this.showError('Failed to initialize the viewer');
        }
    }

    async loadModels() {
        const response = await fetch('data/models.json');
        this.models = await response.json();
        
        // Populate model selects
        this.elements.model1Select.innerHTML = this.models
            .map(model => `<option value="${model}">${model}</option>`)
            .join('');
        
        this.elements.model2Select.innerHTML = this.models
            .map(model => `<option value="${model}">${model}</option>`)
            .join('');
        
        // Select different models by default if possible
        if (this.models.length > 1) {
            this.elements.model2Select.selectedIndex = 1;
        }
    }

    async loadFiles() {
        const response = await fetch('data/files.json');
        this.files = await response.json();
        
        this.elements.fileSelect.innerHTML = this.files
            .map(file => `<option value="${file}">${file}</option>`)
            .join('');
    }

    async loadContent() {
        const filename = this.elements.fileSelect.value;
        this.currentIndex = this.files.indexOf(filename);
        
        // Update navigation buttons
        this.elements.prevBtn.disabled = this.currentIndex === 0;
        this.elements.nextBtn.disabled = this.currentIndex === this.files.length - 1;

        // Update image
        this.elements.imageDisplay.src = `data/images/${filename}`;

        // Update analysis results
        await this.updateContent();
    }

    async updateContent() {
        const filename = this.elements.fileSelect.value;
        const model1 = this.elements.model1Select.value;
        const model2 = this.elements.model2Select.value;

        // Update headers
        this.elements.model1Header.textContent = `${model1} Analysis`;
        this.elements.model2Header.textContent = `${model2} Analysis`;

        try {
            // Load keywords
            await this.loadKeywords(filename);

            // Load model results
            await Promise.all([
                this.loadModelResults(filename, model1, this.elements.model1Display),
                this.loadModelResults(filename, model2, this.elements.model2Display)
            ]);
        } catch (error) {
            console.error('Error updating content:', error);
            this.showError('Failed to load analysis results');
        }
    }

    async loadKeywords(filename) {
        const baseName = filename.split('.')[0];
        const cacheKey = `keywords_${baseName}`;

        try {
            let data;
            if (this.cache.has(cacheKey)) {
                data = this.cache.get(cacheKey);
            } else {
                const response = await fetch(`data/keywords/${baseName}.json`);
                data = await response.json();
                this.cache.set(cacheKey, data);
            }

            this.elements.keywordsDisplay.textContent = JSON.stringify(data, null, 2);
        } catch (error) {
            this.elements.keywordsDisplay.textContent = 'No keywords data available';
        }
    }

    async loadModelResults(filename, model, displayElement) {
        const baseName = filename.split('.')[0];
        const cacheKey = `${model}_${baseName}`;

        try {
            let data;
            if (this.cache.has(cacheKey)) {
                data = this.cache.get(cacheKey);
            } else {
                const response = await fetch(`data/results/${model}/${baseName}.json`);
                data = await response.json();
                this.cache.set(cacheKey, data);
            }

            displayElement.textContent = JSON.stringify(data, null, 2);
        } catch (error) {
            displayElement.textContent = 'No analysis data available';
        }
    }

    navigate(direction) {
        if (direction === 'prev' && this.currentIndex > 0) {
            this.currentIndex--;
        } else if (direction === 'next' && this.currentIndex < this.files.length - 1) {
            this.currentIndex++;
        }

        this.elements.fileSelect.selectedIndex = this.currentIndex;
        this.loadContent();
    }

    showError(message) {
        // You can implement a more sophisticated error display system here
        alert(message);
    }
}

// Initialize the viewer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const viewer = new ModelViewer();
    viewer.initialize();
});