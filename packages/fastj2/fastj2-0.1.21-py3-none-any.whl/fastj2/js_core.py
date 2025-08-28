search_handler = """/**
 * Creates a debounced search handler for input elements
 * @param {Object} options - Configuration options
 * @param {string} options.inputSelector - CSS selector for the input element
 * @param {string} options.searchEndpoint - Base URL endpoint for search requests
 * @param {string} options.targetSelector - CSS selector for results container
 * @param {string} [options.loadingSelector] - CSS selector for loading indicator
 * @param {string} [options.defaultEndpoint] - Endpoint to call when search is cleared
 * @param {number} [options.minLength=2] - Minimum query length to trigger search
 * @param {number} [options.debounceDelay=500] - Delay in ms before making request
 * @param {Function} [options.onSearch] - Custom search handler function
 * @param {Function} [options.onClear] - Custom clear handler function
 * @param {Object} [options.requestOptions] - Additional request options
 */
function createSearchHandler(options) {
    const {
        inputSelector,
        searchEndpoint,
        targetSelector,
        loadingSelector = null,
        defaultEndpoint = null,
        minLength = 2,
        debounceDelay = 500,
        onSearch = null,
        onClear = null,
        requestOptions = {}
    } = options;

    let searchTimeout;
    const inputElement = document.querySelector(inputSelector);

    if (!inputElement) {
        console.error(`Input element not found: ${inputSelector}`);
        return null;
    }

    // Default search handler using htmx
    const defaultSearchHandler = (query) => {
        const searchUrl = `${searchEndpoint}/${encodeURIComponent(query)}`;
        console.log('Making request to:', searchUrl);

        const htmxOptions = {
            target: targetSelector,
            ...requestOptions
        };

        if (loadingSelector) {
            htmxOptions.indicator = loadingSelector;
        }

        htmx.ajax('GET', searchUrl, htmxOptions);
    };

    // Default clear handler
    const defaultClearHandler = () => {
        if (defaultEndpoint) {
            const htmxOptions = {
                target: targetSelector,
                ...requestOptions
            };

            if (loadingSelector) {
                htmxOptions.indicator = loadingSelector;
            }

            htmx.ajax('GET', defaultEndpoint, htmxOptions);
        }
    };

    // Event listener
    const handleInput = (e) => {
        const query = e.target.value.trim();
        console.log('Search input:', query, 'length:', query.length);

        // Clear existing timeout
        clearTimeout(searchTimeout);

        // Set new timeout
        searchTimeout = setTimeout(() => {
            if (query.length >= minLength) {
                // Use custom handler or default
                if (onSearch) {
                    onSearch(query);
                } else {
                    defaultSearchHandler(query);
                }
            } else if (query.length === 0) {
                // Use custom clear handler or default
                if (onClear) {
                    onClear();
                } else {
                    defaultClearHandler();
                }
            }
        }, debounceDelay);
    };

    inputElement.addEventListener('input', handleInput);

    // Return cleanup function
    return () => {
        inputElement.removeEventListener('input', handleInput);
        clearTimeout(searchTimeout);
    };
}

//// Usage Examples:
//
//// 1. Basic usage (similar to your original code)
//const leadsSearch = createSearchHandler({
//    inputSelector: '#search-input',
//    searchEndpoint: '/leads/search',
//    targetSelector: '#results',
//    loadingSelector: '#loading',
//    defaultEndpoint: '/leads/recent'
//});
//
//// 2. Custom search handlers
//const customSearch = createSearchHandler({
//    inputSelector: '#product-search',
//    searchEndpoint: '/api/products/search',
//    targetSelector: '#product-results',
//    minLength: 3,
//    debounceDelay: 300,
//    onSearch: (query) => {
//        // Custom search logic
//        fetch(`/api/products/search?q=${encodeURIComponent(query)}`)
//            .then(response => response.json())
//            .then(data => {
//                document.querySelector('#product-results').innerHTML =
//                    data.map(product => `<div>${product.name}</div>`).join('');
//            });
//    },
//    onClear: () => {
//        document.querySelector('#product-results').innerHTML = '';
//    }
//});
//
//// 3. Using with fetch instead of htmx
//const fetchSearch = createSearchHandler({
//    inputSelector: '#user-search',
//    searchEndpoint: '/api/users/search',
//    targetSelector: '#user-results',
//    onSearch: async (query) => {
//        try {
//            const response = await fetch(`/api/users/search?q=${encodeURIComponent(query)}`);
//            const users = await response.json();
//
//            const resultsContainer = document.querySelector('#user-results');
//            resultsContainer.innerHTML = users.map(user =>
//                `<div class="user-item">${user.name} - ${user.email}</div>`
//            ).join('');
//        } catch (error) {
//            console.error('Search error:', error);
//        }
//    }
//});
//
//// 4. Multiple search instances
//const searches = [
//    createSearchHandler({
//        inputSelector: '#header-search',
//        searchEndpoint: '/search/global',
//        targetSelector: '#global-results'
//    }),
//    createSearchHandler({
//        inputSelector: '#sidebar-search',
//        searchEndpoint: '/search/sidebar',
//        targetSelector: '#sidebar-results',
//        minLength: 1,
//        debounceDelay: 200
//    })
//];
//
//// Cleanup all searches when needed
//// searches.forEach(cleanup => cleanup && cleanup());
"""