// Folder Vision - Enhanced JavaScript Application
// Modern, feature-rich multimodal search interface

class FolderVisionApp {
    constructor() {
        this.currentResults = [];
        this.currentProjection = null;
        this.viewMode = 'grid';
        this.isConnected = true;
        this.settings = {
            autoCluster: false,
            showFilePaths: true,
            defaultResults: 25,
            theme: 'dark'
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSettings();
        this.checkConnection();
        this.loadInitialData();
        this.setupKeyboardShortcuts();
        this.setupTooltips();
    }

    setupEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        themeToggle.addEventListener('change', () => {
            const theme = themeToggle.checked ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', theme);
            this.settings.theme = theme;
            this.saveSettings();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'k':
                        e.preventDefault();
                        document.getElementById('textQuery').focus();
                        break;
                    case 'u':
                        e.preventDefault();
                        document.getElementById('queryImage').click();
                        break;
                    case 'Enter':
                        if (document.getElementById('textQuery').value) {
                            this.searchByText();
                        }
                        break;
                }
            }
            
            if (e.key === 'Escape') {
                this.closeImageViewer();
            }
        });

        // Auto-save search queries
        const textQuery = document.getElementById('textQuery');
        textQuery.addEventListener('input', debounce(() => {
            localStorage.setItem('lastTextQuery', textQuery.value);
        }, 500));
    }

    setupKeyboardShortcuts() {
        // Display keyboard shortcuts help
        const shortcuts = [
            { key: 'Ctrl+K', action: 'Focus text search' },
            { key: 'Ctrl+U', action: 'Upload image' },
            { key: 'Escape', action: 'Close image viewer' },
            { key: 'Ctrl+Enter', action: 'Quick search' }
        ];
        
        console.log('Keyboard shortcuts:', shortcuts);
    }

    setupTooltips() {
        // Add tooltips to buttons without text
        const tooltips = {
            'toggleViewMode': 'Toggle view mode',
            'downloadResults': 'Download results',
            'resetProjectionView': 'Reset view',
            'exportProjection': 'Export visualization',
            'getClusterSuggestions': 'Get suggestions'
        };

        Object.entries(tooltips).forEach(([id, text]) => {
            const element = document.querySelector(`[onclick="${id}()"]`);
            if (element) {
                element.title = text;
                element.setAttribute('aria-label', text);
            }
        });
    }

    async checkConnection() {
        try {
            const response = await fetch('/health');
            const health = await response.json();
            
            this.updateConnectionStatus(true);
            this.isConnected = true;
            
            if (health.search_engine_ready) {
                this.showToast('Search engine ready', 'success');
            }
        } catch (error) {
            this.updateConnectionStatus(false);
            this.isConnected = false;
            this.showToast('Connection failed', 'error');
        }
    }

    updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('connectionStatus');
        const statusText = document.getElementById('statusText');
        
        if (connected) {
            statusIndicator.className = 'status-indicator status-online';
            statusText.textContent = 'Connected';
        } else {
            statusIndicator.className = 'status-indicator status-offline';
            statusText.textContent = 'Disconnected';
        }
    }

    async loadInitialData() {
        await this.fetchStats();
        
        // Restore last search query
        const lastQuery = localStorage.getItem('lastTextQuery');
        if (lastQuery) {
            document.getElementById('textQuery').value = lastQuery;
        }
    }

    // Enhanced indexing with progress tracking
    async indexFolder() {
        const folderPath = document.getElementById('folderPath').value;
        const statusDiv = document.getElementById('indexStatus');
        const progressDiv = document.getElementById('indexProgress');
        
        if (!folderPath.trim()) {
            this.showToast('Please enter a folder path', 'warning');
            document.getElementById('folderPath').focus();
            return;
        }

        // Show progress
        progressDiv.classList.remove('hidden');
        statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Starting indexing...';
        
        try {
            const response = await fetch('/index', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ folder_path: folderPath })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                const { successfully_indexed, total_files_found, failed_to_load } = result;
                
                statusDiv.innerHTML = `
                    <div class="text-success">
                        <i class="fas fa-check-circle mr-2"></i>
                        Indexed ${successfully_indexed}/${total_files_found} images
                        ${failed_to_load > 0 ? `<span class="text-warning">(${failed_to_load} failed)</span>` : ''}
                    </div>
                `;
                
                this.showToast(`Successfully indexed ${successfully_indexed} images`, 'success');
                await this.fetchStats();
                
                // Auto-cluster if enabled
                if (this.settings.autoCluster && successfully_indexed > 10) {
                    setTimeout(() => this.performClustering(), 1000);
                }
                
                // Auto-load projection for visualization
                if (successfully_indexed > 5) {
                    setTimeout(() => this.loadProjection(), 2000);
                }
                
            } else {
                statusDiv.innerHTML = `
                    <div class="text-error">
                        <i class="fas fa-exclamation-triangle mr-2"></i>
                        Error: ${result.detail}
                    </div>
                `;
                this.showToast('Indexing failed', 'error');
            }
        } catch (error) {
            statusDiv.innerHTML = `
                <div class="text-error">
                    <i class="fas fa-exclamation-triangle mr-2"></i>
                    Network error: ${error.message}
                </div>
            `;
            this.showToast('Network error occurred', 'error');
        } finally {
            progressDiv.classList.add('hidden');
        }
    }

    async clearIndex() {
        if (!confirm('Are you sure you want to clear the index?')) return;
        
        try {
            const response = await fetch('/index/clear', { method: 'POST' });
            const result = await response.json();
            
            document.getElementById('indexStatus').innerHTML = `
                <div class="text-warning">
                    <i class="fas fa-trash mr-2"></i>
                    Cleared ${result.cleared_images} images
                </div>
            `;
            
            this.clearResults();
            this.clearProjection();
            await this.fetchStats();
            
            this.showToast('Index cleared', 'info');
        } catch (error) {
            this.showToast('Failed to clear index', 'error');
        }
    }

    async loadCache() {
        try {
            const response = await fetch('/stats');
            if (response.ok) {
                const stats = await response.json();
                this.updateQuickStats(stats);
                this.showToast('Cache loaded successfully', 'success');
            } else {
                this.showToast('No cache available', 'warning');
            }
        } catch (error) {
            this.showToast('Failed to load cache', 'error');
        }
    }

    // Enhanced text search with suggestions
    async searchByText() {
        const query = document.getElementById('textQuery').value.trim();
        const topK = parseInt(document.getElementById('textTopK').value);
        
        if (!query) {
            this.showToast('Please enter a search query', 'warning');
            document.getElementById('textQuery').focus();
            return;
        }

        this.showSearchProgress('Searching for: ' + query);
        
        try {
            const response = await fetch(`/search/text?query=${encodeURIComponent(query)}&top_k=${topK}`);
            const results = await response.json();
            
            if (response.ok) {
                this.currentResults = results;
                this.displayResults(results, `Text Search: "${query}"`);
                this.updateResultCount(results.length);
                
                // Save to search history
                this.saveSearchHistory('text', query, results.length);
                
                if (results.length === 0) {
                    this.showToast('No results found. Try a different query.', 'info');
                } else {
                    this.showToast(`Found ${results.length} results`, 'success');
                }
            } else {
                this.showToast('Search failed: ' + results.detail, 'error');
            }
        } catch (error) {
            this.showToast('Search error: ' + error.message, 'error');
        }
    }

    // Enhanced image search with preview
    async searchByImage() {
        const fileInput = document.getElementById('queryImage');
        const topK = parseInt(document.getElementById('imageTopK').value);
        
        if (!fileInput.files[0]) {
            this.showToast('Please select an image file', 'warning');
            fileInput.click();
            return;
        }

        this.showSearchProgress('Analyzing image...');
        
        const formData = new FormData();
        formData.append('image', fileInput.files[0]);
        formData.append('top_k', topK);
        
        try {
            const response = await fetch('/search/image', {
                method: 'POST',
                body: formData
            });
            
            const results = await response.json();
            
            if (response.ok) {
                this.currentResults = results;
                this.displayResults(results, 'Image Search Results');
                this.updateResultCount(results.length);
                
                this.saveSearchHistory('image', fileInput.files[0].name, results.length);
                
                if (results.length === 0) {
                    this.showToast('No similar images found', 'info');
                } else {
                    this.showToast(`Found ${results.length} similar images`, 'success');
                }
            } else {
                this.showToast('Image search failed: ' + results.detail, 'error');
            }
        } catch (error) {
            this.showToast('Image search error: ' + error.message, 'error');
        }
    }

    // Enhanced clustering with better feedback
    async performClustering() {
        const method = document.getElementById('clusterMethod').value;
        const numClusters = document.getElementById('numClusters').value;
        const clusterDiv = document.getElementById('clusterResult');
        
        clusterDiv.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Clustering images...';
        
        const requestData = { method };
        if (numClusters && method === 'kmeans') {
            requestData.n_clusters = parseInt(numClusters);
        }
        
        try {
            const response = await fetch('/cluster', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                const { method: usedMethod, n_clusters, statistics } = result;
                
                clusterDiv.innerHTML = `
                    <div class="text-success">
                        <i class="fas fa-check-circle mr-2"></i>
                        ${usedMethod.toUpperCase()}: ${n_clusters} clusters
                        <br><small>Avg size: ${statistics.avg_cluster_size.toFixed(1)}</small>
                    </div>
                `;
                
                document.getElementById('clustersCount').textContent = n_clusters;
                
                this.renderClusterList(result);
                this.showToast(`Created ${n_clusters} clusters`, 'success');
                
                // Auto-load projection to show clusters
                setTimeout(() => this.loadProjection(), 500);
                
            } else {
                clusterDiv.innerHTML = `
                    <div class="text-error">
                        <i class="fas fa-exclamation-triangle mr-2"></i>
                        ${result.detail}
                    </div>
                `;
                this.showToast('Clustering failed', 'error');
            }
        } catch (error) {
            clusterDiv.innerHTML = `
                <div class="text-error">
                    <i class="fas fa-exclamation-triangle mr-2"></i>
                    Error: ${error.message}
                </div>
            `;
            this.showToast('Clustering error', 'error');
        }
    }

    async getClusterSuggestions() {
        const clusterDiv = document.getElementById('clusterResult');
        
        clusterDiv.innerHTML = '<i class="fas fa-lightbulb fa-pulse mr-2"></i>Getting suggestions...';
        
        try {
            const response = await fetch('/cluster/suggestions');
            const suggestions = await response.json();
            
            if (response.ok) {
                if (suggestions.length === 0) {
                    clusterDiv.innerHTML = '<span class="text-warning">Need more images for suggestions</span>';
                    return;
                }
                
                let html = '<div class="text-info"><i class="fas fa-lightbulb mr-2"></i>Suggestions:</div>';
                suggestions.forEach((suggestion, i) => {
                    html += `<span class="badge badge-outline mr-1 mb-1">${suggestion.size} images</span>`;
                });
                clusterDiv.innerHTML = html;
                
                this.showToast('Cluster suggestions ready', 'info');
            } else {
                clusterDiv.innerHTML = `<span class="text-error">Error: ${suggestions.detail}</span>`;
            }
        } catch (error) {
            clusterDiv.innerHTML = `<span class="text-error">Error: ${error.message}</span>`;
        }
    }

    // Enhanced visualization with click handling
    async loadProjection() {
        const method = document.getElementById('projMethod').value;
        const dim = document.getElementById('projDim').value;
        const container = document.getElementById('projection');
        
        container.innerHTML = '<div class="flex items-center justify-center h-full"><i class="fas fa-spinner fa-spin mr-2"></i>Generating visualization...</div>';
        
        try {
            const response = await fetch(`/project?method=${method}&dim=${dim}`);
            const data = await response.json();
            
            if (response.ok) {
                this.currentProjection = data;
                this.plotProjection(data);
                this.showToast(`${method.toUpperCase()} projection ready`, 'success');
            } else {
                container.innerHTML = '<div class="flex items-center justify-center h-full text-error">Projection failed</div>';
                this.showToast('Visualization failed', 'error');
            }
        } catch (error) {
            container.innerHTML = '<div class="flex items-center justify-center h-full text-error">Network error</div>';
            this.showToast('Visualization error', 'error');
        }
    }

    plotProjection(data) {
        const { dim, points } = data;
        
        if (!points || points.length === 0) {
            document.getElementById('projection').innerHTML = 
                '<div class="flex items-center justify-center h-full text-gray-500">No data to visualize</div>';
            return;
        }

        // Group points by cluster
        const clusters = {};
        points.forEach(point => {
            const cluster = point.cluster ?? 'Unclustered';
            if (!clusters[cluster]) {
                clusters[cluster] = { x: [], y: [], z: [], text: [], customdata: [] };
            }
            clusters[cluster].x.push(point.x);
            clusters[cluster].y.push(point.y);
            if (dim === 3) clusters[cluster].z.push(point.z);
            clusters[cluster].text.push(point.filename);
            clusters[cluster].customdata.push(point.path);
        });

        // Create traces for each cluster
        const traces = Object.entries(clusters).map(([clusterName, clusterData]) => {
            const trace = {
                type: dim === 3 ? 'scatter3d' : 'scatter',
                mode: 'markers',
                name: clusterName,
                x: clusterData.x,
                y: clusterData.y,
                text: clusterData.text,
                customdata: clusterData.customdata,
                hovertemplate: '<b>%{text}</b><br>Cluster: ' + clusterName + '<extra></extra>',
                marker: {
                    size: dim === 3 ? 4 : 6,
                    opacity: 0.8,
                    line: { width: 1, color: 'white' }
                }
            };
            
            if (dim === 3) {
                trace.z = clusterData.z;
            }
            
            return trace;
        });

        const layout = {
            margin: { l: 0, r: 0, t: 20, b: 0 },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: 'white' },
            showlegend: Object.keys(clusters).length > 1,
            legend: { 
                orientation: 'h',
                x: 0.5,
                xanchor: 'center',
                y: -0.1
            }
        };

        if (dim === 3) {
            layout.scene = {
                aspectmode: 'cube',
                bgcolor: 'rgba(0,0,0,0)',
                xaxis: { backgroundcolor: 'rgba(0,0,0,0)', gridcolor: 'rgba(255,255,255,0.1)' },
                yaxis: { backgroundcolor: 'rgba(0,0,0,0)', gridcolor: 'rgba(255,255,255,0.1)' },
                zaxis: { backgroundcolor: 'rgba(0,0,0,0)', gridcolor: 'rgba(255,255,255,0.1)' }
            };
        } else {
            layout.xaxis = { 
                backgroundcolor: 'rgba(0,0,0,0)', 
                gridcolor: 'rgba(255,255,255,0.1)',
                zerolinecolor: 'rgba(255,255,255,0.1)'
            };
            layout.yaxis = { 
                backgroundcolor: 'rgba(0,0,0,0)', 
                gridcolor: 'rgba(255,255,255,0.1)',
                zerolinecolor: 'rgba(255,255,255,0.1)'
            };
        }

        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            displaylogo: false
        };

        Plotly.newPlot('projection', traces, layout, config);

        // Add click handler for points
        const plotDiv = document.getElementById('projection');
        plotDiv.on('plotly_click', (data) => {
            if (data.points && data.points.length > 0) {
                const point = data.points[0];
                const imagePath = point.customdata;
                const filename = point.text;
                
                if (imagePath) {
                    this.openImageViewer(imagePath, filename);
                }
            }
        });
        
        // Add hover handler for better UX
        plotDiv.on('plotly_hover', (data) => {
            plotDiv.style.cursor = 'pointer';
        });
        
        plotDiv.on('plotly_unhover', (data) => {
            plotDiv.style.cursor = 'default';
        });
    }

    // Enhanced result display with hover effects
    displayResults(results, title) {
        const resultsDiv = document.getElementById('results');
        
        if (!results || results.length === 0) {
            resultsDiv.innerHTML = `
                <div class="col-span-full flex items-center justify-center h-64 text-gray-500">
                    <div class="text-center">
                        <i class="fas fa-search text-4xl mb-4 opacity-30"></i>
                        <p>No results found</p>
                        <p class="text-sm">Try adjusting your search terms</p>
                    </div>
                </div>
            `;
            return;
        }

        let html = '';
        results.forEach((result, index) => {
            const score = result.score ? (result.score * 100).toFixed(1) : '';
            const filename = result.filename || result.path.split('/').pop();
            
            html += `
                <div class="image-card bg-base-100 shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer"
                     onclick="app.openImageViewer('${result.path}', '${filename}', '${score}')"
                     data-index="${index}">
                    <figure class="aspect-square overflow-hidden">
                        <img src="/image/${encodeURIComponent(result.path)}" 
                             alt="${filename}"
                             class="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
                             loading="lazy"
                             style="filter: none !important; backdrop-filter: none !important;" />
                    </figure>
                    <div class="p-3">
                        <div class="font-medium text-sm truncate" title="${filename}">
                            ${filename}
                        </div>
                        ${score ? `
                            <div class="flex items-center justify-between mt-2">
                                <span class="text-xs opacity-70">Similarity</span>
                                <span class="badge badge-primary badge-sm">${score}%</span>
                            </div>
                        ` : ''}
                        ${this.settings.showFilePaths ? `
                            <div class="text-xs opacity-50 truncate mt-1" title="${result.path}">
                                ${result.path}
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        });
        
        resultsDiv.innerHTML = html;
        
        // Add intersection observer for lazy loading
        this.setupLazyLoading();
    }

    setupLazyLoading() {
        const images = document.querySelectorAll('img[loading="lazy"]');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.src; // Trigger loading
                    observer.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }

    // Enhanced image viewer with navigation
    openImageViewer(imagePath, filename, score = '') {
        const viewer = document.getElementById('imageViewer');
        const img = document.getElementById('imageViewerImg');
        const info = document.getElementById('imageViewerInfo');
        
        img.src = `/image/${encodeURIComponent(imagePath)}`;
        img.alt = filename;
        
        let infoText = filename;
        if (score) infoText += ` • ${score}% similarity`;
        info.textContent = infoText;
        
        viewer.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        // Store current image info for other actions
        this.currentViewerImage = { path: imagePath, filename, score };
    }

    closeImageViewer() {
        const viewer = document.getElementById('imageViewer');
        viewer.style.display = 'none';
        document.body.style.overflow = 'auto';
        this.currentViewerImage = null;
    }

    // Enhanced cluster list rendering
    renderClusterList(data) {
        const list = document.getElementById('clusterList');
        
        if (!data.clusters) {
            list.innerHTML = '<div class="text-gray-500 text-center py-2">No clusters available</div>';
            return;
        }

        let html = '';
        Object.entries(data.clusters).forEach(([name, cluster]) => {
            const displayName = name.replace('cluster_', 'C');
            html += `
                <div class="flex items-center justify-between p-2 hover:bg-base-200 rounded cursor-pointer transition-colors"
                     onclick="app.showClusterImages('${name}')">
                    <div class="flex items-center space-x-2">
                        <div class="w-3 h-3 rounded-full bg-primary"></div>
                        <span class="font-mono text-sm">${displayName}</span>
                        <span class="badge badge-ghost badge-sm">${cluster.size}</span>
                    </div>
                    <i class="fas fa-chevron-right text-xs opacity-50"></i>
                </div>
            `;
        });
        
        list.innerHTML = html;
    }

    async showClusterImages(clusterName) {
        try {
            const clusterId = clusterName.replace('cluster_', '');
            const response = await fetch(`/cluster/${clusterId}/images`);
            const data = await response.json();
            
            if (response.ok) {
                const images = data.images.slice(0, 50).map(path => ({
                    path,
                    filename: path.split('/').pop(),
                    score: null
                }));
                
                this.currentResults = images;
                this.displayResults(images, `Cluster ${clusterName}`);
                this.updateResultCount(images.length);
                this.showToast(`Showing ${images.length} images from ${clusterName}`, 'info');
            }
        } catch (error) {
            this.showToast('Failed to load cluster images', 'error');
        }
    }

    // Utility functions
    async fetchStats() {
        try {
            const response = await fetch('/stats');
            if (response.ok) {
                const stats = await response.json();
                this.updateQuickStats(stats);
            }
        } catch (error) {
            console.warn('Failed to fetch stats:', error);
        }
    }

    updateQuickStats(stats) {
        document.getElementById('totalImages').textContent = stats.total_images || 0;
        document.getElementById('embeddingDim').textContent = stats.embedding_dim || 512;
        document.getElementById('deviceInfo').textContent = stats.device || 'CPU';
    }

    updateResultCount(count) {
        document.getElementById('resultCount').textContent = count;
    }

    showSearchProgress(message) {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `
            <div class="col-span-full flex items-center justify-center h-32">
                <div class="text-center">
                    <i class="fas fa-spinner fa-spin text-2xl mb-2"></i>
                    <p>${message}</p>
                </div>
            </div>
        `;
    }

    clearResults() {
        document.getElementById('results').innerHTML = `
            <div class="col-span-full flex items-center justify-center h-64 text-gray-500">
                <div class="text-center">
                    <i class="fas fa-search text-4xl mb-4 opacity-30"></i>
                    <p>Start by indexing a folder and searching...</p>
                </div>
            </div>
        `;
        this.updateResultCount(0);
    }

    clearProjection() {
        document.getElementById('projection').innerHTML = `
            <div class="flex items-center justify-center h-full text-gray-500">
                <div class="text-center">
                    <i class="fas fa-chart-scatter text-4xl mb-4 opacity-30"></i>
                    <p>Click "Visualize" to see embedding projection</p>
                </div>
            </div>
        `;
    }

    // Advanced features
    toggleViewMode() {
        this.viewMode = this.viewMode === 'grid' ? 'list' : 'grid';
        const icon = document.getElementById('viewModeIcon');
        const resultsDiv = document.getElementById('results');
        
        if (this.viewMode === 'list') {
            icon.className = 'fas fa-list';
            resultsDiv.className = 'space-y-2';
        } else {
            icon.className = 'fas fa-th';
            resultsDiv.className = 'grid-auto-fit';
        }
        
        // Re-render current results with new view mode
        if (this.currentResults.length > 0) {
            this.displayResults(this.currentResults, 'Current Results');
        }
    }

    async downloadResults() {
        if (!this.currentResults.length) {
            this.showToast('No results to download', 'warning');
            return;
        }

        const data = {
            timestamp: new Date().toISOString(),
            total_results: this.currentResults.length,
            results: this.currentResults
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `folder-vision-results-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast('Results downloaded', 'success');
    }

    resetProjectionView() {
        if (this.currentProjection) {
            this.plotProjection(this.currentProjection);
            this.showToast('View reset', 'info');
        }
    }

    exportProjection() {
        const plotDiv = document.getElementById('projection');
        Plotly.toImage(plotDiv, { format: 'png', width: 1200, height: 800 })
            .then(dataURL => {
                const a = document.createElement('a');
                a.href = dataURL;
                a.download = `embedding-projection-${Date.now()}.png`;
                a.click();
                this.showToast('Projection exported', 'success');
            })
            .catch(() => {
                this.showToast('Export failed', 'error');
            });
    }

    // Helper functions for UI interactions
    setTextQuery(query) {
        document.getElementById('textQuery').value = query;
        this.searchByText();
    }

    previewQueryImage(input) {
        const preview = document.getElementById('queryImagePreview');
        const img = preview.querySelector('img');
        
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = (e) => {
                img.src = e.target.result;
                preview.classList.remove('hidden');
            };
            reader.readAsDataURL(input.files[0]);
        } else {
            preview.classList.add('hidden');
        }
    }

    selectFolder() {
        // This would require a backend endpoint or electron integration
        this.showToast('Use the input field to enter folder path', 'info');
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }

    showSettings() {
        document.getElementById('settingsModal').showModal();
    }

    showHelp() {
        document.getElementById('helpModal').showModal();
    }

    // Quick actions
    quickIndex() {
        const commonPaths = [
            '/Users/Pictures',
            '/Users/Downloads',
            '/Users/Desktop'
        ];
        
        // For demo purposes, just focus the input
        document.getElementById('folderPath').focus();
        this.showToast('Enter a folder path to index', 'info');
    }

    batchProcess() {
        this.showToast('Batch processing coming soon', 'info');
    }

    exportResults() {
        this.downloadResults();
    }

    exportData() {
        this.showToast('Data export coming soon', 'info');
    }

    downloadCurrentImage() {
        if (this.currentViewerImage) {
            const a = document.createElement('a');
            a.href = `/image/${encodeURIComponent(this.currentViewerImage.path)}`;
            a.download = this.currentViewerImage.filename;
            a.click();
            this.showToast('Download started', 'success');
        }
    }

    shareCurrentImage() {
        if (this.currentViewerImage) {
            const url = window.location.origin + `/image/${encodeURIComponent(this.currentViewerImage.path)}`;
            navigator.clipboard.writeText(url).then(() => {
                this.showToast('Image URL copied to clipboard', 'success');
            }).catch(() => {
                this.showToast('Failed to copy URL', 'error');
            });
        }
    }

    // Settings management
    loadSettings() {
        const saved = localStorage.getItem('folderVisionSettings');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
        }
        
        // Apply theme
        document.documentElement.setAttribute('data-theme', this.settings.theme);
        document.getElementById('themeToggle').checked = this.settings.theme === 'light';
    }

    saveSettings() {
        localStorage.setItem('folderVisionSettings', JSON.stringify(this.settings));
    }

    saveSearchHistory(type, query, resultCount) {
        const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
        history.unshift({
            type,
            query,
            resultCount,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last 50 searches
        if (history.length > 50) {
            history.splice(50);
        }
        
        localStorage.setItem('searchHistory', JSON.stringify(history));
    }

    // Toast notification system
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        const colors = {
            success: 'alert-success',
            error: 'alert-error',
            warning: 'alert-warning',
            info: 'alert-info'
        };
        
        toast.className = `alert ${colors[type]} shadow-lg mb-2 transform translate-x-full transition-transform duration-300`;
        toast.innerHTML = `
            <div class="flex items-center">
                <i class="${icons[type]} mr-2"></i>
                <span>${message}</span>
            </div>
            <button class="btn btn-ghost btn-sm" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.add('translate-x-full');
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize the application
const app = new FolderVisionApp();

// Global functions for onclick handlers (for backward compatibility)
window.indexFolder = () => app.indexFolder();
window.clearIndex = () => app.clearIndex();
window.loadCache = () => app.loadCache();
window.searchByText = () => app.searchByText();
window.searchByImage = () => app.searchByImage();
window.performClustering = () => app.performClustering();
window.getClusterSuggestions = () => app.getClusterSuggestions();
window.loadProjection = () => app.loadProjection();
window.toggleViewMode = () => app.toggleViewMode();
window.downloadResults = () => app.downloadResults();
window.resetProjectionView = () => app.resetProjectionView();
window.exportProjection = () => app.exportProjection();
window.setTextQuery = (query) => app.setTextQuery(query);
window.previewQueryImage = (input) => app.previewQueryImage(input);
window.selectFolder = () => app.selectFolder();
window.toggleFullscreen = () => app.toggleFullscreen();
window.showSettings = () => app.showSettings();
window.showHelp = () => app.showHelp();
window.quickIndex = () => app.quickIndex();
window.batchProcess = () => app.batchProcess();
window.exportResults = () => app.exportResults();
window.exportData = () => app.exportData();
window.downloadCurrentImage = () => app.downloadCurrentImage();
window.shareCurrentImage = () => app.shareCurrentImage();
window.closeImageViewer = () => app.closeImageViewer();
