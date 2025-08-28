/**
 * AdminAjax handles dynamic form updates in the Django admin.
 * This version uses modern vanilla JavaScript (ES6+) and the Fetch API,
 * removing the dependency on jQuery.
 */
// This class contains the core logic. It's prefixed with an underscore
// to indicate it's the internal implementation.
class _AdminAjax {
    /**
     * @param {string} url The URL to send the AJAX request to.
     * @param {string} form_id The ID of the form to serialize.
     * @param {string[]} change_field_ids An array of field IDs that trigger the AJAX call on change.
     */
    constructor(url, form_id, change_field_ids) {
        this.url = url;
        this.form_id = form_id;
        this.change_field_ids = change_field_ids;

        // Ensure initialization runs after the DOM is fully loaded.
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    /**
     * Initializes the event listeners.
     */
    init() {
        this.setEvents(this.change_field_ids);
    }

    /**
     * Attaches change event listeners to the specified form fields.
     * @param {string[]} fields An array of field IDs.
     */
    setEvents(fields) {
        fields.forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                element.addEventListener('change', () => this.getForm());
            } else {
                console.warn(`AdminAjax: Element with ID #${fieldId} not found.`);
            }
        });
    }

    /**
     * Fetches the updated form content from the server and replaces it on the page.
     */
    async getForm() {
        if (!this.url) {
            const errMsg = "Make Sure AdminAjax is instantiated properly!";
            alert(errMsg);
            throw new Error(errMsg);
        }

        const form = document.getElementById(this.form_id);
        if (!form) {
            console.error(`AdminAjax: Form with ID #${this.form_id} not found.`);
            return;
        }

        // Serialize form data into a query string.
        const formData = new FormData(form);
        const params = new URLSearchParams(formData);
        params.append('_', new Date().getTime()); // Prevent browser caching (replicates jQuery's cache:false)

        const fullUrl = `${this.url}?${params.toString()}`;

        try {
            const response = await fetch(fullUrl, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' } // Standard header for AJAX requests
            });

            if (!response.ok) {
                throw new Error(`Network response was not ok, status: ${response.status}`);
            }

            const reply = await response.text();

            // Replace content on the page.
            document.querySelectorAll('.module').forEach(el => el.remove());
            const ajaxContent = document.getElementById('ajax_content');
            if (ajaxContent) {
                ajaxContent.innerHTML = reply;

                // Find and execute any script tags within the new content,
                // as `innerHTML` does not execute them by default for security reasons.
                // Using eval() is a direct way to ensure the script runs, mimicking
                // the more aggressive script execution behavior of jQuery's .html().
                ajaxContent.querySelectorAll('script').forEach(oldScript => {
                    eval(oldScript.textContent);
                });
            } else {
                console.warn('AdminAjax: Element with ID #ajax_content not found to inject HTML.');
            }
        } catch (error) {
            console.error("AdminAjax: There was a problem with the fetch operation:", error);
            alert("Check server logs... ajax error!");
        }
    }
}

/**
 * For backward compatibility with templates that may call AdminAjax(...) without `new`.
 * This factory function ensures the class is instantiated correctly.
 */
var AdminAjax = function(url, form_id, change_field_ids) {
    return new _AdminAjax(url, form_id, change_field_ids);
};
